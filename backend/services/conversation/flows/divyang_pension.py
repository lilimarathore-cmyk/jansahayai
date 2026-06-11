# ============================================
# FILE: backend/services/conversation/flows/divyang_pension.py
# COMPLETE FIXED VERSION - ALL 10 SCHEMES WORKING
# ============================================

from typing import Tuple, Optional, Dict
from backend.database import get_scheme
from backend.services.response_builder import format_scheme_full_details, extract_localized_text
from backend.services.conversation.extractors import Extractors
from backend.services.conversation.eligibility import EligibilityChecker

class DivyangPensionFlow:
    
    @staticmethod
    def handle(message: str, session_id: str, user_data: Dict, user_sessions: Dict) -> Tuple[Optional[str], Optional[str]]:
        scheme_id = user_data.get("scheme_id", "cg_scheme_001")
        
        # ========== SCHEME 001 & 006 FLOW (Pension with Disability) ==========
        if scheme_id in ["cg_scheme_001", "cg_scheme_006"]:
            # Reset if step is invalid
            valid_steps = ["awaiting_age", "awaiting_disability", "awaiting_disability_type_choice", 
                          "awaiting_disability_type", "awaiting_income", "awaiting_school", "completed"]
            if user_data["step"] not in valid_steps:
                user_data["step"] = "awaiting_age"
                user_data.pop("age", None)
                user_data.pop("disability", None)
                user_data.pop("income", None)
                user_sessions[session_id] = user_data
            
            if user_data["step"] == "awaiting_age":
                age = Extractors.extract_age(message)
                if age:
                    # ✅ FIX: Scheme 001 ke liye age range 6-17 hai
                    if scheme_id == "cg_scheme_001":
                        if age < 6:
                            return (f"❌ आयु {age} वर्ष है। इस योजना के लिए न्यूनतम आयु 6 वर्ष है।\n\nकृपया सही **आयु** बताएं (6-17 वर्ष):", "needs_slot")
                        if age > 17:
                            return (f"❌ आयु {age} वर्ष है। इस योजना के लिए अधिकतम आयु 17 वर्ष है।\n\nकृपया सही **आयु** बताएं (6-17 वर्ष):", "needs_slot")
                    else:
                        # Scheme 006 ke liye age 18+ hai
                        if age < 18:
                            return (f"❌ आयु {age} वर्ष है। 18+ आयु चाहिए।\n\nकृपया सही **आयु** बताएं:", "needs_slot")
                    
                    user_data["age"] = age
                    user_data["step"] = "awaiting_disability"
                    user_sessions[session_id] = user_data
                    return (f"✅ आयु {age} वर्ष नोट कर ली गई।\n\nकृपया अपनी **विकलांगता का प्रतिशत** बताएं (40%+):", "needs_slot")
                else:
                    if scheme_id == "cg_scheme_001":
                        return ("कृपया अपनी **आयु** बताएं (6-17 वर्ष):", "needs_slot")
                    else:
                        return ("कृपया अपनी **आयु** बताएं (18+ वर्ष):", "needs_slot")

            if user_data["step"] == "awaiting_disability":
                disability = Extractors.extract_disability(message)
                if disability:
                    if disability < 40:
                        return (f"❌ विकलांगता {disability}% है। 40%+ चाहिए।\n\nसही **विकलांगता प्रतिशत** बताएं:", "needs_slot")
                    user_data["disability"] = disability
                    user_data["step"] = "awaiting_disability_type_choice"
                    user_sessions[session_id] = user_data
                    return (f"✅ विकलांगता {disability}% नोट कर ली गई।\n\nक्या आप अपनी विकलांगता का प्रकार बताना चाहेंगे? (हाँ/नहीं)", "needs_slot")
                else:
                    user_data["disability"] = 40
                    user_data["step"] = "awaiting_disability_type_choice"
                    user_sessions[session_id] = user_data
                    return (f"⚠️ विकलांगता **40%** मान रही हूँ।\n\nक्या आप अपनी विकलांगता का प्रकार बताना चाहेंगे? (हाँ/नहीं)", "needs_slot")

            if user_data["step"] == "awaiting_disability_type_choice":
                if Extractors.is_yes(message):
                    user_data["step"] = "awaiting_disability_type"
                    user_sessions[session_id] = user_data
                    return ("""कृपया अपनी विकलांगता का प्रकार बताएं:

1. अंधापन (Blindness)
2. कम दृष्टि (Low-vision)
3. बहरापन (Hearing Impairment)
4. चलने में असमर्थता (Locomotor Disability)
5. मानसिक बीमारी (Intellectual Disability)
6. बौनापन (Dwarfism)
7. ऑटिज्म (Autism Spectrum Disorder)
8. दिमागी लकवा (Cerebral Palsy)
9. बोलने में असमर्थता (Speech Disability)
10. कोई अन्य (Any other)

कोई नंबर बताएं (1-10):""", "needs_slot")
                else:
                    user_data["step"] = "awaiting_income"
                    user_sessions[session_id] = user_data
                    return ("कृपया अपनी **वार्षिक पारिवारिक आय** बताएं (रुपये में):", "needs_slot")

            if user_data["step"] == "awaiting_disability_type":
                disability_type_map = {
                    "1": "अंधापन", "2": "कम दृष्टि", "3": "बहरापन", "4": "चलने में असमर्थता",
                    "5": "मानसिक बीमारी", "6": "बौनापन", "7": "ऑटिज्म", "8": "दिमागी लकवा",
                    "9": "बोलने में असमर्थता", "10": "कोई अन्य"
                }
                selected = message.strip()
                if selected in disability_type_map:
                    user_data["disability_type"] = disability_type_map[selected]
                    user_data["step"] = "awaiting_income"
                    user_sessions[session_id] = user_data
                    return (f"✅ {disability_type_map[selected]} नोट कर लिया गया।\n\nकृपया अपनी **वार्षिक पारिवारिक आय** बताएं (रुपये में):", "needs_slot")
                else:
                    return ("कृपया सही नंबर बताएं (1-10):", "needs_slot")

            if user_data["step"] == "awaiting_income":
                income = Extractors.extract_income(message)
                if income:
                    user_data["income"] = income
                    if scheme_id == "cg_scheme_001" and 6 <= user_data["age"] <= 14:
                        user_data["step"] = "awaiting_school"
                        user_sessions[session_id] = user_data
                        return ("कृपया बताएं, क्या आप नियमित रूप से स्कूल जाते हैं? (हाँ/नहीं)", "needs_slot")
                    else:
                        user_data["step"] = "completed"
                        user_sessions[session_id] = user_data
                        is_eligible, reason = EligibilityChecker.check_eligibility(
                            scheme_id, age=user_data["age"], disability=user_data["disability"], income=user_data["income"])
                        scheme = get_scheme(scheme_id)
                        if scheme:
                            full_details = format_scheme_full_details(scheme)
                            response = f"✅ **आप इस योजना के लिए पात्र हैं!**\n\n{full_details}" if is_eligible else f"❌ **आप पात्र नहीं हैं।**\n\n**कारण:**\n{reason}\n\n{full_details}"
                            user_data["last_active_scheme_id"] = scheme_id
                            return (response, "success")
                        return ("योजना की जानकारी उपलब्ध नहीं है।", "error")
                else:
                    return ("कृपया अपनी **वार्षिक पारिवारिक आय** बताएं (रुपये में):", "needs_slot")

            if user_data["step"] == "awaiting_school":
                if Extractors.is_yes(message):
                    user_data["school_enrolled"] = "हाँ"
                elif Extractors.is_no(message):
                    user_data["school_enrolled"] = "नहीं"
                else:
                    return ("कृपया 'हाँ' या 'नहीं' में बताएं। क्या आप नियमित रूप से स्कूल जाते हैं?", "needs_slot")
                user_data["step"] = "completed"
                user_sessions[session_id] = user_data
                is_eligible, reason = EligibilityChecker.check_eligibility(
                    scheme_id, age=user_data["age"], disability=user_data["disability"], 
                    income=user_data["income"], school_enrolled=user_data.get("school_enrolled"))
                scheme = get_scheme(scheme_id)
                if scheme:
                    full_details = format_scheme_full_details(scheme)
                    response = f"✅ **आप इस योजना के लिए पात्र हैं!**\n\n{full_details}" if is_eligible else f"❌ **आप पात्र नहीं हैं।**\n\n**कारण:**\n{reason}\n\n{full_details}"
                    user_data["last_active_scheme_id"] = scheme_id
                    return (response, "success")
                return ("योजना की जानकारी उपलब्ध नहीं है।", "error")

        # ========== SCHEME 009 FLOW (Marriage Incentive) ==========
        elif scheme_id == "cg_scheme_009":
            valid_steps = ["awaiting_male_age", "awaiting_female_age", "awaiting_disability", "awaiting_first_marriage", "completed"]
            if user_data["step"] not in valid_steps:
                user_data["step"] = "awaiting_male_age"
                user_data.pop("male_age", None)
                user_data.pop("female_age", None)
                user_data.pop("disability", None)
                user_data.pop("first_marriage", None)
                user_sessions[session_id] = user_data
            
            if user_data["step"] == "awaiting_male_age":
                male_age = Extractors.extract_age(message)
                if male_age:
                    if male_age < 21 or male_age > 45:
                        return (f"❌ पुरुष की आयु {male_age} वर्ष है। 21-45 वर्ष चाहिए।\n\nकृपया सही **आयु** बताएं:", "needs_slot")
                    user_data["male_age"] = male_age
                    user_data["step"] = "awaiting_female_age"
                    user_sessions[session_id] = user_data
                    return (f"✅ पुरुष की आयु {male_age} वर्ष नोट कर ली गई।\n\nकृपया महिला की **आयु** बताएं (18-45 वर्ष):", "needs_slot")
                else:
                    return ("कृपया पुरुष की **आयु** बताएं (21-45 वर्ष):", "needs_slot")

            if user_data["step"] == "awaiting_female_age":
                female_age = Extractors.extract_age(message)
                if female_age:
                    if female_age < 18 or female_age > 45:
                        return (f"❌ महिला की आयु {female_age} वर्ष है। 18-45 वर्ष चाहिए।\n\nकृपया सही **आयु** बताएं:", "needs_slot")
                    user_data["female_age"] = female_age
                    user_data["step"] = "awaiting_disability"
                    user_sessions[session_id] = user_data
                    return (f"✅ महिला की आयु {female_age} वर्ष नोट कर ली गई।\n\nकृपया **विकलांगता प्रतिशत** बताएं (40%+):", "needs_slot")
                else:
                    return ("कृपया महिला की **आयु** बताएं (18-45 वर्ष):", "needs_slot")

            if user_data["step"] == "awaiting_disability":
                disability = Extractors.extract_disability(message)
                if disability:
                    if disability < 40:
                        return (f"❌ विकलांगता {disability}% है। 40%+ चाहिए।\n\nसही **विकलांगता प्रतिशत** बताएं:", "needs_slot")
                    user_data["disability"] = disability
                    user_data["step"] = "awaiting_first_marriage"
                    user_sessions[session_id] = user_data
                    return (f"✅ विकलांगता {disability}% नोट कर ली गई।\n\nक्या यह **पुरुष की पहली शादी** है? (हाँ/नहीं)", "needs_slot")
                else:
                    user_data["disability"] = 40
                    user_data["step"] = "awaiting_first_marriage"
                    user_sessions[session_id] = user_data
                    return (f"⚠️ विकलांगता **40%** मान रही हूँ।\n\nक्या यह **पुरुष की पहली शादी** है? (हाँ/नहीं)", "needs_slot")

            if user_data["step"] == "awaiting_first_marriage":
                if Extractors.is_yes(message):
                    user_data["first_marriage"] = "हाँ"
                elif Extractors.is_no(message):
                    user_data["first_marriage"] = "नहीं"
                else:
                    return ("कृपया 'हाँ' या 'नहीं' में बताएं। क्या यह पुरुष की पहली शादी है?", "needs_slot")
                user_data["step"] = "completed"
                user_sessions[session_id] = user_data
                is_eligible, reason = EligibilityChecker.check_eligibility(
                    scheme_id, male_age=user_data["male_age"], female_age=user_data["female_age"],
                    disability=user_data["disability"], first_marriage=user_data["first_marriage"])
                scheme = get_scheme(scheme_id)
                if scheme:
                    full_details = format_scheme_full_details(scheme)
                    response = f"✅ **आप पात्र हैं!**\n\n{full_details}" if is_eligible else f"❌ **आप पात्र नहीं हैं।**\n\n**कारण:**\n{reason}\n\n{full_details}"
                    user_data["last_active_scheme_id"] = scheme_id
                    return (response, "success")
                return ("योजना की जानकारी उपलब्ध नहीं है।", "error")

        # ========== SCHEME 010 FLOW (Scholarship) ==========
        elif scheme_id == "cg_scheme_010":
            valid_steps = ["awaiting_age", "awaiting_disability", "awaiting_class", "awaiting_study_status", "awaiting_previous_pass", "completed"]
            if user_data["step"] not in valid_steps:
                user_data["step"] = "awaiting_age"
                user_data.pop("age", None)
                user_data.pop("disability", None)
                user_data.pop("class_grade", None)
                user_data.pop("study_status", None)
                user_data.pop("previous_class_pass", None)
                user_sessions[session_id] = user_data
            
            if user_data["step"] == "awaiting_age":
                age = Extractors.extract_age(message)
                if age:
                    user_data["age"] = age
                    user_data["step"] = "awaiting_disability"
                    user_sessions[session_id] = user_data
                    return (f"✅ आयु {age} वर्ष नोट कर ली गई।\n\n**विकलांगता प्रतिशत** बताएं (40%+):", "needs_slot")
                else:
                    return ("कृपया अपनी **आयु** बताएं:", "needs_slot")

            if user_data["step"] == "awaiting_disability":
                disability = Extractors.extract_disability(message)
                if disability:
                    if disability < 40:
                        return (f"❌ विकलांगता {disability}% है। 40%+ चाहिए।\n\nसही **विकलांगता प्रतिशत** बताएं:", "needs_slot")
                    user_data["disability"] = disability
                    user_data["step"] = "awaiting_class"
                    user_sessions[session_id] = user_data
                    return (f"✅ विकलांगता {disability}% नोट कर ली गई।\n\n**किस कक्षा में** पढ़ते हैं? (1-12)", "needs_slot")
                else:
                    user_data["disability"] = 40
                    user_data["step"] = "awaiting_class"
                    user_sessions[session_id] = user_data
                    return (f"⚠️ विकलांगता **40%** मान रही हूँ।\n\n**किस कक्षा में** पढ़ते हैं? (1-12)", "needs_slot")

            if user_data["step"] == "awaiting_class":
                class_num = Extractors.extract_age(message)
                if class_num and 1 <= class_num <= 12:
                    user_data["class_grade"] = class_num
                    user_data["step"] = "awaiting_study_status"
                    user_sessions[session_id] = user_data
                    return (f"✅ कक्षा {class_num} नोट कर ली गई।\n\n**नियमित अध्ययनरत** हैं? (हाँ/नहीं)", "needs_slot")
                else:
                    return ("कृपया **कक्षा** बताएं (1-12):", "needs_slot")

            if user_data["step"] == "awaiting_study_status":
                if Extractors.is_yes(message):
                    user_data["study_status"] = "हाँ"
                elif Extractors.is_no(message):
                    user_data["study_status"] = "नहीं"
                else:
                    return ("कृपया 'हाँ' या 'नहीं' में बताएं। क्या आप नियमित अध्ययनरत हैं?", "needs_slot")
                user_data["step"] = "awaiting_previous_pass"
                user_sessions[session_id] = user_data
                return ("क्या आपने **पिछली कक्षा उत्तीर्ण** की है? (हाँ/नहीं)", "needs_slot")

            if user_data["step"] == "awaiting_previous_pass":
                if Extractors.is_yes(message):
                    user_data["previous_class_pass"] = "हाँ"
                elif Extractors.is_no(message):
                    user_data["previous_class_pass"] = "नहीं"
                else:
                    return ("कृपया 'हाँ' या 'नहीं' में बताएं। क्या आपने पिछली कक्षा उत्तीर्ण की है?", "needs_slot")
                user_data["step"] = "completed"
                user_sessions[session_id] = user_data
                is_eligible, reason = EligibilityChecker.check_eligibility(
                    scheme_id, disability=user_data["disability"], class_grade=user_data["class_grade"],
                    study_status=user_data["study_status"], previous_class_pass=user_data["previous_class_pass"])
                scheme = get_scheme(scheme_id)
                if scheme:
                    full_details = format_scheme_full_details(scheme)
                    response = f"✅ **आप पात्र हैं!**\n\n{full_details}" if is_eligible else f"❌ **आप पात्र नहीं हैं।**\n\n**कारण:**\n{reason}\n\n{full_details}"
                    user_data["last_active_scheme_id"] = scheme_id
                    return (response, "success")
                return ("योजना की जानकारी उपलब्ध नहीं है।", "error")

        # ========== SCHEME 011 FLOW (Higher Education) ==========
        elif scheme_id == "cg_scheme_011":
            valid_steps = ["awaiting_age", "awaiting_disability", "awaiting_education", "awaiting_study_status", "awaiting_previous_qualification", "completed"]
            if user_data["step"] not in valid_steps:
                user_data["step"] = "awaiting_age"
                user_data.pop("age", None)
                user_data.pop("disability", None)
                user_data.pop("education_level", None)
                user_data.pop("study_status", None)
                user_data.pop("previous_qualification", None)
                user_sessions[session_id] = user_data
            
            if user_data["step"] == "awaiting_age":
                age = Extractors.extract_age(message)
                if age:
                    if age < 18:
                        return (f"❌ आयु {age} वर्ष है। 18+ आयु चाहिए।\n\nकृपया सही **आयु** बताएं:", "needs_slot")
                    user_data["age"] = age
                    user_data["step"] = "awaiting_disability"
                    user_sessions[session_id] = user_data
                    return (f"✅ आयु {age} वर्ष नोट कर ली गई।\n\n**विकलांगता प्रतिशत** बताएं (40%+):", "needs_slot")
                else:
                    return ("कृपया अपनी **आयु** बताएं (18+ वर्ष):", "needs_slot")

            if user_data["step"] == "awaiting_disability":
                disability = Extractors.extract_disability(message)
                if disability:
                    if disability < 40:
                        return (f"❌ विकलांगता {disability}% है। 40%+ चाहिए।\n\nसही **विकलांगता प्रतिशत** बताएं:", "needs_slot")
                    user_data["disability"] = disability
                    user_data["step"] = "awaiting_education"
                    user_sessions[session_id] = user_data
                    return (f"✅ विकलांगता {disability}% नोट कर ली गई।\n\n**किस उच्च शिक्षा में** हैं?\n1. स्नातक\n2. परास्नातक\n3. डिप्लोमा\n4. आईटीआई\n\nनंबर बताएं:", "needs_slot")
                else:
                    user_data["disability"] = 40
                    user_data["step"] = "awaiting_education"
                    user_sessions[session_id] = user_data
                    return (f"⚠️ विकलांगता **40%** मान रही हूँ।\n\n**किस उच्च शिक्षा में** हैं?\n1. स्नातक\n2. परास्नातक\n3. डिप्लोमा\n4. आईटीआई\n\nनंबर बताएं:", "needs_slot")

            if user_data["step"] == "awaiting_education":
                education = Extractors.extract_education_level(message)
                if education:
                    user_data["education_level"] = education
                    user_data["step"] = "awaiting_study_status"
                    user_sessions[session_id] = user_data
                    return (f"✅ {education} नोट कर लिया गया।\n\n**नियमित अध्ययनरत** हैं? (हाँ/नहीं)", "needs_slot")
                else:
                    return ("कृपया नंबर बताएं (1,2,3,4):", "needs_slot")

            if user_data["step"] == "awaiting_study_status":
                if Extractors.is_yes(message):
                    user_data["study_status"] = "हाँ"
                elif Extractors.is_no(message):
                    user_data["study_status"] = "नहीं"
                else:
                    return ("कृपया 'हाँ' या 'नहीं' में बताएं। क्या आप नियमित अध्ययनरत हैं?", "needs_slot")
                user_data["step"] = "awaiting_previous_qualification"
                user_sessions[session_id] = user_data
                edu = user_data.get("education_level", "")
                if "स्नातक" in edu:
                    qual_question = "क्या आपने **12वीं** उत्तीर्ण की है? (हाँ/नहीं)"
                elif "परास्नातक" in edu:
                    qual_question = "क्या आपने **स्नातक** उत्तीर्ण किया है? (हाँ/नहीं)"
                elif "डिप्लोमा" in edu:
                    qual_question = "क्या आपने **12वीं** उत्तीर्ण की है? (हाँ/नहीं)"
                else:
                    qual_question = "क्या आपने **10वीं या 12वीं** उत्तीर्ण की है? (हाँ/नहीं)"
                return (qual_question, "needs_slot")

            if user_data["step"] == "awaiting_previous_qualification":
                if Extractors.is_yes(message):
                    user_data["previous_qualification"] = "हाँ"
                elif Extractors.is_no(message):
                    user_data["previous_qualification"] = "नहीं"
                else:
                    return ("कृपया 'हाँ' या 'नहीं' में बताएं।", "needs_slot")
                user_data["step"] = "completed"
                user_sessions[session_id] = user_data
                is_eligible, reason = EligibilityChecker.check_eligibility(
                    scheme_id, age=user_data.get("age"), disability=user_data.get("disability"),
                    education_level=user_data.get("education_level"), study_status=user_data.get("study_status"),
                    previous_qualification=user_data.get("previous_qualification"))
                scheme = get_scheme(scheme_id)
                if scheme:
                    full_details = format_scheme_full_details(scheme)
                    response = f"✅ **आप पात्र हैं!**\n\n{full_details}" if is_eligible else f"❌ **आप पात्र नहीं हैं।**\n\n**कारण:**\n{reason}\n\n{full_details}"
                    user_data["last_active_scheme_id"] = scheme_id
                    return (response, "success")
                return ("योजना की जानकारी उपलब्ध नहीं है।", "error")

        # ========== SCHEME 012 FLOW (Civil Services) ==========
        elif scheme_id == "cg_scheme_012":
            valid_steps = ["awaiting_disability", "awaiting_exam", "completed"]
            if user_data["step"] not in valid_steps:
                user_data["step"] = "awaiting_disability"
                user_data.pop("disability", None)
                user_data.pop("exam_type", None)
                user_sessions[session_id] = user_data
            
            if user_data["step"] == "awaiting_disability":
                disability = Extractors.extract_disability(message)
                if disability:
                    if disability < 40:
                        return (f"❌ विकलांगता {disability}% है। 40%+ चाहिए।\n\nसही **विकलांगता प्रतिशत** बताएं:", "needs_slot")
                    user_data["disability"] = disability
                    user_data["step"] = "awaiting_exam"
                    user_sessions[session_id] = user_data
                    return (f"✅ विकलांगता {disability}% नोट कर ली गई।\n\n**कौन सी परीक्षा** पास की?\n1. UPSC\n2. CGPSC\n\nनंबर बताएं:", "needs_slot")
                else:
                    user_data["disability"] = 40
                    user_data["step"] = "awaiting_exam"
                    user_sessions[session_id] = user_data
                    return (f"⚠️ विकलांगता **40%** मान रही हूँ।\n\n**कौन सी परीक्षा** पास की?\n1. UPSC\n2. CGPSC\n\nनंबर बताएं:", "needs_slot")

            if user_data["step"] == "awaiting_exam":
                exam_type = Extractors.extract_exam_type(message)
                if exam_type:
                    user_data["exam_type"] = exam_type
                    user_data["step"] = "completed"
                    user_sessions[session_id] = user_data
                    is_eligible, reason = EligibilityChecker.check_eligibility(
                        scheme_id, disability=user_data.get("disability"), exam_type=user_data.get("exam_type"))
                    scheme = get_scheme(scheme_id)
                    if scheme:
                        full_details = format_scheme_full_details(scheme)
                        response = f"✅ **आप पात्र हैं!**\n\n{full_details}" if is_eligible else f"❌ **आप पात्र नहीं हैं।**\n\n**कारण:**\n{reason}\n\n{full_details}"
                        user_data["last_active_scheme_id"] = scheme_id
                        return (response, "success")
                    return ("योजना की जानकारी उपलब्ध नहीं है।", "error")
                else:
                    return ("कृपया नंबर बताएं (1 या 2):", "needs_slot")

        # ========== SCHEME 013 FLOW (Hostel) ==========
        elif scheme_id == "cg_scheme_013":
            valid_steps = ["awaiting_disability", "awaiting_education", "awaiting_distance", "completed"]
            if user_data["step"] not in valid_steps:
                user_data["step"] = "awaiting_disability"
                user_data.pop("disability", None)
                user_data.pop("education_level_hostel", None)
                user_data.pop("distance", None)
                user_sessions[session_id] = user_data
            
            if user_data["step"] == "awaiting_disability":
                disability = Extractors.extract_disability(message)
                if disability:
                    if disability < 40:
                        return (f"❌ विकलांगता {disability}% है। 40%+ चाहिए।\n\nसही **विकलांगता प्रतिशत** बताएं:", "needs_slot")
                    user_data["disability"] = disability
                    user_data["step"] = "awaiting_education"
                    user_sessions[session_id] = user_data
                    return (f"✅ विकलांगता {disability}% नोट कर ली गई।\n\n**किस कक्षा में** पढ़ते हैं?\n1. 12वीं उत्तीर्ण\n2. महाविद्यालय में अध्ययनरत\n\nनंबर बताएं:", "needs_slot")
                else:
                    user_data["disability"] = 40
                    user_data["step"] = "awaiting_education"
                    user_sessions[session_id] = user_data
                    return (f"⚠️ विकलांगता **40%** मान रही हूँ।\n\n**किस कक्षा में** पढ़ते हैं?\n1. 12वीं उत्तीर्ण\n2. महाविद्यालय में अध्ययनरत\n\nनंबर बताएं:", "needs_slot")

            if user_data["step"] == "awaiting_education":
                education = Extractors.extract_education_level_hostel(message)
                if education:
                    user_data["education_level_hostel"] = education
                    user_data["step"] = "awaiting_distance"
                    user_sessions[session_id] = user_data
                    return (f"✅ {education} नोट कर लिया गया।\n\n**घर से संस्थान की दूरी** कितनी है? (20 किमी से अधिक)", "needs_slot")
                else:
                    return ("कृपया नंबर बताएं (1 या 2):", "needs_slot")

            if user_data["step"] == "awaiting_distance":
                distance = Extractors.extract_distance(message)
                if distance:
                    if distance <= 20:
                        return (f"❌ दूरी {distance} किमी है। 20 किमी से अधिक चाहिए।\n\nकृपया सही **दूरी** बताएं:", "needs_slot")
                    user_data["distance"] = distance
                    user_data["step"] = "completed"
                    user_sessions[session_id] = user_data
                    is_eligible, reason = EligibilityChecker.check_eligibility(
                        scheme_id, disability=user_data.get("disability"),
                        education_level_hostel=user_data.get("education_level_hostel"),
                        distance=user_data.get("distance"))
                    scheme = get_scheme(scheme_id)
                    if scheme:
                        full_details = format_scheme_full_details(scheme)
                        response = f"✅ **आप पात्र हैं!**\n\n{full_details}" if is_eligible else f"❌ **आप पात्र नहीं हैं।**\n\n**कारण:**\n{reason}\n\n{full_details}"
                        user_data["last_active_scheme_id"] = scheme_id
                        return (response, "success")
                    return ("योजना की जानकारी उपलब्ध नहीं है।", "error")
                else:
                    return ("कृपया **दूरी** किलोमीटर में बताएं (जैसे: 25, 30):", "needs_slot")

        # ========== SCHEME 014 FLOW (Camp) - ✅ FIXED with Eligible text ==========
        elif scheme_id == "cg_scheme_014":
            scheme = get_scheme("cg_scheme_014")
            if scheme:
                full_details = format_scheme_full_details(scheme)
                scheme_name = extract_localized_text(scheme.get("scheme_name"), "hi")
                # ✅ FIX: Eligible text add karo taaki PDF button frontend mein dikh sake
                response = f"✅ **आप {scheme_name} के लिए पात्र हैं!**\n\n{full_details}"
            else:
                response = """✅ **आप दिव्यांगजन हेतु शिविरों का आयोजन के लिए पात्र हैं!**

इस योजना में दिव्यांगजनों के लिए शिविर लगाकर प्रमाण पत्र, उपकरण और परामर्श दिया जाता है।

✅ **शिविर में क्या मिलता है:**
• दिव्यांगता प्रमाण पत्र बनाना
• सहायक उपकरण (व्हीलचेयर, कैन, श्रवण यंत्र) वितरण
• पेंशन एवं अन्य योजनाओं से जोड़ना
• चिकित्सा परामर्श

📍 **शिविर की जानकारी के लिए:** जिला दिव्यांगजन सशक्तिकरण कार्यालय से संपर्क करें।

📥 **डाउनलोड फॉर्म:** /forms/cg_scheme_014.pdf"""
            user_data["last_active_scheme_id"] = scheme_id
            del user_sessions[session_id]
            return (response, "success")

        # ========== SCHEME 015 FLOW (Assistive Devices) ==========
        elif scheme_id == "cg_scheme_015":
            valid_steps = ["awaiting_disability", "awaiting_income", "completed"]
            if user_data["step"] not in valid_steps:
                user_data["step"] = "awaiting_disability"
                user_data.pop("disability", None)
                user_data.pop("income", None)
                user_sessions[session_id] = user_data
            
            if user_data["step"] == "awaiting_disability":
                disability = Extractors.extract_disability(message)
                if disability:
                    if disability < 40:
                        return (f"❌ विकलांगता {disability}% है। 40%+ चाहिए।\n\nसही **विकलांगता प्रतिशत** बताएं:", "needs_slot")
                    user_data["disability"] = disability
                    user_data["step"] = "awaiting_income"
                    user_sessions[session_id] = user_data
                    return (f"✅ विकलांगता {disability}% नोट कर ली गई।\n\nकृपया अपनी **मासिक पारिवारिक आय** बताएं (₹6500 से कम):", "needs_slot")
                else:
                    user_data["disability"] = 40
                    user_data["step"] = "awaiting_income"
                    user_sessions[session_id] = user_data
                    return (f"⚠️ विकलांगता **40%** मान रही हूँ।\n\nकृपया अपनी **मासिक पारिवारिक आय** बताएं (₹6500 से कम):", "needs_slot")

            if user_data["step"] == "awaiting_income":
                income = Extractors.extract_income(message)
                if income:
                    if income >= 6500:
                        return (f"❌ मासिक आय ₹{income} है। ₹6500 से कम चाहिए।\n\nकृपया सही **आय** बताएं:", "needs_slot")
                    user_data["income"] = income
                    user_data["step"] = "completed"
                    user_sessions[session_id] = user_data
                    is_eligible, reason = EligibilityChecker.check_eligibility(
                        scheme_id, disability=user_data.get("disability"), income=user_data.get("income"))
                    scheme = get_scheme(scheme_id)
                    if scheme:
                        full_details = format_scheme_full_details(scheme)
                        response = f"✅ **आप पात्र हैं!**\n\n{full_details}" if is_eligible else f"❌ **आप पात्र नहीं हैं।**\n\n**कारण:**\n{reason}\n\n{full_details}"
                        user_data["last_active_scheme_id"] = scheme_id
                        return (response, "success")
                    return ("योजना की जानकारी उपलब्ध नहीं है।", "error")
                else:
                    return ("कृपया अपनी **मासिक आय** रुपये में बताएं (जैसे: 5000, 6000):", "needs_slot")

        # ========== SCHEME 016 FLOW (Rehabilitation) - ✅ FIXED with Eligible text ==========
        elif scheme_id == "cg_scheme_016":
            scheme = get_scheme("cg_scheme_016")
            if scheme:
                full_details = format_scheme_full_details(scheme)
                scheme_name = extract_localized_text(scheme.get("scheme_name"), "hi")
                # ✅ FIX: Eligible text add karo taaki PDF button frontend mein dikh sake
                response = f"✅ **आप {scheme_name} के लिए पात्र हैं!**\n\n{full_details}"
            else:
                response = """✅ **आप राष्ट्रीय दिव्यांगजन पुनर्वास कार्यक्रम के लिए पात्र हैं!**

इस कार्यक्रम में दिव्यांगजनों को मार्गदर्शन, प्रमाण पत्र एवं योजनाओं से जोड़ने का कार्य किया जाता है।

✅ **कार्यक्रम की विशेषताएं:**
• दिव्यांगता प्रमाण पत्र हेतु मार्गदर्शन
• सरकारी योजनाओं से जोड़ना
• रोजगार एवं स्वरोजगार हेतु प्रशिक्षण
• पुनर्वास के लिए सहायता

📍 **संपर्क करें:** जिला दिव्यांगजन सशक्तिकरण कार्यालय

📥 **डाउनलोड फॉर्म:** /forms/cg_scheme_016.pdf"""
            user_data["last_active_scheme_id"] = scheme_id
            del user_sessions[session_id]
            return (response, "success")

        return (None, None)