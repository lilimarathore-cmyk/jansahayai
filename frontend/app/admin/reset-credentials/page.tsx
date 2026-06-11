//frontend/app/admin/reset-credentials/page.tsx
"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import Image from "next/image";

export default function ResetCredentials() {
  const router = useRouter();
  const [newEmail, setNewEmail] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);
  const [recoveryType, setRecoveryType] = useState<"password" | "email" | "both">("password");

  useEffect(() => {
    const resetToken = localStorage.getItem("reset_token");
    if (!resetToken) {
      router.push("/admin/login");
    }

    const storedType = localStorage.getItem("recovery_type") as "password" | "email" | "both" | null;
    if (storedType === "password" || storedType === "email" || storedType === "both") {
      setRecoveryType(storedType);
    }
  }, [router]);

  const handleReset = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setSuccess("");

    const adminAccount = JSON.parse(localStorage.getItem("admin_account") || "{}");
    const updatedAccount = { ...adminAccount };

    if (recoveryType === "email" || recoveryType === "both") {
      if (!newEmail) {
        setError("❌ Please enter new email address.");
        setLoading(false);
        return;
      }
      if (!newEmail.includes("@")) {
        setError("❌ Please enter a valid email address.");
        setLoading(false);
        return;
      }
      updatedAccount.email = newEmail;
    }

    if (recoveryType === "password" || recoveryType === "both") {
      if (!newPassword) {
        setError("❌ Please enter new password.");
        setLoading(false);
        return;
      }
      if (newPassword.length < 6) {
        setError("❌ Password must be at least 6 characters.");
        setLoading(false);
        return;
      }
      if (newPassword !== confirmPassword) {
        setError("❌ Passwords do not match.");
        setLoading(false);
        return;
      }
      updatedAccount.password = newPassword;
    }

    localStorage.setItem("admin_account", JSON.stringify(updatedAccount));
    
    localStorage.removeItem("reset_token");
    localStorage.removeItem("reset_otp");
    localStorage.removeItem("otp_expiry");
    localStorage.removeItem("recovery_type");

    setSuccess("✅ Credentials updated successfully! Redirecting to login...");
    
    setTimeout(() => {
      router.push("/admin/login");
    }, 2000);
    setLoading(false);
  };

  const showEmailField = recoveryType === "email" || recoveryType === "both";
  const showPasswordField = recoveryType === "password" || recoveryType === "both";

  const getTitleText = () => {
    if (recoveryType === "email") return "Reset Email Address";
    if (recoveryType === "password") return "Reset Password";
    return "Reset Email & Password";
  };

  const getDescriptionText = () => {
    if (recoveryType === "email") return "Set your new email address";
    if (recoveryType === "password") return "Set your new password";
    return "Set your new email address and password";
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center bg-gradient-to-br from-[#0A0F1C] via-[#0F172A] to-[#1E1B4B] overflow-hidden">
      <div className="absolute -top-40 -right-40 w-96 h-96 bg-blue-500 rounded-full blur-3xl opacity-10 animate-pulse" />
      <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-purple-500 rounded-full blur-3xl opacity-10 animate-pulse" />

      <div className="relative z-10 w-full px-4 sm:px-6">
        <div className="mx-auto w-full max-w-[90%] sm:max-w-md md:max-w-lg bg-white/5 backdrop-blur-xl rounded-2xl shadow-2xl border border-white/10 p-5 sm:p-6 md:p-8">
          
          {/* Logo Section */}
          <div className="text-center mb-4 sm:mb-5">
            <div className="w-12 h-12 sm:w-14 sm:h-14 md:w-16 md:h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center mx-auto shadow-lg overflow-hidden">
              <Image
                src="/logo.png"
                alt="JanSahayAI Logo"
                width={64}
                height={64}
                className="object-cover w-full h-full"
                priority
              />
            </div>
            <h1 className="text-xl sm:text-2xl md:text-3xl font-bold text-white tracking-tight mt-2 sm:mt-3">
              JanSahayAI
            </h1>
            <p className="text-blue-300/80 text-xs sm:text-sm md:text-base font-medium tracking-wide mt-0.5">
              Admin Portal
            </p>
          </div>

          {/* Title Section */}
          <div className="text-center mb-5 sm:mb-6">
            <h2 className="text-base sm:text-lg md:text-xl font-semibold text-white">{getTitleText()}</h2>
            <p className="text-gray-400 text-xs sm:text-sm mt-1">{getDescriptionText()}</p>
          </div>

          <form onSubmit={handleReset} className="space-y-4 sm:space-y-5">
            {showEmailField && (
              <div>
                <label className="block text-xs sm:text-sm font-medium text-gray-300 mb-1.5">New Email Address</label>
                <div className="relative">
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm sm:text-base">📧</span>
                  <input
                    type="email"
                    value={newEmail}
                    onChange={(e) => setNewEmail(e.target.value)}
                    placeholder="newadmin@jansahay.ai"
                    required={!showPasswordField}
                    className="w-full pl-9 sm:pl-10 pr-3 py-2.5 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 text-sm sm:text-base focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
            )}

            {showPasswordField && (
              <>
                <div>
                  <label className="block text-xs sm:text-sm font-medium text-gray-300 mb-1.5">New Password</label>
                  <div className="relative">
                    <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm sm:text-base">🔒</span>
                    <input
                      type={showPassword ? "text" : "password"}
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      placeholder="••••••••"
                      required={!showEmailField}
                      className="w-full pl-9 sm:pl-10 pr-9 sm:pr-10 py-2.5 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 text-sm sm:text-base focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-300 transition text-sm sm:text-base"
                    >
                      {showPassword ? "👁️" : "👁️‍🗨️"}
                    </button>
                  </div>
                  <p className="text-[10px] sm:text-xs text-gray-500 mt-1">Password must be at least 6 characters</p>
                </div>

                <div>
                  <label className="block text-xs sm:text-sm font-medium text-gray-300 mb-1.5">Confirm New Password</label>
                  <div className="relative">
                    <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm sm:text-base">✓</span>
                    <input
                      type={showPassword ? "text" : "password"}
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      placeholder="••••••••"
                      required={!showEmailField}
                      className="w-full pl-9 sm:pl-10 pr-3 py-2.5 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 text-sm sm:text-base focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
              </>
            )}

            {error && (
              <div className="bg-red-500/10 border border-red-500/30 text-red-300 text-xs sm:text-sm p-2.5 rounded-xl">
                {error}
              </div>
            )}

            {success && (
              <div className="bg-green-500/10 border border-green-500/30 text-green-300 text-xs sm:text-sm p-2.5 rounded-xl">
                {success}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-2.5 sm:py-3 rounded-xl font-medium text-sm sm:text-base hover:from-blue-700 hover:to-purple-700 transition-all disabled:opacity-50 shadow-lg"
            >
              {loading ? "Updating..." : "Update Credentials"}
            </button>
          </form>

          <div className="mt-5 text-center">
            <Link href="/admin/login" className="text-xs sm:text-sm text-blue-400 hover:text-blue-300 transition">
              ← Back to Login
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}