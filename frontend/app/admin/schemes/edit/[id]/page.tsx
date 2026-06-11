// frontend/app/admin/schemes/edit/[id]/page.tsx
"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import Link from "next/link";
import { getSchemeById, updateScheme, Scheme } from "@/services/adminApi";

export default function EditSchemePage() {
  const router = useRouter();
  const params = useParams();
  const schemeId = params.id as string;
  
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [categories, setCategories] = useState<any[]>([]);
  const [formData, setFormData] = useState<Partial<Scheme>>({
    scheme_id: "",
    scheme_name: { hi: "", en: "" },
    category: "",
    short_answer: "",
    benefits: "",
    documents: [],
    apply_steps: [],
    locations: [],
    pdf_link: "",
    keywords: [],
    active: true,
  });

  useEffect(() => {
    fetchScheme();
    fetchCategories();
  }, []);

  const fetchScheme = async () => {
    try {
      setLoading(true);
      const data = await getSchemeById(schemeId);
      setFormData({
        ...data,
        documents: data.documents || [],
        apply_steps: data.apply_steps || [],
        locations: data.locations || [],
        keywords: data.keywords || [],
      });
    } catch (error) {
      console.error("Error fetching scheme:", error);
      alert("Failed to fetch scheme details");
      router.push("/admin/schemes");
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/admin/categories");
      const data = await response.json();
      setCategories(data);
    } catch (error) {
      console.error("Error fetching categories:", error);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    
    if (name.includes(".")) {
      const [parent, child] = name.split(".");
      setFormData((prev) => ({
        ...prev,
        [parent]: {
          ...(prev[parent as keyof typeof prev] as { hi: string; en: string }),
          [child]: value,
        },
      }));
    } else {
      setFormData((prev) => ({ ...prev, [name]: value }));
    }
  };

  const handleArrayChange = (field: keyof Scheme, index: number, value: string) => {
    const currentArray = formData[field] as string[] || [];
    const newArray = [...currentArray];
    newArray[index] = value;
    setFormData((prev) => ({ ...prev, [field]: newArray }));
  };

  const addArrayItem = (field: keyof Scheme) => {
    const currentArray = formData[field] as string[] || [];
    setFormData((prev) => ({ ...prev, [field]: [...currentArray, ""] }));
  };

  const removeArrayItem = (field: keyof Scheme, index: number) => {
    const currentArray = formData[field] as string[] || [];
    const newArray = [...currentArray];
    newArray.splice(index, 1);
    setFormData((prev) => ({ ...prev, [field]: newArray }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const cleanedData: Partial<Scheme> = {
      ...formData,
      documents: (formData.documents || []).filter((d) => d && d.trim()),
      apply_steps: (formData.apply_steps || []).filter((s) => s && s.trim()),
      locations: (formData.locations || []).filter((l) => l && l.trim()),
      keywords: (formData.keywords || []).filter((k) => k && k.trim()),
    };

    setSubmitting(true);
    try {
      await updateScheme(schemeId, cleanedData);
      alert("✅ Scheme updated successfully!");
      router.push("/admin/schemes");
    } catch (error: any) {
      console.error("Error updating scheme:", error);
      alert(error.message || "❌ Failed to update scheme");
    } finally {
      setSubmitting(false);
    }
  };

  const documentsArray = formData.documents || [];
  const applyStepsArray = formData.apply_steps || [];
  const locationsArray = formData.locations || [];
  const keywordsArray = formData.keywords || [];

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-96">
        <div className="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
        <p className="mt-4 text-gray-500 dark:text-gray-400">Loading scheme details...</p>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <div className="w-10 h-10 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-xl flex items-center justify-center shadow-md">
              <span className="text-white text-xl">✏️</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-800 dark:text-white">Edit Scheme</h1>
              <p className="text-gray-500 dark:text-gray-400 text-sm">Update scheme details and information</p>
            </div>
          </div>
        </div>
        <Link
          href="/admin/schemes"
          className="inline-flex items-center gap-2 px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-white transition-colors bg-gray-100 dark:bg-slate-800 rounded-lg hover:bg-gray-200 dark:hover:bg-slate-700"
        >
          ← Back to Schemes
        </Link>
      </div>

      {/* Form Card */}
      <form onSubmit={handleSubmit} className="bg-white dark:bg-slate-800 rounded-2xl shadow-lg border border-gray-200 dark:border-slate-700 overflow-hidden">
        {/* Form Header */}
        <div className="bg-gradient-to-r from-emerald-50 to-teal-50 dark:from-emerald-950/30 dark:to-teal-950/30 px-6 py-4 border-b border-gray-200 dark:border-slate-700">
          <div className="flex items-center gap-2">
            <span className="text-emerald-600 dark:text-emerald-400">✏️</span>
            <h2 className="font-semibold text-gray-800 dark:text-white">Editing: {formData.scheme_id}</h2>
          </div>
        </div>

        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Scheme ID (Read-only) */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Scheme ID
              </label>
              <div className="relative">
                <input
                  type="text"
                  value={formData.scheme_id || ""}
                  disabled
                  className="w-full px-4 py-2.5 border border-gray-300 dark:border-slate-600 rounded-xl bg-gray-50 dark:bg-slate-900 text-gray-500 dark:text-gray-400 cursor-not-allowed"
                />
                <div className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400">🔒</div>
              </div>
            </div>

            {/* Category */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Category <span className="text-red-500">*</span>
              </label>
              <select
                name="category"
                value={formData.category || ""}
                onChange={handleChange}
                required
                className="w-full px-4 py-2.5 border border-gray-300 dark:border-slate-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent dark:bg-slate-900 dark:text-white transition-all"
              >
                <option value="">Select Category</option>
                {categories.map((cat) => (
                  <option key={cat.id} value={cat.id}>
                    {cat.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Scheme Name Hindi */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Scheme Name (Hindi) <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                name="scheme_name.hi"
                value={formData.scheme_name?.hi || ""}
                onChange={handleChange}
                required
                className="w-full px-4 py-2.5 border border-gray-300 dark:border-slate-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent dark:bg-slate-900 dark:text-white transition-all"
              />
            </div>

            {/* Scheme Name English */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Scheme Name (English) <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                name="scheme_name.en"
                value={formData.scheme_name?.en || ""}
                onChange={handleChange}
                required
                className="w-full px-4 py-2.5 border border-gray-300 dark:border-slate-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent dark:bg-slate-900 dark:text-white transition-all"
              />
            </div>

            {/* Short Answer */}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Short Answer / Description <span className="text-red-500">*</span>
              </label>
              <textarea
                name="short_answer"
                value={formData.short_answer || ""}
                onChange={handleChange}
                required
                rows={3}
                className="w-full px-4 py-2.5 border border-gray-300 dark:border-slate-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent dark:bg-slate-900 dark:text-white transition-all resize-none"
              />
            </div>

            {/* Benefits */}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Benefits <span className="text-red-500">*</span>
              </label>
              <textarea
                name="benefits"
                value={formData.benefits || ""}
                onChange={handleChange}
                required
                rows={3}
                className="w-full px-4 py-2.5 border border-gray-300 dark:border-slate-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent dark:bg-slate-900 dark:text-white transition-all resize-none"
              />
            </div>

            {/* Documents Section */}
            <div className="md:col-span-2">
              <div className="flex items-center justify-between mb-3">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  📄 Required Documents
                </label>
                <button
                  type="button"
                  onClick={() => addArrayItem("documents")}
                  className="text-sm text-emerald-600 dark:text-emerald-400 hover:text-emerald-700 flex items-center gap-1"
                >
                  + Add Document
                </button>
              </div>
              <div className="space-y-2">
                {(documentsArray.length === 0 ? [""] : documentsArray).map((doc, index) => (
                  <div key={index} className="flex gap-2">
                    <input
                      type="text"
                      value={doc || ""}
                      onChange={(e) => handleArrayChange("documents", index, e.target.value)}
                      placeholder={`Document ${index + 1}`}
                      className="flex-1 px-4 py-2.5 border border-gray-300 dark:border-slate-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent dark:bg-slate-900 dark:text-white transition-all"
                    />
                    <button
                      type="button"
                      onClick={() => removeArrayItem("documents", index)}
                      className="px-3 py-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-950/30 rounded-lg transition-colors"
                    >
                      🗑️
                    </button>
                  </div>
                ))}
              </div>
            </div>

            {/* Apply Steps Section */}
            <div className="md:col-span-2">
              <div className="flex items-center justify-between mb-3">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  📋 Application Steps
                </label>
                <button
                  type="button"
                  onClick={() => addArrayItem("apply_steps")}
                  className="text-sm text-emerald-600 dark:text-emerald-400 hover:text-emerald-700 flex items-center gap-1"
                >
                  + Add Step
                </button>
              </div>
              <div className="space-y-2">
                {(applyStepsArray.length === 0 ? [""] : applyStepsArray).map((step, index) => (
                  <div key={index} className="flex gap-2">
                    <div className="flex items-center justify-center w-8 h-10 bg-emerald-100 dark:bg-emerald-900/30 rounded-lg text-emerald-600 dark:text-emerald-400 font-semibold text-sm">
                      {index + 1}
                    </div>
                    <input
                      type="text"
                      value={step || ""}
                      onChange={(e) => handleArrayChange("apply_steps", index, e.target.value)}
                      placeholder={`Step ${index + 1}`}
                      className="flex-1 px-4 py-2.5 border border-gray-300 dark:border-slate-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent dark:bg-slate-900 dark:text-white transition-all"
                    />
                    <button
                      type="button"
                      onClick={() => removeArrayItem("apply_steps", index)}
                      className="px-3 py-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-950/30 rounded-lg transition-colors"
                    >
                      🗑️
                    </button>
                  </div>
                ))}
              </div>
            </div>

            {/* Locations Section */}
            <div className="md:col-span-2">
              <div className="flex items-center justify-between mb-3">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  📍 Application Locations
                </label>
                <button
                  type="button"
                  onClick={() => addArrayItem("locations")}
                  className="text-sm text-emerald-600 dark:text-emerald-400 hover:text-emerald-700 flex items-center gap-1"
                >
                  + Add Location
                </button>
              </div>
              <div className="space-y-2">
                {(locationsArray.length === 0 ? [""] : locationsArray).map((location, index) => (
                  <div key={index} className="flex gap-2">
                    <input
                      type="text"
                      value={location || ""}
                      onChange={(e) => handleArrayChange("locations", index, e.target.value)}
                      placeholder={`Location ${index + 1}`}
                      className="flex-1 px-4 py-2.5 border border-gray-300 dark:border-slate-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent dark:bg-slate-900 dark:text-white transition-all"
                    />
                    <button
                      type="button"
                      onClick={() => removeArrayItem("locations", index)}
                      className="px-3 py-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-950/30 rounded-lg transition-colors"
                    >
                      🗑️
                    </button>
                  </div>
                ))}
              </div>
            </div>

            {/* PDF Link */}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                📎 PDF Download Link
              </label>
              <input
                type="text"
                name="pdf_link"
                value={formData.pdf_link || ""}
                onChange={handleChange}
                placeholder="/forms/cg_scheme_017.pdf"
                className="w-full px-4 py-2.5 border border-gray-300 dark:border-slate-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent dark:bg-slate-900 dark:text-white transition-all"
              />
            </div>

            {/* Keywords Section */}
            <div className="md:col-span-2">
              <div className="flex items-center justify-between mb-3">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  🔑 Search Keywords
                </label>
                <button
                  type="button"
                  onClick={() => addArrayItem("keywords")}
                  className="text-sm text-emerald-600 dark:text-emerald-400 hover:text-emerald-700 flex items-center gap-1"
                >
                  + Add Keyword
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {(keywordsArray.length === 0 ? [""] : keywordsArray).map((keyword, index) => (
                  <div key={index} className="flex items-center gap-1 bg-gray-100 dark:bg-slate-700 rounded-full px-3 py-1">
                    <input
                      type="text"
                      value={keyword || ""}
                      onChange={(e) => handleArrayChange("keywords", index, e.target.value)}
                      placeholder={`Keyword ${index + 1}`}
                      className="bg-transparent px-2 py-1 text-sm focus:outline-none dark:text-white w-24"
                    />
                    <button
                      type="button"
                      onClick={() => removeArrayItem("keywords", index)}
                      className="text-red-500 hover:text-red-700 text-xs"
                    >
                      ✕
                    </button>
                  </div>
                ))}
              </div>
            </div>

            {/* Active Status Toggle */}
            <div className="md:col-span-2">
              <label className="flex items-center gap-3 cursor-pointer">
                <div className="relative">
                  <input
                    type="checkbox"
                    checked={formData.active || false}
                    onChange={(e) => setFormData((prev) => ({ ...prev, active: e.target.checked }))}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-300 dark:bg-slate-600 rounded-full peer peer-checked:bg-emerald-600 transition-all duration-300"></div>
                  <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-all duration-300 peer-checked:translate-x-5"></div>
                </div>
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  {formData.active ? "✅ Active (visible to users)" : "⭕ Inactive (hidden from users)"}
                </span>
              </label>
            </div>
          </div>
        </div>

        {/* Form Actions */}
        <div className="bg-gray-50 dark:bg-slate-900/50 px-6 py-4 border-t border-gray-200 dark:border-slate-700 flex justify-end gap-3">
          <Link
            href="/admin/schemes"
            className="px-5 py-2.5 border border-gray-300 dark:border-slate-600 rounded-xl text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-slate-700 transition-all duration-200"
          >
            Cancel
          </Link>
          <button
            type="submit"
            disabled={submitting}
            className="px-6 py-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 text-white rounded-xl font-medium hover:from-emerald-700 hover:to-teal-700 transition-all duration-200 disabled:opacity-50 shadow-md flex items-center gap-2"
          >
            {submitting ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Saving...
              </>
            ) : (
              <>
                💾 Save Changes
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}