// frontend/app/admin/schemes/page.tsx
"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { 
  Search, 
  Edit, 
  Trash2, 
  Plus,
  FolderOpen,
  CheckCircle,
  AlertCircle,
  TrendingUp,
  Filter,
  X,
  RefreshCw,
  Trash
} from "lucide-react";

interface Scheme {
  _id?: string;
  scheme_id: string;
  scheme_name: { hi: string; en: string };
  category: string;
  active: boolean;
  applications?: number;
  budget?: string;
}

export default function SchemeManagementPage() {
  const [schemes, setSchemes] = useState<Scheme[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [showInactive, setShowInactive] = useState(false);
  const [categories, setCategories] = useState<{ id: string; name: string }[]>([]);

  useEffect(() => {
    fetchSchemes();
    fetchCategories();
  }, []);

  const fetchSchemes = async () => {
    try {
      setLoading(true);
      const response = await fetch("http://127.0.0.1:8000/admin/schemes");
      const data = await response.json();
      setSchemes(data);
    } catch (error) {
      console.error("Error fetching schemes:", error);
      setSchemes([
        { scheme_id: "CG001", scheme_name: { hi: "पीएम किसान सम्मान निधि", en: "PM Kisan Samman Nidhi" }, category: "Agriculture", active: true, applications: 12450, budget: "₹60,000 Cr" },
        { scheme_id: "CG002", scheme_name: { hi: "आयुष्मान भारत", en: "Ayushman Bharat" }, category: "Healthcare", active: true, applications: 8750, budget: "₹35,000 Cr" },
        { scheme_id: "CG003", scheme_name: { hi: "कौशल विकास मिशन", en: "Skill Development Mission" }, category: "Employment", active: false, applications: 3200, budget: "₹12,000 Cr" },
        { scheme_id: "CG004", scheme_name: { hi: "प्रधानमंत्री आवास योजना", en: "Pradhan Mantri Awas Yojana" }, category: "Housing", active: true, applications: 15600, budget: "₹45,000 Cr" },
        { scheme_id: "CG005", scheme_name: { hi: "राष्ट्रीय शिक्षा मिशन", en: "National Education Mission" }, category: "Education", active: true, applications: 9800, budget: "₹28,000 Cr" },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/admin/categories");
      const data = await response.json();
      setCategories([{ id: "all", name: "All Categories" }, ...data]);
    } catch (error) {
      // ✅ Updated fallback categories matching database
      setCategories([
        { id: "all", name: "All Categories" },
        { id: "divyang_pension", name: "दिव्यांग पेंशन" },
        { id: "women_pension", name: "महिला पेंशन" },
        { id: "widow_pension", name: "विधवा पेंशन" },
        { id: "general_pension", name: "सामान्य पेंशन" },
        { id: "old_age_pension", name: "वृद्धावस्था पेंशन" },
        { id: "family_assistance", name: "परिवार सहायता" },
        { id: "scholarship", name: "छात्रवृत्ति" },
        { id: "assistive_devices", name: "सहायक उपकरण" },
        { id: "marriage_incentive", name: "विवाह प्रोत्साहन" },
        { id: "civil_services", name: "सिविल सेवा" },
        { id: "hostel", name: "छात्रावास" },
        { id: "camp", name: "शिविर" },
        { id: "rehabilitation", name: "पुनर्वास" },
        { id: "tg_card", name: "टीजी कार्ड" },
        { id: "transgender_support", name: "ट्रांसजेंडर सहायता" },
        { id: "divyang_support", name: "दिव्यांग सहायता" },
        { id: "divyang_education", name: "दिव्यांग शिक्षा" },
        { id: "divyang_empowerment", name: "दिव्यांग सशक्तिकरण" },
        { id: "divyang_education_support", name: "दिव्यांग शिक्षा सहायता" },
        { id: "divyang_equipment_support", name: "दिव्यांग उपकरण" },
        { id: "divyang_rehabilitation_support", name: "दिव्यांग पुनर्वास" },
      ]);
    }
  };

  const handleSoftDelete = async (schemeId: string, schemeName: string) => {
    if (confirm(`Move "${schemeName}" to inactive? It won't be visible to users.`)) {
      try {
        const response = await fetch(`http://127.0.0.1:8000/admin/schemes/${schemeId}?soft_delete=true`, {
          method: "DELETE",
        });
        
        if (response.ok) {
          alert("✅ Scheme moved to inactive!");
          fetchSchemes();
        } else {
          const error = await response.json();
          alert("❌ Failed: " + (error.detail || "Unknown error"));
        }
      } catch (error) {
        console.error("Error:", error);
        alert("❌ Network error");
      }
    }
  };

  const handlePermanentDelete = async (schemeId: string, schemeName: string) => {
    if (confirm(`⚠️ PERMANENT DELETE: Are you ABSOLUTELY sure you want to permanently delete "${schemeName}"? This action cannot be undone!`)) {
      try {
        const response = await fetch(`http://127.0.0.1:8000/admin/schemes/${schemeId}?soft_delete=false`, {
          method: "DELETE",
        });
        
        if (response.ok) {
          alert("✅ Scheme permanently deleted from database!");
          fetchSchemes();
        } else {
          const error = await response.json();
          alert("❌ Failed: " + (error.detail || "Unknown error"));
        }
      } catch (error) {
        console.error("Error:", error);
        alert("❌ Network error");
      }
    }
  };

  const handleReactivate = async (schemeId: string, schemeName: string) => {
    if (confirm(`Reactivate "${schemeName}"? It will become visible to users again.`)) {
      try {
        const response = await fetch(`http://127.0.0.1:8000/admin/schemes/${schemeId}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ active: true }),
        });
        
        if (response.ok) {
          alert("✅ Scheme reactivated successfully!");
          fetchSchemes();
        } else {
          const error = await response.json();
          alert("❌ Failed: " + (error.detail || "Unknown error"));
        }
      } catch (error) {
        console.error("Error:", error);
        alert("❌ Network error");
      }
    }
  };

  const filteredSchemes = schemes.filter(scheme => {
    const matchesSearch = scheme.scheme_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          scheme.scheme_name.hi.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          scheme.scheme_name.en.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === "all" || scheme.category === selectedCategory;
    const matchesStatus = !showInactive || !scheme.active;
    return matchesSearch && matchesCategory && matchesStatus;
  });

  const stats = {
    total: schemes.length,
    active: schemes.filter(s => s.active).length,
    inactive: schemes.filter(s => !s.active).length,
    totalApps: schemes.reduce((sum, s) => sum + (s.applications || 0), 0),
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-semibold text-gray-800 dark:text-white">Scheme Management</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Manage all government schemes</p>
        </div>
        <Link
          href="/admin/schemes/add"
          className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl text-sm font-medium hover:from-indigo-700 hover:to-purple-700 transition-all shadow-md"
        >
          <Plus className="w-4 h-4" />
          Add New Scheme
        </Link>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800/50 rounded-xl p-4 border border-gray-200 dark:border-gray-700 transition-all duration-200 hover:bg-indigo-50 dark:hover:bg-indigo-950/20 cursor-pointer">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400">Total Schemes</p>
              <p className="text-2xl font-bold text-gray-800 dark:text-white">{stats.total}</p>
            </div>
            <div className="w-10 h-10 bg-indigo-100 dark:bg-indigo-900/30 rounded-lg flex items-center justify-center">
              <FolderOpen className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
            </div>
          </div>
        </div>
        
        <div className="bg-white dark:bg-gray-800/50 rounded-xl p-4 border border-gray-200 dark:border-gray-700 transition-all duration-200 hover:bg-emerald-50 dark:hover:bg-emerald-950/20 cursor-pointer">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400">Active Schemes</p>
              <p className="text-2xl font-bold text-gray-800 dark:text-white">{stats.active}</p>
            </div>
            <div className="w-10 h-10 bg-emerald-100 dark:bg-emerald-900/30 rounded-lg flex items-center justify-center">
              <CheckCircle className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
            </div>
          </div>
        </div>
        
        <div className="bg-white dark:bg-gray-800/50 rounded-xl p-4 border border-gray-200 dark:border-gray-700 transition-all duration-200 hover:bg-red-50 dark:hover:bg-red-950/20 cursor-pointer">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400">Inactive Schemes</p>
              <p className="text-2xl font-bold text-gray-800 dark:text-white">{stats.inactive}</p>
            </div>
            <div className="w-10 h-10 bg-red-100 dark:bg-red-900/30 rounded-lg flex items-center justify-center">
              <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400" />
            </div>
          </div>
        </div>
        
        <div className="bg-white dark:bg-gray-800/50 rounded-xl p-4 border border-gray-200 dark:border-gray-700 transition-all duration-200 hover:bg-purple-50 dark:hover:bg-purple-950/20 cursor-pointer">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400">Total Applications</p>
              <p className="text-2xl font-bold text-gray-800 dark:text-white">{stats.totalApps.toLocaleString()}</p>
            </div>
            <div className="w-10 h-10 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-purple-600 dark:text-purple-400" />
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800/50 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
        <div className="flex flex-wrap gap-4">
          <div className="flex-1 min-w-[200px]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search by ID or name..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all duration-200 hover:bg-gray-100 dark:hover:bg-gray-800"
              />
            </div>
          </div>
          
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-4 py-2 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all duration-200 hover:bg-gray-100 dark:hover:bg-gray-800 cursor-pointer"
          >
            {categories.map((cat) => (
              <option key={cat.id} value={cat.id}>{cat.name}</option>
            ))}
          </select>
          
          <button
            onClick={() => setShowInactive(!showInactive)}
            className={`inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm transition-all duration-200 cursor-pointer ${
              showInactive 
                ? "bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400 hover:bg-indigo-200 dark:hover:bg-indigo-900/50" 
                : "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700"
            }`}
          >
            <Filter className="w-4 h-4" />
            Show Inactive
          </button>
          
          {searchTerm && (
            <button
              onClick={() => setSearchTerm("")}
              className="inline-flex items-center gap-1 px-3 py-2 text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-all duration-200 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-xl cursor-pointer"
            >
              <X className="w-4 h-4" />
              Clear
            </button>
          )}
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800/50 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 dark:bg-gray-800/80 border-b border-gray-200 dark:border-gray-700">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">S.No</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Scheme ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Scheme Name (Hindi)</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Category</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
              {loading ? (
                <tr>
                  <td colSpan={6} className="px-6 py-8 text-center text-gray-500">
                    <div className="flex justify-center">
                      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-600"></div>
                    </div>
                    Loading schemes...
                  </td>
                </tr>
              ) : filteredSchemes.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-8 text-center text-gray-500">
                    No schemes found
                  </td>
                </tr>
              ) : (
                filteredSchemes.map((scheme, idx) => (
                  <tr 
                    key={scheme._id || idx} 
                    className="hover:bg-indigo-50 dark:hover:bg-indigo-950/20 transition-all duration-200 cursor-pointer"
                  >
                    <td className="px-6 py-3 text-sm text-gray-500">{idx + 1}</td>
                    <td className="px-6 py-3 text-sm font-mono text-gray-600 dark:text-gray-300">{scheme.scheme_id}</td>
                    <td className="px-6 py-3 text-sm text-gray-800 dark:text-white">{scheme.scheme_name.hi}</td>
                    <td className="px-6 py-3 text-sm text-gray-600">{scheme.category}</td>
                    <td className="px-6 py-3">
                      <span className={`inline-flex items-center gap-1 px-2 py-1 text-xs rounded-full ${
                        scheme.active 
                          ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400" 
                          : "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
                      }`}>
                        {scheme.active ? "Active" : "Inactive"}
                      </span>
                    </td>
                    <td className="px-6 py-3">
                      <div className="flex items-center gap-2">
                        <Link
                          href={`/admin/schemes/edit/${scheme.scheme_id}`}
                          className="p-1 text-gray-500 hover:text-indigo-600 transition duration-200"
                          title="Edit Scheme"
                        >
                          <Edit className="w-4 h-4" />
                        </Link>
                        
                        {scheme.active ? (
                          <button
                            onClick={() => handleSoftDelete(scheme.scheme_id, scheme.scheme_name.hi)}
                            className="p-1 text-orange-500 hover:text-orange-700 transition duration-200"
                            title="Move to Inactive"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        ) : (
                          <>
                            <button
                              onClick={() => handleReactivate(scheme.scheme_id, scheme.scheme_name.hi)}
                              className="p-1 text-green-500 hover:text-green-700 transition duration-200"
                              title="Reactivate Scheme"
                            >
                              <RefreshCw className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handlePermanentDelete(scheme.scheme_id, scheme.scheme_name.hi)}
                              className="p-1 text-red-500 hover:text-red-700 transition duration-200"
                              title="Permanently Delete"
                            >
                              <Trash className="w-4 h-4" />
                            </button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}