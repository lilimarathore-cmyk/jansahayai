# backend/services/response_builder.py
# PROFESSIONAL VERSION - No emojis, No stars, Only bold headings

from typing import Dict, Any, Optional, List
import json


def extract_field(data: Dict, path: str) -> Optional[Any]:
    keys = path.split(".")
    val = data
    
    for key in keys:
        if val is None:
            return None
        if isinstance(val, list):
            return val
        if not isinstance(val, dict):
            return None
        val = val.get(key)
    
    return val


def extract_localized_text(value: Any, lang: str = "hi") -> str:
    if value is None:
        return ""
    
    if isinstance(value, str):
        return value.strip()
    
    if isinstance(value, (int, float)):
        return str(value)
    
    if isinstance(value, list):
        lines = []
        for item in value:
            text = extract_localized_text(item, lang)
            if text:
                lines.append(f"- {text}")
        return "\n".join(lines)
    
    if isinstance(value, dict):
        if lang in value and value[lang]:
            return value[lang].strip()
        
        for key in ["text", "answer", "rules", "steps", "description", "hi"]:
            if key in value:
                text = extract_localized_text(value[key], lang)
                if text:
                    return text
        
        parts = []
        for k, v in value.items():
            if k not in ["_id", "id", "scheme_id"]:
                text = extract_localized_text(v, lang)
                if text:
                    parts.append(text)
        
        if parts:
            return "\n".join(parts)
    
    return ""


def format_eligibility_rules(eligibility_data: Any) -> str:
    if eligibility_data is None:
        return ""
    
    rules = []
    
    if isinstance(eligibility_data, list):
        for rule in eligibility_data:
            if isinstance(rule, dict):
                text = extract_localized_text(rule.get("text"))
                if text:
                    rules.append(f"- {text}")
            elif isinstance(rule, str):
                rules.append(f"- {rule}")
    elif isinstance(eligibility_data, dict):
        text = extract_localized_text(eligibility_data)
        if text:
            rules.append(f"- {text}")
    else:
        text = extract_localized_text(eligibility_data)
        if text:
            rules.append(f"- {text}")
    
    return "\n".join(rules)


def format_documents_list(docs_data: Any) -> str:
    if docs_data is None:
        return ""
    
    docs = []
    
    if isinstance(docs_data, list):
        for doc in docs_data:
            text = extract_localized_text(doc)
            if text:
                docs.append(f"- {text}")
    else:
        text = extract_localized_text(docs_data)
        if text:
            docs.append(f"- {text}")
    
    return "\n".join(docs)


def format_application_steps(steps_data: Any) -> str:
    if steps_data is None:
        return ""
    
    steps = []
    
    if isinstance(steps_data, list):
        for i, step in enumerate(steps_data, 1):
            text = extract_localized_text(step)
            if text:
                steps.append(f"{i}. {text}")
    else:
        text = extract_localized_text(steps_data)
        if text:
            steps.append(f"- {text}")
    
    return "\n".join(steps)


def format_locations_list(locations_data: Any) -> str:
    if locations_data is None:
        return ""
    
    locs = []
    
    if isinstance(locations_data, list):
        for loc in locations_data:
            text = extract_localized_text(loc)
            if text:
                locs.append(f"- {text}")
    else:
        text = extract_localized_text(locations_data)
        if text:
            locs.append(f"- {text}")
    
    return "\n".join(locs)


def format_zone_location_block(zone_details: Dict, zone_response: str = None) -> str:
    if zone_response:
        return f"\nकहाँ आवेदन करें\n{zone_response}"
    return "\nकहाँ आवेदन करें\n- ग्राम पंचायत\n- जनपद पंचायत\n- नगर निगम / नगर पालिका"


def build_response(scheme: Dict, intent: str) -> str:
    nlp = scheme.get("nlp", {})
    intents = nlp.get("intents", [])
    
    response_path = "content.short_answer"
    
    for intent_config in intents:
        if intent_config.get("name") == intent:
            response_path = intent_config.get("response", "content.short_answer")
            break
    
    data = extract_field(scheme, response_path)
    
    if data is None:
        fallback_paths = ["content.short_answer", "content.objective", "scheme_name"]
        for fallback in fallback_paths:
            fallback_data = extract_field(scheme, fallback)
            if fallback_data:
                data = fallback_data
                break
    
    response = extract_localized_text(data, "hi")
    
    if response:
        return response
    
    scheme_name = extract_localized_text(scheme.get("scheme_name"), "hi")
    if scheme_name:
        return f"{scheme_name} के बारे में विस्तृत जानकारी उपलब्ध नहीं है।"
    
    return "जानकारी उपलब्ध नहीं है।"


def format_scheme_full_details(scheme: Dict, zone_response: str = None, show_pdf: bool = True) -> str:
    """
    Professional format - No emojis, No stars, Only bold headings
    
    Args:
        scheme: Scheme dictionary
        zone_response: Zone details (optional)
        show_pdf: Whether to show PDF download link
    """
    scheme_name = extract_localized_text(scheme.get("scheme_name"), "hi")
    if not scheme_name:
        scheme_name = "योजना"
    
    content = scheme.get("content", {})
    
    benefits = ""
    benefits_data = content.get("benefits", {})
    if benefits_data:
        benefits = extract_localized_text(benefits_data.get("text")) or extract_localized_text(benefits_data)
    
    eligibility = ""
    eligibility_data = content.get("eligibility", {}).get("rules")
    if eligibility_data:
        eligibility = format_eligibility_rules(eligibility_data)
    else:
        eligibility = extract_localized_text(content.get("eligibility"))
    
    documents = format_documents_list(content.get("documents"))
    steps = format_application_steps(content.get("application", {}).get("steps"))
    locations = format_locations_list(content.get("application", {}).get("locations"))
    
    response = f"**{scheme_name}**\n\n"
    
    if benefits:
        response += f"**क्या मिलता है**\n\n{benefits}\n\n"
    
    if eligibility:
        response += f"**कौन ले सकता है**\n\n{eligibility}\n\n"
    
    if documents:
        response += f"**आवश्यक दस्तावेज**\n\n{documents}\n\n"
    
    if steps:
        response += f"**आवेदन कैसे करें**\n\n{steps}\n\n"
    
    if zone_response:
        response += f"**कहाँ आवेदन करें**\n\n{zone_response}\n\n"
    elif locations:
        response += f"**कहाँ आवेदन करें**\n\n{locations}\n\n"
    
    # PDF Link - ONLY if show_pdf is True
    if show_pdf:
        pdf_link = scheme.get("pdf_link", "")
        if pdf_link:
            response += f"**डाउनलोड फॉर्म**\n\n{pdf_link}\n\n"
    
    if not response.strip() or response == f"**{scheme_name}**\n\n":
        short_answer = extract_localized_text(content.get("short_answer"))
        if short_answer:
            response = f"**{scheme_name}**\n\n{short_answer}\n\n"
        else:
            response = f"**{scheme_name}**\n\nजानकारी उपलब्ध नहीं है।\n\n"
    
    return response


def format_scheme_brief(scheme: Dict) -> str:
    scheme_name = extract_localized_text(scheme.get("scheme_name"), "hi")
    short_answer = extract_localized_text(scheme.get("content", {}).get("short_answer"))
    
    if short_answer:
        short_text = short_answer[:100] + "..." if len(short_answer) > 100 else short_answer
        return f"**{scheme_name}** - {short_text}"
    else:
        return f"**{scheme_name}**"


def format_schemes_list(schemes: List[Dict], title: str = "उपलब्ध योजनाएं") -> str:
    if not schemes:
        return "कोई योजना उपलब्ध नहीं है।"
    
    response = f"**{title}**\n\n"
    for i, scheme in enumerate(schemes, 1):
        brief = format_scheme_brief(scheme)
        response += f"{i}. {brief}\n\n"
    
    response += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    response += "कृपया कोई **नंबर** बताएं - उस योजना की पूरी जानकारी मिलेगी।\n"
    response += "जैसे: 1, 2, या 3"
    
    return response


# ========== LLM PROMPT BUILDING ==========

def build_llm_context(
    intent: str, 
    scheme: Dict, 
    user_query: str, 
    confidence: float = 0.5,
    conversation_history: List[Dict] = None
) -> Dict:
    scheme_name = extract_localized_text(scheme.get("scheme_name"), "hi")
    content = scheme.get("content", {})
    
    relevant_data = {}
    
    if intent == "ask_documents":
        docs = content.get("documents", [])
        if isinstance(docs, list):
            relevant_data["documents"] = [extract_localized_text(d) for d in docs[:5]]
        else:
            relevant_data["documents"] = extract_localized_text(docs)
    
    elif intent == "ask_eligibility":
        eligibility = content.get("eligibility", {})
        rules = eligibility.get("rules", [])
        relevant_data["eligibility_rules"] = [extract_localized_text(r.get("text")) for r in rules[:3]]
    
    elif intent in ["ask_benefits", "ask_amount"]:
        benefits = content.get("benefits", {})
        relevant_data["benefits"] = extract_localized_text(benefits.get("text")) or extract_localized_text(benefits)
    
    elif intent == "ask_process":
        application = content.get("application", {})
        steps = application.get("steps", [])
        relevant_data["steps"] = [extract_localized_text(s) for s in steps[:4]]
    
    elif intent == "ask_location":
        application = content.get("application", {})
        locations = application.get("locations", [])
        relevant_data["locations"] = [extract_localized_text(l) for l in locations[:3]]
    
    else:
        short_answer = content.get("short_answer", {})
        relevant_data["short_answer"] = extract_localized_text(short_answer)
    
    context = {
        "intent": intent,
        "intent_confidence": confidence,
        "scheme_name": scheme_name,
        "scheme_id": scheme.get("id", scheme.get("scheme_id", "")),
        "user_query": user_query,
        "relevant_data": relevant_data,
        "conversation_history": conversation_history or [],
        "language": "hinglish"
    }
    
    return context


def build_llm_prompt(context: Dict) -> str:
    intent = context.get("intent", "general")
    scheme_name = context.get("scheme_name", "")
    user_query = context.get("user_query", "")
    relevant_data = context.get("relevant_data", {})
    
    data_str = json.dumps(relevant_data, ensure_ascii=False, indent=2)
    
    intent_instructions = {
        "ask_documents": "List all required documents with hyphen (-) for bullet points.",
        "ask_eligibility": "Explain who can apply. List conditions with hyphen (-) for bullet points.",
        "ask_benefits": "Mention the exact benefit amount.",
        "ask_amount": "Clearly state the monetary benefit.",
        "ask_process": "List application steps in order with numbers.",
        "ask_location": "Tell where to apply with hyphen (-) for bullet points.",
        "general": "Provide a concise helpful answer."
    }
    
    instruction = intent_instructions.get(intent, intent_instructions["general"])
    
    prompt = f"""You are JanSahayAI, a helpful government scheme assistant for Chhattisgarh.

USER QUERY: "{user_query}"
INTENT: {intent}
SCHEME: {scheme_name}
DATA: {data_str}

INSTRUCTION: {instruction}

RESPONSE GUIDELINES:
1. Respond in Hinglish (Hindi + English mix)
2. NO emojis, NO stars, NO asterisks for bullets
3. Use hyphen (-) for bullet points if needed
4. Use **bold** for headings only
5. Keep response concise and professional

RESPONSE:"""

    return prompt


def build_simple_prompt(user_query: str, scheme_name: str, intent: str) -> str:
    return f"""You are JanSahayAI. Respond in Hinglish. No emojis, no stars.
User asked: "{user_query}"
Scheme: {scheme_name}
Intent: {intent}
Keep response short and professional."""


# ========== ADD TO EXISTING response_builder.py ==========

def build_profile_summary(profile: Dict) -> str:
    """Build profile summary for display"""
    lines = ["**📋 Aapki di gayi jankari:**\n"]
    if "age" in profile:
        lines.append(f"• **Age:** {profile['age']} years")
    gender_map = {"male":"Purush","female":"Mahila","transgender":"Transgender"}
    if "gender" in profile:
        lines.append(f"• **Gender:** {gender_map.get(profile['gender'], profile['gender'])}")
    if "disability" in profile and isinstance(profile["disability"], dict):
        dtype = profile["disability"].get("type","")
        dtype_map = {"blind":"Blind","deaf":"Deaf","locomotor":"Locomotor","general":"Divyang"}
        lines.append(f"• **Disability:** {dtype_map.get(dtype, dtype)}")
        pct = profile["disability"].get("percentage")
        if pct: lines.append(f"• **Disability %:** {pct}%")
    if profile.get("is_student"):
        lines.append("• **Student:** Haan")
        edu = profile.get("education",{})
        if edu:
            edu_str = edu.get("course", edu.get("level",""))
            year = edu.get("year")
            if year: edu_str += f" - Year {year}"
            lines.append(f"• **Education:** {edu_str}")
    if "annual_income" in profile:
        lines.append(f"• **Annual Income:** ₹{profile['annual_income']:,}")
    if "bpl_status" in profile:
        lines.append(f"• **BPL:** {'Haan' if profile['bpl_status'] else 'Nahi'}")
    if "marital_status" in profile:
        marital_map = {"widow":"Vidhwa","divorced":"Talakshuda","married":"Vivahit","unmarried":"Avivahit"}
        lines.append(f"• **Marital:** {marital_map.get(profile['marital_status'], profile['marital_status'])}")
    certs = profile.get("certificates",{})
    if certs.get("has_disability_certificate"):
        lines.append("• **Disability Certificate:** Haan")
    return "\n".join(lines)