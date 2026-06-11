# backend/llm/groq_client.py
# COMPLETE FIXED VERSION - Hinglish responses for better understanding

import os
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv
from groq import Groq

load_dotenv()


def get_client():
    """Get Groq client instance"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("⚠️ GROQ_API_KEY not found. Please set it in .env file")
        return None
    return Groq(api_key=api_key)


def run_completion(messages: List[Dict]) -> Optional[str]:
    """Run LLM completion with Groq"""
    client = get_client()
    if client is None:
        return None
    
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.7,
            max_tokens=1000,
            top_p=0.9
        )
        return response.choices[0].message.content
    except Exception as exc:
        print(f"LLM ERROR: {exc}")
        return None


# ========== ELIGIBILITY RESPONSE (Most Important) ==========

def generate_eligibility_response(
    scheme_name: str,
    is_eligible: bool,
    reasons: Optional[str],
    benefits: str,
    documents: List[str],
    application_steps: List[str],
    user_entities: Dict[str, Any],
    missing_info: List[str]
) -> Optional[str]:
    """
    Generate eligibility check response in Hinglish (Hindi + English mix)
    """
    
    if is_eligible:
        prompt = f"""You are JanSahayAI, a helpful government scheme assistant for Chhattisgarh.

SCHEME NAME: {scheme_name}
USER IS ELIGIBLE ✅

BENEFITS: {benefits}

REQUIRED DOCUMENTS:
{chr(10).join(['• ' + d for d in documents[:5]])}

APPLICATION STEPS:
{chr(10).join([f'{i+1}. ' + s for i, s in enumerate(application_steps[:4])])}

USER INFO PROVIDED: {user_entities}

INSTRUCTIONS - Respond in HINGLISH (mix of Hindi and English):
1. Start with "✅ Aap [scheme name] ke liye eligible hain!"
2. Mention benefit with "💰 Benefit: [amount] per month"
3. List documents with "📋 Documents required:" (bullet points)
4. Explain process with "📝 How to apply:" (numbered steps)
5. End with "❓ Kya aap aur koi information chahte hain?"

Keep it conversational. Use simple words. Don't use pure Hindi. Example:
"✅ Aap Social Security Divyang Pension Yojana ke liye eligible hain! 💰 Aapko ₹500 per month pension milega. 📋 Documents: Aadhar card, Disability certificate. 📝 Apply: Gram Panchayat me form submit karein." 

RESPONSE:"""
    
    else:
        # Build alternative suggestion
        alternative_suggestion = ""
        if "age" in str(reasons).lower():
            alternative_suggestion = "💡 Aap Indira Gandhi Divyang Pension Yojana (18+ years ke liye) try kar sakte hain."
        elif "disability" in str(reasons).lower():
            alternative_suggestion = "💡 Aap Mukhyamantri Pension Yojana try kar sakte hain."
        
        prompt = f"""You are JanSahayAI, a helpful government scheme assistant for Chhattisgarh.

SCHEME NAME: {scheme_name}
USER IS NOT ELIGIBLE ❌

FAILURE REASONS:
{reasons}

BENEFITS: {benefits}

USER INFO PROVIDED: {user_entities}
MISSING INFO NEEDED: {missing_info if missing_info else 'None'}

ALTERNATIVE SUGGESTION: {alternative_suggestion}

INSTRUCTIONS - Respond in HINGLISH (mix of Hindi and English):
1. Start with "❌ Aap [scheme name] ke liye eligible nahi hain"
2. Explain reasons in simple Hinglish (2-3 lines max)
3. If missing info exists, ask for it politely
4. Suggest alternative scheme if available
5. End with helpful question

Keep it polite and helpful. Don't discourage the user. Example:
"❌ Aap Social Security Divyang Pension Yojana ke liye eligible nahi hain. Kyunki ye scheme sirf 6-17 years ke bachchon ke liye hai. 💡 Aap Indira Gandhi Divyang Pension Yojana try kar sakte hain jo 18+ years ke liye hai."

RESPONSE:"""
    
    messages = [
        {
            "role": "system",
            "content": """You are JanSahayAI, a helpful government scheme assistant for Chhattisgarh.

CRITICAL RULES:
1. ALWAYS respond in HINGLISH (Hindi + English mix) - NOT pure Hindi
2. Use simple words that everyone can understand
3. Examples of Hinglish: 
   - "Aap eligible hain" (NOT "आप पात्र हैं")
   - "Benefits kya hain?" (NOT "लाभ क्या हैं?")
   - "Documents required" (NOT "आवश्यक दस्तावेज")
   - "Kaise apply karein?" (NOT "आवेदन कैसे करें?")

4. Use emojis: ✅ for eligible, ❌ for not eligible, 💰 for benefits, 📋 for documents, 📝 for process, 💡 for suggestions
5. Be concise - 3-4 sentences maximum for eligibility response
6. Always be helpful and polite

Example Response (Eligible):
"✅ Aap Social Security Divyang Pension Yojana ke liye eligible hain! 💰 Aapko ₹500 per month pension milega. 📋 Documents: Aadhar card, Disability certificate, Bank passbook. 📝 Gram Panchayat me form submit karein. ❓ Kya aap form download karna chahenge?"

Example Response (Not Eligible):
"❌ Aap is scheme ke liye eligible nahi hain. Kyunki ye scheme sirf 6-17 years ke bachchon ke liye hai. 💡 Aap Indira Gandhi Divyang Pension Yojana try kar sakte hain jo 18+ years ke liye hai."""
        },
        {"role": "user", "content": prompt}
    ]
    
    return run_completion(messages)


# ========== SCHEME INFORMATION RESPONSE ==========

def generate_scheme_info_response(
    scheme_name: str,
    benefits: str,
    documents: List[str],
    application_steps: List[str],
    locations: List[str],
    intent: str
) -> Optional[str]:
    """
    Generate general scheme information response in Hinglish
    """
    
    prompt = f"""You are JanSahayAI.

SCHEME: {scheme_name}
USER ASKED ABOUT: {intent}

INFORMATION:
- Benefits: {benefits}
- Documents: {documents[:5]}
- Steps: {application_steps[:4]}
- Locations: {locations[:3]}

INSTRUCTIONS - Respond in HINGLISH (Hindi + English mix):

If intent is "ask_documents":
- Focus on listing required documents with 📋 emoji
- Write: "Documents required hain:" then bullet points

If intent is "ask_benefits":
- Focus on benefits with 💰 emoji
- Write: "Is scheme ke benefits:" then explain

If intent is "ask_process":
- Focus on steps with 📝 emoji
- Number the steps (1., 2., 3.)

If intent is "general":
- Give overview: benefits first, then documents, then process

Keep response short (4-5 lines max). Use Hinglish, not pure Hindi.

RESPONSE:"""
    
    messages = [
        {
            "role": "system",
            "content": "You are JanSahayAI. Respond in Hinglish (Hindi+English mix) with emojis. Keep it short and helpful."
        },
        {"role": "user", "content": prompt}
    ]
    
    return run_completion(messages)


# ========== FOLLOW-UP QUESTION RESPONSE ==========

def generate_followup_response(
    scheme_name: str,
    missing_fields: List[str],
    current_entities: Dict[str, Any]
) -> Optional[str]:
    """
    Generate follow-up question when information is missing (Hinglish)
    """
    
    field_names = {
        "age": "your age / aapki age",
        "disability_percentage": "disability percentage / divyangta percentage",
        "income": "your annual/monthly income",
        "bpl_status": "BPL status (yes/no)",
        "gender": "gender (male/female)",
        "disability": "divyangta percentage"
    }
    
    missing_fields_en = [field_names.get(f, f) for f in missing_fields]
    
    prompt = f"""You are JanSahayAI.

User is checking eligibility for {scheme_name}.
Current info: {current_entities}
Missing info needed: {missing_fields_en}

Generate a short follow-up question in HINGLISH asking for the missing information.
Be polite and specific.
Example: "❓ Please tell me your age. Kya aap apni age bata sakte hain?"

RESPONSE:"""
    
    messages = [
        {"role": "system", "content": "You are JanSahayAI. Ask for missing information politely in Hinglish (Hindi+English mix). Keep it short (1 sentence)."},
        {"role": "user", "content": prompt}
    ]
    
    response = run_completion(messages)
    
    # Fallback if LLM fails
    if not response:
        missing_text = ", ".join(missing_fields_en)
        response = f"❓ Please tell me: {missing_text}. Kya aap ye information de sakte hain?"
    
    return response


# ========== WELCOME MESSAGE ==========

def generate_welcome_message() -> str:
    """Generate welcome message in Hinglish"""
    
    prompt = """Generate a short welcome message in HINGLISH (Hindi+English mix) for JanSahayAI bot.

Include:
- Greeting with 🙏 emoji
- Your name: JanSahayAI
- 3 example questions in Hinglish
- Closing with 😊

Keep it under 100 words. Use simple Hinglish.
Example style: "Namaste! 🙏 Main JanSahayAI hoon..."

RESPONSE:"""
    
    messages = [
        {"role": "system", "content": "You are JanSahayAI. Generate a short welcome message in Hinglish."},
        {"role": "user", "content": prompt}
    ]
    
    response = run_completion(messages)
    
    # Fallback if LLM fails
    if not response:
        response = """Namaste! 🙏

Main JanSahayAI hoon. Main Chhattisgarh ki government schemes ke baare me information deta hoon.

Aap mujhse pooch sakte hain:
• "Divyang pension ke liye kya documents chahiye?"
• "Kya main pension ke liye eligible hoon?"
• "Scheme kaise apply karein?"

Apna question likhiye, main help karunga! 😊"""
    
    return response


# ========== SIMPLE RESPONSE (Fallback) ==========

def generate_simple_response(message: str) -> Optional[str]:
    """Simple response for general queries"""
    
    prompt = f"""User asked: "{message}"

Respond in HINGLISH (Hindi+English mix) with emojis.
Keep it helpful but short (2-3 sentences).
If you don't know, suggest asking about schemes.

RESPONSE:"""
    
    messages = [
        {"role": "system", "content": "You are JanSahayAI. Respond in Hinglish with emojis. Be helpful."},
        {"role": "user", "content": prompt}
    ]
    
    return run_completion(messages)


# ========== TEST FUNCTION ==========

def test_llm():
    """Test LLM connection and generation"""
    print("=" * 50)
    print("Testing LLM Connection...")
    print("=" * 50)
    
    # Test 1: Eligibility response (Eligible)
    print("\n1. Testing ELIGIBLE response...")
    response1 = generate_eligibility_response(
        scheme_name="Social Security Divyang Pension Yojana",
        is_eligible=True,
        reasons=None,
        benefits="₹500 per month pension",
        documents=["Aadhar card", "Disability certificate", "Bank passbook"],
        application_steps=["Get form from Gram Panchayat", "Fill and submit", "Get approval"],
        user_entities={"age": 45, "disability": 50},
        missing_info=[]
    )
    
    if response1:
        print(f"✅ Response:\n{response1}\n")
    else:
        print("❌ Test 1 failed - check API key\n")
    
    # Test 2: Eligibility response (Not Eligible)
    print("\n2. Testing NOT ELIGIBLE response...")
    response2 = generate_eligibility_response(
        scheme_name="Social Security Divyang Pension Yojana",
        is_eligible=False,
        reasons="• Age 45 years hai. Ye scheme 6-17 years ke liye hai.",
        benefits="₹500 per month pension",
        documents=["Aadhar card", "Disability certificate"],
        application_steps=["Apply at Gram Panchayat"],
        user_entities={"age": 45, "disability": 50},
        missing_info=[]
    )
    
    if response2:
        print(f"✅ Response:\n{response2}\n")
    else:
        print("❌ Test 2 failed\n")
    
    # Test 3: Welcome message
    print("\n3. Testing WELCOME message...")
    response3 = generate_welcome_message()
    if response3:
        print(f"✅ Response:\n{response3}\n")
    else:
        print("❌ Test 3 failed\n")
    
    print("=" * 50)
    print("LLM Test Complete")
    print("=" * 50)
    
    return response1


if __name__ == "__main__":
    test_llm()