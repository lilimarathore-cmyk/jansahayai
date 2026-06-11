// frontend/app/admin/schemes/add/page.tsx
"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

export default function AddSchemePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [activeTab, setActiveTab] = useState("basic");
  
  const [isCustomCategory, setIsCustomCategory] = useState(false);
  const [customCategory, setCustomCategory] = useState("");

  const [formData, setFormData] = useState({
    scheme_id: "",
    scheme_name_hi: "",
    scheme_name_en: "",
    scheme_name_hinglish: "",
    category: "",
    active: true,
    objective_hi: "",
    objective_en: "",
    objective_hinglish: "",
    short_answer_hi: "",
    short_answer_en: "",
    short_answer_hinglish: "",
    benefits_type: "monthly",
    benefits_amount: "",
    benefits_text_hi: "",
    benefits_text_en: "",
    benefits_text_hinglish: "",
    eligibility_rules_hi: [""],
    eligibility_rules_en: [""],
    eligibility_rules_hinglish: [""],
    documents_hi: [""],
    documents_en: [""],
    documents_hinglish: [""],
    application_mode: "offline",
    steps_hi: [""],
    steps_en: [""],
    steps_hinglish: [""],
    locations_hi: [""],
    locations_en: [""],
    locations_hinglish: [""],
    process_hi: [""],
    process_en: [""],
    process_hinglish: [""],
    faq_question_hi: [""],
    faq_question_en: [""],
    faq_question_hinglish: [""],
    faq_answer_hi: [""],
    faq_answer_en: [""],
    faq_answer_hinglish: [""],
    keywords: "",
    scheme_identity_keywords: "",
    followup_hi: [""],
    followup_en: [""],
    followup_hinglish: [""],
    pdf_link: "",
  });

  const tabs = [
    { id: "basic", name: "Basic", icon: "📝" },
    { id: "content", name: "Content", icon: "📄" },
    { id: "apply", name: "Apply", icon: "⚙️" },
    { id: "nlp", name: "NLP", icon: "🤖" },
  ];

  const currentStep = tabs.findIndex(t => t.id === activeTab) + 1;
  const totalSteps = tabs.length;

  useEffect(() => {
    // Only load saved data if it's from current session, not old submissions
    const savedData = localStorage.getItem("add_scheme_form_data");
    if (savedData) {
      try {
        const parsed = JSON.parse(savedData);
        // Don't load if scheme_id already exists (might be already submitted)
        if (!parsed.scheme_id || !parsed.scheme_id.match(/^cg_scheme_\d{3}$/)) {
          setFormData(parsed);
        }
      } catch (e) {}
    }
    const savedTab = localStorage.getItem("add_scheme_active_tab");
    if (savedTab) setActiveTab(savedTab);
  }, []);

  const updateFormData = (newData: Partial<typeof formData>) => {
    const updated = { ...formData, ...newData };
    setFormData(updated);
    localStorage.setItem("add_scheme_form_data", JSON.stringify(updated));
    if (Object.keys(fieldErrors).length > 0) {
      setFieldErrors({});
    }
    setErrorMessage("");
  };

  const updateActiveTab = (tab: string) => {
    setActiveTab(tab);
    localStorage.setItem("add_scheme_active_tab", tab);
    setFieldErrors({});
    setErrorMessage("");
  };

  // Validate only current tab
  const validateCurrentTab = () => {
    const errors: Record<string, string> = {};
    
    if (activeTab === "basic") {
      if (!formData.scheme_id.trim()) {
        errors.scheme_id = "Scheme ID is required";
      } else if (!formData.scheme_id.match(/^cg_scheme_\d{3}$/)) {
        errors.scheme_id = 'Format must be: cg_scheme_001, cg_scheme_002, etc.';
      }
      if (!formData.scheme_name_hi.trim()) {
        errors.scheme_name_hi = "Scheme Name (Hindi) is required";
      }
      if (!formData.scheme_name_en.trim()) {
        errors.scheme_name_en = "Scheme Name (English) is required";
      }
      if (!formData.category) {
        errors.category = "Please select a category";
      }
    }
    
    else if (activeTab === "content") {
      if (!formData.short_answer_hi.trim()) {
        errors.short_answer_hi = "Short Answer (Hindi) is required";
      }
    }
    
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleNext = () => {
    if (validateCurrentTab()) {
      const currentIndex = tabs.findIndex(t => t.id === activeTab);
      if (currentIndex < tabs.length - 1) {
        updateActiveTab(tabs[currentIndex + 1].id);
      }
    }
  };

  const resetForm = () => {
    setFormData({
      scheme_id: "",
      scheme_name_hi: "",
      scheme_name_en: "",
      scheme_name_hinglish: "",
      category: "",
      active: true,
      objective_hi: "",
      objective_en: "",
      objective_hinglish: "",
      short_answer_hi: "",
      short_answer_en: "",
      short_answer_hinglish: "",
      benefits_type: "monthly",
      benefits_amount: "",
      benefits_text_hi: "",
      benefits_text_en: "",
      benefits_text_hinglish: "",
      eligibility_rules_hi: [""],
      eligibility_rules_en: [""],
      eligibility_rules_hinglish: [""],
      documents_hi: [""],
      documents_en: [""],
      documents_hinglish: [""],
      application_mode: "offline",
      steps_hi: [""],
      steps_en: [""],
      steps_hinglish: [""],
      locations_hi: [""],
      locations_en: [""],
      locations_hinglish: [""],
      process_hi: [""],
      process_en: [""],
      process_hinglish: [""],
      faq_question_hi: [""],
      faq_question_en: [""],
      faq_question_hinglish: [""],
      faq_answer_hi: [""],
      faq_answer_en: [""],
      faq_answer_hinglish: [""],
      keywords: "",
      scheme_identity_keywords: "",
      followup_hi: [""],
      followup_en: [""],
      followup_hinglish: [""],
      pdf_link: "",
    });
    setIsCustomCategory(false);
    setCustomCategory("");
    setFieldErrors({});
    setErrorMessage("");
    setActiveTab("basic");
    localStorage.removeItem("add_scheme_form_data");
    localStorage.removeItem("add_scheme_active_tab");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage("");
    
    // Validate all tabs before submit
    const basicValid = (() => {
      if (!formData.scheme_id.trim()) return false;
      if (!formData.scheme_id.match(/^cg_scheme_\d{3}$/)) return false;
      if (!formData.scheme_name_hi.trim()) return false;
      if (!formData.scheme_name_en.trim()) return false;
      if (!formData.category) return false;
      return true;
    })();
    
    const contentValid = formData.short_answer_hi.trim() !== "";
    
    if (!basicValid) {
      setActiveTab("basic");
      setErrorMessage("Please fill all required fields in Basic tab");
      return;
    }
    
    if (!contentValid) {
      setActiveTab("content");
      setErrorMessage("Please fill Short Answer in Content tab");
      return;
    }
    
    setLoading(true);

    try {
      const schemeData = {
        scheme_id: formData.scheme_id,
        scheme_name: {
          hi: formData.scheme_name_hi,
          en: formData.scheme_name_en,
        },
        category: formData.category,
        active: formData.active,
        short_answer: formData.short_answer_hi,
        benefits: formData.benefits_text_hi || `₹${formData.benefits_amount} ${formData.benefits_type}`,
        documents: formData.documents_hi.filter(d => d.trim()),
        apply_steps: formData.steps_hi.filter(s => s.trim()),
        locations: formData.locations_hi.filter(l => l.trim()),
        keywords: formData.keywords.split(',').map(k => k.trim()).filter(k => k),
        eligibility_rules: formData.eligibility_rules_hi.filter(r => r.trim()).map((rule, idx) => ({
          field: `rule_${idx + 1}`,
          operator: "==",
          value: true,
          message: rule,
        })),
        pdf_link: formData.pdf_link || "",
        conversation_flow: null,
      };

      const response = await fetch("http://127.0.0.1:8000/admin/schemes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(schemeData),
      });

      if (response.ok) {
        alert("✅ Scheme added successfully!");
        resetForm();
      } else {
        let errorMsg = `Error ${response.status}: Failed to add scheme`;
        try {
          const errorData = await response.json();
          if (Array.isArray(errorData.detail)) {
            errorMsg = errorData.detail.map((err: any) => 
              `${err.loc?.join(" → ")}: ${err.msg}`
            ).join("\n");
          } else if (errorData.detail) {
            errorMsg = errorData.detail;
          }
        } catch {
          errorMsg = `Error ${response.status}: ${response.statusText}`;
        }
        setErrorMessage(errorMsg);
      }
    } catch (err: any) {
      console.error("Network error:", err);
      const errorMsg = "Network error: Please check if backend is running on http://127.0.0.1:8000";
      setErrorMessage(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  // Helper functions (all same as before)
  const updateEligibility = (idx: number, lang: string, value: string) => {
    if (lang === "hi") {
      const newArr = [...formData.eligibility_rules_hi];
      newArr[idx] = value;
      updateFormData({ eligibility_rules_hi: newArr });
    } else if (lang === "en") {
      const newArr = [...formData.eligibility_rules_en];
      newArr[idx] = value;
      updateFormData({ eligibility_rules_en: newArr });
    } else {
      const newArr = [...formData.eligibility_rules_hinglish];
      newArr[idx] = value;
      updateFormData({ eligibility_rules_hinglish: newArr });
    }
  };

  const addEligibility = () => {
    updateFormData({ 
      eligibility_rules_hi: [...formData.eligibility_rules_hi, ""],
      eligibility_rules_en: [...formData.eligibility_rules_en, ""],
      eligibility_rules_hinglish: [...formData.eligibility_rules_hinglish, ""]
    });
  };

  const removeEligibility = (idx: number) => {
    const hi = [...formData.eligibility_rules_hi];
    const en = [...formData.eligibility_rules_en];
    const hing = [...formData.eligibility_rules_hinglish];
    hi.splice(idx, 1); en.splice(idx, 1); hing.splice(idx, 1);
    updateFormData({ eligibility_rules_hi: hi, eligibility_rules_en: en, eligibility_rules_hinglish: hing });
  };

  const updateDocument = (idx: number, lang: string, value: string) => {
    if (lang === "hi") {
      const newArr = [...formData.documents_hi];
      newArr[idx] = value;
      updateFormData({ documents_hi: newArr });
    } else if (lang === "en") {
      const newArr = [...formData.documents_en];
      newArr[idx] = value;
      updateFormData({ documents_en: newArr });
    } else {
      const newArr = [...formData.documents_hinglish];
      newArr[idx] = value;
      updateFormData({ documents_hinglish: newArr });
    }
  };

  const addDocument = () => {
    updateFormData({ 
      documents_hi: [...formData.documents_hi, ""],
      documents_en: [...formData.documents_en, ""],
      documents_hinglish: [...formData.documents_hinglish, ""]
    });
  };

  const removeDocument = (idx: number) => {
    const hi = [...formData.documents_hi];
    const en = [...formData.documents_en];
    const hing = [...formData.documents_hinglish];
    hi.splice(idx, 1); en.splice(idx, 1); hing.splice(idx, 1);
    updateFormData({ documents_hi: hi, documents_en: en, documents_hinglish: hing });
  };

  const updateStep = (idx: number, lang: string, value: string) => {
    if (lang === "hi") {
      const newArr = [...formData.steps_hi];
      newArr[idx] = value;
      updateFormData({ steps_hi: newArr });
    } else if (lang === "en") {
      const newArr = [...formData.steps_en];
      newArr[idx] = value;
      updateFormData({ steps_en: newArr });
    } else {
      const newArr = [...formData.steps_hinglish];
      newArr[idx] = value;
      updateFormData({ steps_hinglish: newArr });
    }
  };

  const addStep = () => {
    updateFormData({ 
      steps_hi: [...formData.steps_hi, ""],
      steps_en: [...formData.steps_en, ""],
      steps_hinglish: [...formData.steps_hinglish, ""]
    });
  };

  const removeStep = (idx: number) => {
    const hi = [...formData.steps_hi];
    const en = [...formData.steps_en];
    const hing = [...formData.steps_hinglish];
    hi.splice(idx, 1); en.splice(idx, 1); hing.splice(idx, 1);
    updateFormData({ steps_hi: hi, steps_en: en, steps_hinglish: hing });
  };

  const updateLocation = (idx: number, lang: string, value: string) => {
    if (lang === "hi") {
      const newArr = [...formData.locations_hi];
      newArr[idx] = value;
      updateFormData({ locations_hi: newArr });
    } else if (lang === "en") {
      const newArr = [...formData.locations_en];
      newArr[idx] = value;
      updateFormData({ locations_en: newArr });
    } else {
      const newArr = [...formData.locations_hinglish];
      newArr[idx] = value;
      updateFormData({ locations_hinglish: newArr });
    }
  };

  const addLocation = () => {
    updateFormData({ 
      locations_hi: [...formData.locations_hi, ""],
      locations_en: [...formData.locations_en, ""],
      locations_hinglish: [...formData.locations_hinglish, ""]
    });
  };

  const removeLocation = (idx: number) => {
    const hi = [...formData.locations_hi];
    const en = [...formData.locations_en];
    const hing = [...formData.locations_hinglish];
    hi.splice(idx, 1); en.splice(idx, 1); hing.splice(idx, 1);
    updateFormData({ locations_hi: hi, locations_en: en, locations_hinglish: hing });
  };

  const updateProcess = (idx: number, lang: string, value: string) => {
    if (lang === "hi") {
      const newArr = [...formData.process_hi];
      newArr[idx] = value;
      updateFormData({ process_hi: newArr });
    } else if (lang === "en") {
      const newArr = [...formData.process_en];
      newArr[idx] = value;
      updateFormData({ process_en: newArr });
    } else {
      const newArr = [...formData.process_hinglish];
      newArr[idx] = value;
      updateFormData({ process_hinglish: newArr });
    }
  };

  const addProcess = () => {
    updateFormData({ 
      process_hi: [...formData.process_hi, ""],
      process_en: [...formData.process_en, ""],
      process_hinglish: [...formData.process_hinglish, ""]
    });
  };

  const removeProcess = (idx: number) => {
    const hi = [...formData.process_hi];
    const en = [...formData.process_en];
    const hing = [...formData.process_hinglish];
    hi.splice(idx, 1); en.splice(idx, 1); hing.splice(idx, 1);
    updateFormData({ process_hi: hi, process_en: en, process_hinglish: hing });
  };

  const updateFollowup = (idx: number, lang: string, value: string) => {
    if (lang === "hi") {
      const newArr = [...formData.followup_hi];
      newArr[idx] = value;
      updateFormData({ followup_hi: newArr });
    } else if (lang === "en") {
      const newArr = [...formData.followup_en];
      newArr[idx] = value;
      updateFormData({ followup_en: newArr });
    } else {
      const newArr = [...formData.followup_hinglish];
      newArr[idx] = value;
      updateFormData({ followup_hinglish: newArr });
    }
  };

  const addFollowup = () => {
    updateFormData({ 
      followup_hi: [...formData.followup_hi, ""],
      followup_en: [...formData.followup_en, ""],
      followup_hinglish: [...formData.followup_hinglish, ""]
    });
  };

  const removeFollowup = (idx: number) => {
    const hi = [...formData.followup_hi];
    const en = [...formData.followup_en];
    const hing = [...formData.followup_hinglish];
    hi.splice(idx, 1); en.splice(idx, 1); hing.splice(idx, 1);
    updateFormData({ followup_hi: hi, followup_en: en, followup_hinglish: hing });
  };

  const updateFaqQuestion = (idx: number, lang: string, value: string) => {
    if (lang === "hi") {
      const newArr = [...formData.faq_question_hi];
      newArr[idx] = value;
      updateFormData({ faq_question_hi: newArr });
    } else if (lang === "en") {
      const newArr = [...formData.faq_question_en];
      newArr[idx] = value;
      updateFormData({ faq_question_en: newArr });
    } else {
      const newArr = [...formData.faq_question_hinglish];
      newArr[idx] = value;
      updateFormData({ faq_question_hinglish: newArr });
    }
  };

  const updateFaqAnswer = (idx: number, lang: string, value: string) => {
    if (lang === "hi") {
      const newArr = [...formData.faq_answer_hi];
      newArr[idx] = value;
      updateFormData({ faq_answer_hi: newArr });
    } else if (lang === "en") {
      const newArr = [...formData.faq_answer_en];
      newArr[idx] = value;
      updateFormData({ faq_answer_en: newArr });
    } else {
      const newArr = [...formData.faq_answer_hinglish];
      newArr[idx] = value;
      updateFormData({ faq_answer_hinglish: newArr });
    }
  };

  const addFaq = () => {
    updateFormData({ 
      faq_question_hi: [...formData.faq_question_hi, ""],
      faq_question_en: [...formData.faq_question_en, ""],
      faq_question_hinglish: [...formData.faq_question_hinglish, ""],
      faq_answer_hi: [...formData.faq_answer_hi, ""],
      faq_answer_en: [...formData.faq_answer_en, ""],
      faq_answer_hinglish: [...formData.faq_answer_hinglish, ""]
    });
  };

  const removeFaq = (idx: number) => {
    const qHi = [...formData.faq_question_hi];
    const qEn = [...formData.faq_question_en];
    const qHing = [...formData.faq_question_hinglish];
    const aHi = [...formData.faq_answer_hi];
    const aEn = [...formData.faq_answer_en];
    const aHing = [...formData.faq_answer_hinglish];
    qHi.splice(idx, 1); qEn.splice(idx, 1); qHing.splice(idx, 1);
    aHi.splice(idx, 1); aEn.splice(idx, 1); aHing.splice(idx, 1);
    updateFormData({ 
      faq_question_hi: qHi, faq_question_en: qEn, faq_question_hinglish: qHing,
      faq_answer_hi: aHi, faq_answer_en: aEn, faq_answer_hinglish: aHing
    });
  };

  const renderRulesSection = () => (
    <div className="mb-5">
      <div className="flex justify-between items-center mb-2">
        <label className="block text-sm font-medium text-gray-700">Eligibility Rules</label>
        <button type="button" onClick={addEligibility} className="text-indigo-600 text-sm hover:text-indigo-700">+ Add Rule</button>
      </div>
      {formData.eligibility_rules_hi.map((_, idx) => (
        <div key={idx} className="flex gap-2 mb-2">
          <input type="text" value={formData.eligibility_rules_hi[idx] || ""} onChange={(e) => updateEligibility(idx, "hi", e.target.value)} placeholder="Hindi" className="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm" />
          <input type="text" value={formData.eligibility_rules_en[idx] || ""} onChange={(e) => updateEligibility(idx, "en", e.target.value)} placeholder="English" className="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm" />
          {formData.eligibility_rules_hi.length > 1 && (
            <button type="button" onClick={() => removeEligibility(idx)} className="text-red-500 px-2">✖</button>
          )}
        </div>
      ))}
    </div>
  );

  const renderDocumentsSection = () => (
    <div className="mb-5">
      <div className="flex justify-between items-center mb-2">
        <label className="block text-sm font-medium text-gray-700">Required Documents</label>
        <button type="button" onClick={addDocument} className="text-indigo-600 text-sm hover:text-indigo-700">+ Add Document</button>
      </div>
      {formData.documents_hi.map((_, idx) => (
        <div key={idx} className="flex gap-2 mb-2">
          <input type="text" value={formData.documents_hi[idx] || ""} onChange={(e) => updateDocument(idx, "hi", e.target.value)} placeholder="Hindi" className="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm" />
          <input type="text" value={formData.documents_en[idx] || ""} onChange={(e) => updateDocument(idx, "en", e.target.value)} placeholder="English" className="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm" />
          {formData.documents_hi.length > 1 && (
            <button type="button" onClick={() => removeDocument(idx)} className="text-red-500 px-2">✖</button>
          )}
        </div>
      ))}
    </div>
  );

  const renderStepsSection = () => (
    <div className="mb-5">
      <div className="flex justify-between items-center mb-2">
        <label className="block text-sm font-medium text-gray-700">Application Steps</label>
        <button type="button" onClick={addStep} className="text-indigo-600 text-sm hover:text-indigo-700">+ Add Step</button>
      </div>
      {formData.steps_hi.map((_, idx) => (
        <div key={idx} className="flex gap-2 mb-2">
          <input type="text" value={formData.steps_hi[idx] || ""} onChange={(e) => updateStep(idx, "hi", e.target.value)} placeholder="Hindi" className="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm" />
          <input type="text" value={formData.steps_en[idx] || ""} onChange={(e) => updateStep(idx, "en", e.target.value)} placeholder="English" className="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm" />
          {formData.steps_hi.length > 1 && (
            <button type="button" onClick={() => removeStep(idx)} className="text-red-500 px-2">✖</button>
          )}
        </div>
      ))}
    </div>
  );

  const renderLocationsSection = () => (
    <div className="mb-5">
      <div className="flex justify-between items-center mb-2">
        <label className="block text-sm font-medium text-gray-700">Application Locations</label>
        <button type="button" onClick={addLocation} className="text-indigo-600 text-sm hover:text-indigo-700">+ Add Location</button>
      </div>
      {formData.locations_hi.map((_, idx) => (
        <div key={idx} className="flex gap-2 mb-2">
          <input type="text" value={formData.locations_hi[idx] || ""} onChange={(e) => updateLocation(idx, "hi", e.target.value)} placeholder="Hindi" className="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm" />
          <input type="text" value={formData.locations_en[idx] || ""} onChange={(e) => updateLocation(idx, "en", e.target.value)} placeholder="English" className="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm" />
          {formData.locations_hi.length > 1 && (
            <button type="button" onClick={() => removeLocation(idx)} className="text-red-500 px-2">✖</button>
          )}
        </div>
      ))}
    </div>
  );

  const renderProcessSection = () => (
    <div className="mb-5">
      <div className="flex justify-between items-center mb-2">
        <label className="block text-sm font-medium text-gray-700">Process Flow</label>
        <button type="button" onClick={addProcess} className="text-indigo-600 text-sm hover:text-indigo-700">+ Add Step</button>
      </div>
      {formData.process_hi.map((_, idx) => (
        <div key={idx} className="flex gap-2 mb-2">
          <input type="text" value={formData.process_hi[idx] || ""} onChange={(e) => updateProcess(idx, "hi", e.target.value)} placeholder="Hindi" className="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm" />
          <input type="text" value={formData.process_en[idx] || ""} onChange={(e) => updateProcess(idx, "en", e.target.value)} placeholder="English" className="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm" />
          {formData.process_hi.length > 1 && (
            <button type="button" onClick={() => removeProcess(idx)} className="text-red-500 px-2">✖</button>
          )}
        </div>
      ))}
    </div>
  );

  const renderFollowupSection = () => (
    <div className="mb-5">
      <div className="flex justify-between items-center mb-2">
        <label className="block text-sm font-medium text-gray-700">Follow-up Questions</label>
        <button type="button" onClick={addFollowup} className="text-indigo-600 text-sm hover:text-indigo-700">+ Add Question</button>
      </div>
      {formData.followup_hi.map((_, idx) => (
        <div key={idx} className="flex gap-2 mb-2">
          <input type="text" value={formData.followup_hi[idx] || ""} onChange={(e) => updateFollowup(idx, "hi", e.target.value)} placeholder="Hindi" className="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm" />
          <input type="text" value={formData.followup_en[idx] || ""} onChange={(e) => updateFollowup(idx, "en", e.target.value)} placeholder="English" className="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm" />
          {formData.followup_hi.length > 1 && (
            <button type="button" onClick={() => removeFollowup(idx)} className="text-red-500 px-2">✖</button>
          )}
        </div>
      ))}
    </div>
  );

  const renderFaqSection = () => (
    <div className="mb-5">
      <div className="flex justify-between items-center mb-2">
        <label className="block text-sm font-medium text-gray-700">FAQ</label>
        <button type="button" onClick={addFaq} className="text-indigo-600 text-sm hover:text-indigo-700">+ Add FAQ</button>
      </div>
      {formData.faq_question_hi.map((_, idx) => (
        <div key={idx} className="p-3 bg-gray-50 rounded-lg mb-2">
          <div className="flex justify-between mb-1">
            <span className="text-xs font-medium text-gray-500">FAQ {idx + 1}</span>
            {formData.faq_question_hi.length > 1 && (
              <button type="button" onClick={() => removeFaq(idx)} className="text-red-500 text-xs">Remove</button>
            )}
          </div>
          <input type="text" value={formData.faq_question_hi[idx] || ""} onChange={(e) => updateFaqQuestion(idx, "hi", e.target.value)} placeholder="Question (Hindi)" className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm mb-2" />
          <input type="text" value={formData.faq_question_en[idx] || ""} onChange={(e) => updateFaqQuestion(idx, "en", e.target.value)} placeholder="Question (English)" className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm mb-2" />
          <textarea value={formData.faq_answer_hi[idx] || ""} onChange={(e) => updateFaqAnswer(idx, "hi", e.target.value)} rows={2} placeholder="Answer (Hindi)" className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm mb-2" />
          <textarea value={formData.faq_answer_en[idx] || ""} onChange={(e) => updateFaqAnswer(idx, "en", e.target.value)} rows={2} placeholder="Answer (English)" className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" />
        </div>
      ))}
    </div>
  );

  const categoryOptions = [
    { value: "divyang_pension", icon: "🦽", label: "Divyang Pension", labelHi: "दिव्यांग पेंशन" },
    { value: "women_pension", icon: "👩", label: "Women Pension", labelHi: "महिला पेंशन" },
    { value: "widow_pension", icon: "👩‍🦳", label: "Widow Pension", labelHi: "विधवा पेंशन" },
    { value: "general_pension", icon: "👥", label: "General Pension", labelHi: "सामान्य पेंशन" },
    { value: "old_age_pension", icon: "👴", label: "Old Age Pension", labelHi: "वृद्धावस्था पेंशन" },
    { value: "family_assistance", icon: "👨‍👩‍👧", label: "Family Assistance", labelHi: "परिवार सहायता" },
    { value: "scholarship", icon: "🎓", label: "Scholarship", labelHi: "छात्रवृत्ति" },
    { value: "assistive_devices", icon: "🦻", label: "Assistive Devices", labelHi: "सहायक उपकरण" },
    { value: "marriage_incentive", icon: "💒", label: "Marriage Incentive", labelHi: "विवाह प्रोत्साहन" },
    { value: "civil_services", icon: "⚖️", label: "Civil Services", labelHi: "सिविल सेवा" },
    { value: "hostel", icon: "🏘️", label: "Hostel", labelHi: "छात्रावास" },
    { value: "camp", icon: "🏕️", label: "Camp", labelHi: "शिविर" },
    { value: "rehabilitation", icon: "🩺", label: "Rehabilitation", labelHi: "पुनर्वास" },
    { value: "tg_card", icon: "🆔", label: "TG Card", labelHi: "टीजी कार्ड" },
  ];

  const ErrorIcon = () => (
    <svg className="w-3.5 h-3.5 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
    </svg>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="max-w-4xl mx-auto px-4 py-6">
        
        {/* Global Error Message */}
        {errorMessage && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl flex items-start gap-2">
            <ErrorIcon />
            <p className="text-red-700 text-sm">{errorMessage}</p>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {/* Progress Tabs */}
          <div className="mb-8">
            <div className="flex items-center justify-between">
              {tabs.map((tab, idx) => (
                <React.Fragment key={tab.id}>
                  <button
                    type="button"
                    onClick={() => {
                      if (idx <= tabs.findIndex(t => t.id === activeTab)) {
                        updateActiveTab(tab.id);
                      }
                    }}
                    className={`flex flex-col items-center group focus:outline-none ${
                      idx > tabs.findIndex(t => t.id === activeTab) ? 'opacity-50 cursor-not-allowed' : ''
                    }`}
                    disabled={idx > tabs.findIndex(t => t.id === activeTab)}
                  >
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center text-lg transition-all ${
                      activeTab === tab.id
                        ? "bg-indigo-600 text-white shadow-md ring-4 ring-indigo-200"
                        : idx < tabs.findIndex(t => t.id === activeTab)
                        ? "bg-green-500 text-white"
                        : "bg-gray-200 text-gray-500"
                    }`}>
                      {idx < tabs.findIndex(t => t.id === activeTab) ? "✓" : tab.icon}
                    </div>
                    <span className={`text-xs font-medium mt-2 ${
                      activeTab === tab.id ? "text-indigo-600" : "text-gray-500"
                    }`}>
                      {tab.name}
                    </span>
                  </button>
                  {idx < tabs.length - 1 && (
                    <div className={`flex-1 h-0.5 mx-2 rounded ${
                      idx < tabs.findIndex(t => t.id === activeTab) 
                        ? "bg-green-500" 
                        : "bg-gray-200"
                    }`} />
                  )}
                </React.Fragment>
              ))}
            </div>
            <div className="text-center mt-3">
              <span className="text-xs text-gray-400">Step {currentStep} of {totalSteps}</span>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 md:p-8">
            
            {activeTab === "basic" && (
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">
                    Scheme ID <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={formData.scheme_id}
                    onChange={(e) => updateFormData({ scheme_id: e.target.value })}
                    placeholder="cg_scheme_017"
                    className={`w-full px-4 py-2.5 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all ${
                      fieldErrors.scheme_id 
                        ? 'border-2 border-red-500 bg-red-50 ring-1 ring-red-500' 
                        : 'border border-gray-300 hover:border-indigo-300 focus:border-indigo-500'
                    }`}
                  />
                  {fieldErrors.scheme_id && (
                    <div className="mt-1.5 flex items-start gap-1.5 text-red-600">
                      <ErrorIcon />
                      <span className="text-xs font-medium">{fieldErrors.scheme_id}</span>
                    </div>
                  )}
                  <p className="text-gray-400 text-xs mt-1.5">
                    Format: cg_scheme_001, cg_scheme_002, cg_scheme_003...
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">
                      Scheme Name <span className="text-red-500">*</span> <span className="text-xs text-gray-400">(Hindi)</span>
                    </label>
                    <input
                      type="text"
                      value={formData.scheme_name_hi}
                      onChange={(e) => updateFormData({ scheme_name_hi: e.target.value })}
                      placeholder="हिंदी में नाम"
                      className={`w-full px-4 py-2.5 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all ${
                        fieldErrors.scheme_name_hi 
                          ? 'border-2 border-red-500 bg-red-50 ring-1 ring-red-500' 
                          : 'border border-gray-300 hover:border-indigo-300 focus:border-indigo-500'
                      }`}
                    />
                    {fieldErrors.scheme_name_hi && (
                      <div className="mt-1.5 flex items-start gap-1.5 text-red-600">
                        <ErrorIcon />
                        <span className="text-xs font-medium">{fieldErrors.scheme_name_hi}</span>
                      </div>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">
                      Scheme Name <span className="text-red-500">*</span> <span className="text-xs text-gray-400">(English)</span>
                    </label>
                    <input
                      type="text"
                      value={formData.scheme_name_en}
                      onChange={(e) => updateFormData({ scheme_name_en: e.target.value })}
                      placeholder="English name"
                      className={`w-full px-4 py-2.5 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all ${
                        fieldErrors.scheme_name_en 
                          ? 'border-2 border-red-500 bg-red-50 ring-1 ring-red-500' 
                          : 'border border-gray-300 hover:border-indigo-300 focus:border-indigo-500'
                      }`}
                    />
                    {fieldErrors.scheme_name_en && (
                      <div className="mt-1.5 flex items-start gap-1.5 text-red-600">
                        <ErrorIcon />
                        <span className="text-xs font-medium">{fieldErrors.scheme_name_en}</span>
                      </div>
                    )}
                  </div>

                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">
                      Scheme Name <span className="text-xs text-gray-400">(Hinglish - Optional)</span>
                    </label>
                    <input
                      type="text"
                      value={formData.scheme_name_hinglish}
                      onChange={(e) => updateFormData({ scheme_name_hinglish: e.target.value })}
                      placeholder="Hinglish mein naam"
                      className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent hover:border-indigo-300"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">
                    Category <span className="text-red-500">*</span>
                  </label>
                  
                  {!isCustomCategory ? (
                    <div className="relative">
                      <select
                        value={formData.category}
                        onChange={(e) => {
                          if (e.target.value === "custom") {
                            setIsCustomCategory(true);
                            setFormData({ ...formData, category: "" });
                          } else {
                            setFormData({ ...formData, category: e.target.value });
                            if (fieldErrors.category) {
                              setFieldErrors({ ...fieldErrors, category: "" });
                            }
                          }
                        }}
                        className={`w-full px-4 py-2.5 rounded-lg appearance-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white cursor-pointer ${
                          fieldErrors.category 
                            ? 'border-2 border-red-500 bg-red-50 ring-1 ring-red-500' 
                            : 'border border-gray-300'
                        }`}
                      >
                        <option value="">-- Select Category --</option>
                        {categoryOptions.map((cat) => (
                          <option key={cat.value} value={cat.value}>
                            {cat.icon} {cat.label} ({cat.labelHi})
                          </option>
                        ))}
                        <option value="custom" className="border-t border-gray-200 mt-1 pt-1">✨ Custom Category</option>
                      </select>
                      <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
                        <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      <div className="flex gap-2">
                        <input
                          type="text"
                          value={customCategory}
                          onChange={(e) => {
                            const val = e.target.value.toLowerCase().replace(/\s+/g, '_');
                            setCustomCategory(val);
                            setFormData({ ...formData, category: val });
                            if (fieldErrors.category) {
                              setFieldErrors({ ...fieldErrors, category: "" });
                            }
                          }}
                          placeholder="e.g., healthcare_scheme, education_special"
                          className="flex-1 px-4 py-2.5 border border-indigo-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                          autoFocus
                        />
                        <button
                          type="button"
                          onClick={() => {
                            setIsCustomCategory(false);
                            setCustomCategory("");
                            setFormData({ ...formData, category: "" });
                          }}
                          className="px-4 py-2.5 bg-gray-100 rounded-lg hover:bg-gray-200 transition text-sm font-medium"
                        >
                          Cancel
                        </button>
                      </div>
                      <div className="p-3 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg border border-indigo-200">
                        <p className="text-sm text-indigo-700">
                          ✨ <span className="font-medium">Custom Category:</span> {customCategory || "category_name"}
                        </p>
                        <p className="text-xs text-indigo-600 mt-1">
                          Use lowercase letters and underscores (e.g., "healthcare", "education_special")
                        </p>
                      </div>
                    </div>
                  )}
                  
                  {fieldErrors.category && (
                    <div className="mt-1.5 flex items-start gap-1.5 text-red-600">
                      <ErrorIcon />
                      <span className="text-xs font-medium">{fieldErrors.category}</span>
                    </div>
                  )}
                </div>

                <div className="flex items-center gap-3 pt-2">
                  <input
                    type="checkbox"
                    id="active"
                    checked={formData.active}
                    onChange={(e) => updateFormData({ active: e.target.checked })}
                    className="w-4 h-4 text-indigo-600 rounded border-gray-300 focus:ring-indigo-500"
                  />
                  <label htmlFor="active" className="text-sm text-gray-700">Active (visible to users)</label>
                </div>
              </div>
            )}

            {activeTab === "content" && (
              <div className="space-y-5">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">Objective</label>
                  <textarea value={formData.objective_hi} onChange={(e) => updateFormData({ objective_hi: e.target.value })} rows={2} placeholder="Hindi - योजना का उद्देश्य" className="w-full px-4 py-2.5 border border-gray-300 rounded-lg mb-2" />
                  <textarea value={formData.objective_en} onChange={(e) => updateFormData({ objective_en: e.target.value })} rows={2} placeholder="English - Objective" className="w-full px-4 py-2.5 border border-gray-300 rounded-lg mb-2" />
                  <textarea value={formData.objective_hinglish} onChange={(e) => updateFormData({ objective_hinglish: e.target.value })} rows={2} placeholder="Hinglish - Uddeshya" className="w-full px-4 py-2.5 border border-gray-300 rounded-lg" />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">
                    Short Answer <span className="text-red-500">*</span>
                  </label>
                  <textarea 
                    value={formData.short_answer_hi} 
                    onChange={(e) => updateFormData({ short_answer_hi: e.target.value })} 
                    rows={2} 
                    placeholder="Short description in Hindi" 
                    className={`w-full px-4 py-2.5 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all ${
                      fieldErrors.short_answer_hi 
                        ? 'border-2 border-red-500 bg-red-50 ring-1 ring-red-500' 
                        : 'border border-gray-300'
                    }`}
                  />
                  {fieldErrors.short_answer_hi && (
                    <div className="mt-1.5 flex items-start gap-1.5 text-red-600">
                      <ErrorIcon />
                      <span className="text-xs font-medium">{fieldErrors.short_answer_hi}</span>
                    </div>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">Benefits</label>
                  <div className="grid grid-cols-2 gap-3 mb-2">
                    <select value={formData.benefits_type} onChange={(e) => updateFormData({ benefits_type: e.target.value })} className="px-4 py-2.5 border border-gray-300 rounded-lg">
                      <option value="monthly">Monthly</option>
                      <option value="one_time">One Time</option>
                      <option value="service">Service</option>
                    </select>
                    <input type="number" value={formData.benefits_amount} onChange={(e) => updateFormData({ benefits_amount: e.target.value })} placeholder="Amount (₹)" className="px-4 py-2.5 border border-gray-300 rounded-lg" />
                  </div>
                  <textarea value={formData.benefits_text_hi} onChange={(e) => updateFormData({ benefits_text_hi: e.target.value })} rows={2} placeholder="Benefits description (Hindi)" className="w-full px-4 py-2.5 border border-gray-300 rounded-lg" />
                </div>
              </div>
            )}

            {activeTab === "apply" && (
              <div>
                {renderRulesSection()}
                {renderDocumentsSection()}
                <div className="mb-5">
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">Application Mode</label>
                  <select value={formData.application_mode} onChange={(e) => updateFormData({ application_mode: e.target.value })} className="w-full px-4 py-2.5 border border-gray-300 rounded-lg">
                    <option value="offline">Offline</option>
                    <option value="online">Online</option>
                    <option value="both">Both</option>
                  </select>
                </div>
                {renderStepsSection()}
                {renderLocationsSection()}
                {renderProcessSection()}
                {renderFaqSection()}
              </div>
            )}

            {activeTab === "nlp" && (
              <div className="space-y-5">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">Search Keywords</label>
                  <input type="text" value={formData.keywords} onChange={(e) => updateFormData({ keywords: e.target.value })} placeholder="divyang, pension, सहायता" className="w-full px-4 py-2.5 border border-gray-300 rounded-lg" />
                  <p className="text-xs text-gray-400 mt-1">Separate keywords with commas</p>
                </div>
                {renderFollowupSection()}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">PDF Form Link</label>
                  <input type="text" value={formData.pdf_link} onChange={(e) => updateFormData({ pdf_link: e.target.value })} placeholder="/forms/cg_scheme_017.pdf" className="w-full px-4 py-2.5 border border-gray-300 rounded-lg" />
                </div>
              </div>
            )}
          </div>

          {/* ========== BUTTONS ========== */}
          <div className="flex justify-between mt-6">
            <button
              type="button"
              onClick={() => {
                const currentIndex = tabs.findIndex(t => t.id === activeTab);
                if (activeTab === "basic") {
                  router.push("/admin/schemes");
                } else {
                  updateActiveTab(tabs[currentIndex - 1].id);
                }
              }}
              className="px-6 py-2.5 border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50 transition"
            >
              ← Previous
            </button>
            
            {activeTab !== "nlp" ? (
              <button
                type="button"
                onClick={handleNext}
                className="px-6 py-2.5 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition shadow-sm"
              >
                Next →
              </button>
            ) : (
              <button
                type="submit"
                disabled={loading}
                className="px-6 py-2.5 bg-emerald-600 text-white rounded-lg font-medium hover:bg-emerald-700 transition shadow-sm disabled:opacity-50"
              >
                {loading ? "Creating..." : "✓ Create Scheme"}
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}