//frontend/app/admin/settings/page.tsx
"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

export default function SettingsPage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<"password" | "email">("password");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  
  const [newEmail, setNewEmail] = useState("");
  const [confirmEmail, setConfirmEmail] = useState("");
  const [currentEmail, setCurrentEmail] = useState("");

  // Get current date
  const currentDate = new Date().toLocaleDateString('en-US', { 
    weekday: 'long', 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  });

  useEffect(() => {
    const adminAccount = JSON.parse(localStorage.getItem("admin_account") || "{}");
    setCurrentEmail(adminAccount.email || "");
  }, []);

  useEffect(() => {
    const isLoggedIn = localStorage.getItem("admin_logged_in");
    if (isLoggedIn !== "true") {
      router.push("/admin/login");
    }
  }, [router]);

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage("");
    setError("");

    const adminAccount = JSON.parse(localStorage.getItem("admin_account") || "{}");

    if (currentPassword !== adminAccount.password) {
      setError("Current password is incorrect");
      setLoading(false);
      return;
    }

    if (!newPassword || newPassword.length < 6) {
      setError("Password must be at least 6 characters");
      setLoading(false);
      return;
    }

    if (newPassword !== confirmPassword) {
      setError("Passwords do not match");
      setLoading(false);
      return;
    }

    if (newPassword === currentPassword) {
      setError("New password must be different");
      setLoading(false);
      return;
    }

    adminAccount.password = newPassword;
    localStorage.setItem("admin_account", JSON.stringify(adminAccount));

    setMessage("Password changed successfully!");
    setCurrentPassword("");
    setNewPassword("");
    setConfirmPassword("");
    
    setTimeout(() => setMessage(""), 3000);
    setLoading(false);
  };

  const handleEmailChange = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage("");
    setError("");

    const adminAccount = JSON.parse(localStorage.getItem("admin_account") || "{}");

    if (!newEmail || !newEmail.includes("@")) {
      setError("Please enter a valid email address");
      setLoading(false);
      return;
    }

    if (newEmail !== confirmEmail) {
      setError("Emails do not match");
      setLoading(false);
      return;
    }

    if (newEmail === currentEmail) {
      setError("New email is same as current");
      setLoading(false);
      return;
    }

    adminAccount.email = newEmail;
    localStorage.setItem("admin_account", JSON.stringify(adminAccount));
    localStorage.setItem("admin_email", newEmail);
    setCurrentEmail(newEmail);

    setMessage("Email changed successfully!");
    setNewEmail("");
    setConfirmEmail("");
    
    setTimeout(() => setMessage(""), 3000);
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      <div className="max-w-2xl mx-auto px-4 py-10">
        
        {/* Header - Only One */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-2">
            <h1 className="text-2xl font-semibold text-gray-800">Settings</h1>
            <span className="text-xs text-gray-400">{currentDate}</span>
          </div>
          <p className="text-gray-500 text-sm">Manage your account preferences</p>
        </div>

        {/* Tabs */}
        <div className="flex gap-8 border-b border-gray-200 mb-8">
          <button
            onClick={() => setActiveTab("password")}
            className={`pb-3 px-2 text-sm font-medium transition-all ${
              activeTab === "password"
                ? "text-indigo-600 border-b-2 border-indigo-600"
                : "text-gray-500 hover:text-gray-700"
            }`}
          >
            Change Password
          </button>
          <button
            onClick={() => setActiveTab("email")}
            className={`pb-3 px-2 text-sm font-medium transition-all ${
              activeTab === "email"
                ? "text-indigo-600 border-b-2 border-indigo-600"
                : "text-gray-500 hover:text-gray-700"
            }`}
          >
            Change Email
          </button>
        </div>

        {/* Password Tab */}
        {activeTab === "password" && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
            <div className="p-6">
              <form onSubmit={handlePasswordChange} className="space-y-5">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">
                    Current Password
                  </label>
                  <div className="relative">
                    <input
                      type={showCurrentPassword ? "text" : "password"}
                      value={currentPassword}
                      onChange={(e) => setCurrentPassword(e.target.value)}
                      placeholder="Enter current password"
                      required
                      className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-gray-800 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                    />
                    <button
                      type="button"
                      onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 text-xs hover:text-gray-600 transition"
                    >
                      {showCurrentPassword ? "Hide" : "Show"}
                    </button>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">
                    New Password
                  </label>
                  <div className="relative">
                    <input
                      type={showNewPassword ? "text" : "password"}
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      placeholder="Enter new password"
                      required
                      className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-gray-800 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                    />
                    <button
                      type="button"
                      onClick={() => setShowNewPassword(!showNewPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 text-xs hover:text-gray-600 transition"
                    >
                      {showNewPassword ? "Hide" : "Show"}
                    </button>
                  </div>
                  <p className="text-xs text-gray-400 mt-1.5 flex items-center gap-1">
                    <span className="w-1 h-1 bg-gray-400 rounded-full"></span>
                    Minimum 6 characters required
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">
                    Confirm Password
                  </label>
                  <input
                    type={showNewPassword ? "text" : "password"}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Confirm new password"
                    required
                    className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-gray-800 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                  />
                </div>

                {error && (
                  <div className="bg-rose-50 border border-rose-200 text-rose-600 text-sm p-3 rounded-lg">
                    {error}
                  </div>
                )}

                {message && (
                  <div className="bg-emerald-50 border border-emerald-200 text-emerald-600 text-sm p-3 rounded-lg">
                    {message}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-2.5 rounded-lg text-sm font-medium hover:from-indigo-700 hover:to-purple-700 transition-all disabled:opacity-50 shadow-sm"
                >
                  {loading ? "Updating..." : "Update Password"}
                </button>
              </form>
            </div>
          </div>
        )}

        {/* Email Tab */}
        {activeTab === "email" && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
            <div className="p-6">
              <form onSubmit={handleEmailChange} className="space-y-5">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">
                    Current Email
                  </label>
                  <input
                    type="email"
                    value={currentEmail}
                    disabled
                    className="w-full px-4 py-2.5 border border-gray-200 rounded-lg bg-gray-50 text-gray-500 text-sm cursor-not-allowed"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">
                    New Email
                  </label>
                  <input
                    type="email"
                    value={newEmail}
                    onChange={(e) => setNewEmail(e.target.value)}
                    placeholder="Enter new email address"
                    required
                    className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-gray-800 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">
                    Confirm Email
                  </label>
                  <input
                    type="email"
                    value={confirmEmail}
                    onChange={(e) => setConfirmEmail(e.target.value)}
                    placeholder="Confirm new email"
                    required
                    className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-gray-800 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                  />
                </div>

                {error && (
                  <div className="bg-rose-50 border border-rose-200 text-rose-600 text-sm p-3 rounded-lg">
                    {error}
                  </div>
                )}

                {message && (
                  <div className="bg-emerald-50 border border-emerald-200 text-emerald-600 text-sm p-3 rounded-lg">
                    {message}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-2.5 rounded-lg text-sm font-medium hover:from-indigo-700 hover:to-purple-700 transition-all disabled:opacity-50 shadow-sm"
                >
                  {loading ? "Updating..." : "Update Email"}
                </button>
              </form>
            </div>
          </div>
        )}

        {/* Security Tips */}
        <div className="mt-6 bg-gradient-to-r from-indigo-50/80 to-purple-50/80 rounded-xl p-4 border border-indigo-100">
          <div className="flex gap-2">
            <span className="text-indigo-500 text-base">✨</span>
            <div>
              <p className="text-sm font-medium text-gray-800">Security Tips</p>
              <ul className="text-xs text-gray-600 mt-1.5 space-y-1">
                <li className="flex items-center gap-2">
                  <span className="w-1 h-1 bg-indigo-400 rounded-full"></span>
                  Use a strong password (min 6 characters)
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1 h-1 bg-indigo-400 rounded-full"></span>
                  Never share your credentials with anyone
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1 h-1 bg-indigo-400 rounded-full"></span>
                  Update your password regularly for safety
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}