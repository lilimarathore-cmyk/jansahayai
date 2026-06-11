# ============================================
# FILE: backend/services/conversation/keywords.py
# All keyword arrays
# ============================================

class ConversationKeywords:
    # Divyang pension scheme keywords
    divyang_pension_keywords = [
        "दिव्यांग पेंशन", "सामाजिक सुरक्षा", "divyang pension",
        "पेंशन योजना", "विकलांग पेंशन", "500 रुपए","दिव्यांग", "विकलांग", "divyang", "viklang", "अपंग", "disabled",
        "divyang yojna", "divyang scheme", "divyang yojanaye", "divyang yojnaon", "दिव्यांग योजनाओं के बारे में बताओ",
        "दिव्यांग योजना के बारे में बताओ", "divyang yojna ke bare me batao", "divyang scheme ke bare me batao", "दिव्यांग पेंशन कैसे मिलेगी",
        "दिव्यांग पेंशन कैसे मिलती है", "divyang pension kaise milegi", "divyang pension kaise milti hai", 
        "विकलांग पेंशन कैसे मिलेगी", "विकलांग पेंशन कैसे मिलती है", "viklang pension kaise milegi", "viklang pension kaise milti hai",  
        "दिव्यांग पेंशन के लिए क्या करना होगा", "divyang pension ke liye kya karna hoga", 
        "विकलांग पेंशन के लिए क्या करना होगा", "viklang pension ke liye kya karna hoga"
    ]

    # Widow pension keywords
    widow_pension_keywords = [
        "विधवा पेंशन", "विधवा योजना", "सुखद सहारा", "तलाकशुदा पेंशन", 
        "परित्यक्ता पेंशन", "महिला पेंशन", "विधवा को पेंशन", "तलाकशुदा महिला पेंशन",
        "vidhva pension", "widow pension", "talakshuda pension", "abandoned women pension",
        "sukhad sahara", "mahila pension", "talakshuda mahila pension", "chhuti hui mahila pension",
        "इंदिरा गांधी विधवा पेंशन", "इंदिरा गांधी राष्ट्रीय विधवा पेंशन",
        "indira gandhi widow pension", "indira gandhi national widow pension",
        "मुख्यमंत्री पेंशन", "CM pension", "SECC pension", "मुख्यमंत्री योजना",
        "vidhva pensan", "widow pensan", "talakshuda pensan", 
        "vidhwa pensan", "vidhva penshan", "widow penshan",
        "vidhva pension yojna", "widow pension yojna", "talakshuda pension yojna",
        "विधवा पेंशन योजना", "तलाकशुदा पेंशन योजना"
    ]

    # Old Age pension keywords
    old_age_pension_keywords = [
        "बुजुर्ग पेंशन", "वृद्धावस्था पेंशन",  "वृद्ध पेंशन",
        "बूढ़े लोगों की पेंशन", "वृद्ध पेंशन योजना","वृद्ध पेंशन स्कीम", "60+ पेंशन","60 से ऊपर पेंशन", "60 साल वाली पेंशन","वृद्धावस्था पेंसन",
        "बुजुर्ग पेंसन","वृद्ध पेंसन के बारे में बताओ", "वृद्ध पेंशन के बारे में जानकारी","वृद्धावस्था पेंशन के बारे में बताओ", "वृद्धावस्था पेंसन के बारे में जानकारी",
        # ... (rest of old_age_pension_keywords from your original file)
    ]

    # Family Assistance keywords
    family_assistance_keywords = [
        "परिवार सहायता योजना", "राष्ट्रीय परिवार सहायता योजना",
        "परिवार सहायता", "मृत्यु सहायता", "मृत्यु सहायता योजना",
        "परिवार को पैसा", "मुखिया मृत्यु", "20000 सहायता",
         "मुखिया की मृत्यु", "मुखिया का निधन", "परिवार के मुखिया की मौत",
        "परिवार सहायता", "राष्ट्रीय परिवार सहायता योजना",
        "परिवार में मौत", "परिवार में निधन", "मुखिया की death",
        "परिवार के मुखिया", "मुखिया का देहांत", "परिवार का मुखिया",
        
        # Hinglish/English
        "family assistance", "family benefit", "national family benefit",
        "मृत्यु सहायता", "death assistance", "मौत पर सहायता",
        "मुखिया की मृत्यु हो गई", "मुखिया का स्वर्गवास",
        
        # Short forms
        "परिवार योजना", "मुखिया योजना", "death of head", "death of family head", "family head death",
        "परिवार के मुखिया की मृत्यु", "परिवार के मुखिया का निधन", "परिवार के मुखिया की मौत",
        "परिवार के मुखिया की death", "परिवार के मुखिया का death", "family head death", "family head demise",
        "परिवार के मुखिया की death", "family head death", "family head demise"

    ]

    # TG Card keywords
    tg_card_keywords = [
        "टीजी कार्ड", "tg card", "उभयलिंगी कार्ड", "ट्रांसजेंडर कार्ड",
        "थर्ड जेंडर कार्ड", "tg card kaise banega", "tg card banana hai",
        "transgender card", "third gender card", "tg identity card", "kinnar",
        "टीजी कार्ड कैसे बनेगा", "उभयलिंगी पहचान पत्र", "tg yojana", "sixer", "सिक्सर", 
        "छत्तीसगढ़ टीजी कार्ड", "छ.ग. टीजी कार्ड", "hijda", "हिजड़ा", "किन्नर कार्ड", "किन्नर पहचान पत्र", "किन्नर योजना",
        "किन्नर पेंशन", "किन्नर सहायता", "किन्नर योजना", "किन्नर कार्ड कैसे बनवाएं", "किन्नर कार्ड कैसे बनवाए", "किन्नर कार्ड कैसे बनवायें",
        "kinnar card", "kinnar pehchan patra", "kinnar yojana", "kinnar pension", "kinnar sahayata", 
        "kinnar card kaise banvaye", "kinnar card kaise banwaye",
        "how to get transgender card", "how to get tg card", "how to get third gender card", 
        "how to get kinnar card", "how to get hijda card"

    ]


    # Known questions
    known_questions = {
        "pension_how": ["पेंशन कैसे मिलेगी", "पेंशन कैसे मिलती है", "पेंशन के लिए क्या करना होगा", "pension kaise milegi"],
        "documents_needed": ["क्या दस्तावेज चाहिए", "दस्तावेज क्या हैं", "कागज क्या लगेंगे", "documents kya chahiye"],
        "apply_process": ["आवेदन कैसे करें", "कैसे आवेदन करें", "apply kaise kare", "form kaha milega"],
        "eligibility": ["कौन ले सकता है", "पात्रता क्या है", "किसे मिलेगी", "eligible kaun hai"],
        "benefits": ["क्या मिलता है", "लाभ क्या है", "कितना मिलता है", "kitna paisa milega"],
        "location": ["कहाँ जाना है", "कहाँ आवेदन करें", "office kahan hai", "kaha jana hai", "kahan apply kare"]
    }

    greeting_patterns = ["namaste", "नमस्ते", "हैलो", "नमस्कार", "जय श्री राम"]