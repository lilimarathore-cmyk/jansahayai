//frontend/app/admin/forgot-credentials/page.tsx
"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import Image from "next/image";

export default function ForgotCredentials() {
  const router = useRouter();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [recoveryType, setRecoveryType] = useState<"password" | "email" | "both">("password");
  const [registeredEmail, setRegisteredEmail] = useState("");

  useEffect(() => {
    const adminAccount = JSON.parse(localStorage.getItem("admin_account") || "{}");
    if (adminAccount.email) {
      setRegisteredEmail(adminAccount.email);
    }
  }, []);

  const handleSendOTP = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    const adminAccount = JSON.parse(localStorage.getItem("admin_account") || "{}");

    if (!adminAccount.email) {
      setError("❌ No admin account found.");
      setLoading(false);
      return;
    }

    const generatedOtp = Math.floor(100000 + Math.random() * 900000).toString();
    
    localStorage.setItem("reset_otp", generatedOtp);
    localStorage.setItem("reset_email", adminAccount.email);
    localStorage.setItem("recovery_type", recoveryType);
    localStorage.setItem("otp_expiry", (Date.now() + 300000).toString());
    
    alert(`Your OTP is: ${generatedOtp}\n\n(This would be sent to your email in production)`);
    
    router.push("/admin/verify-otp");
    setLoading(false);
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center bg-gradient-to-br from-[#0A0F1C] via-[#0F172A] to-[#1E1B4B] overflow-hidden">
      <div className="absolute -top-40 -right-40 w-96 h-96 bg-blue-500 rounded-full blur-3xl opacity-10 animate-pulse" />
      <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-purple-500 rounded-full blur-3xl opacity-10 animate-pulse" />

      <div className="relative z-10 w-full px-4 sm:px-6">
        <div className="mx-auto w-full max-w-[90%] sm:max-w-md md:max-w-lg lg:max-w-md xl:max-w-lg bg-white/5 backdrop-blur-xl rounded-2xl shadow-2xl border border-white/10 p-5 sm:p-6 md:p-8">
          
          {/* Logo Section - Compact */}
          <div className="text-center mb-3 sm:mb-4">
            <div className="w-10 h-10 sm:w-12 sm:h-12 md:w-14 md:h-14 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center mx-auto shadow-lg overflow-hidden">
              <Image
                src="/logo.png"
                alt="JanSahayAI Logo"
                width={56}
                height={56}
                className="object-cover w-full h-full"
                priority
              />
            </div>
            <h1 className="text-lg sm:text-xl md:text-2xl font-bold text-white tracking-tight mt-2 sm:mt-2 md:mt-3">
              JanSahayAI
            </h1>
            <p className="text-blue-300/80 text-[10px] sm:text-xs md:text-sm font-medium tracking-wide mt-0.5">
              Admin Portal
            </p>
          </div>

          {/* Title Section - Compact */}
          <div className="text-center mb-2">
            <h2 className="text-sm sm:text-base md:text-lg font-semibold text-white">
              Forgot Credentials
            </h2>
          </div>

          {/* Small helper text - Extra compact */}
          <p className="text-gray-400 text-[9px] sm:text-[10px] text-center mb-4 sm:mb-5">
            Unable to log in? Choose a recovery method below.
          </p>

          {/* Recovery Options - Compact spacing */}
          <div className="space-y-2 sm:space-y-2.5 mb-4 sm:mb-5">
            <button
              type="button"
              onClick={() => setRecoveryType("password")}
              className={`w-full text-left p-2 sm:p-2.5 rounded-xl border transition-all duration-200 ${
                recoveryType === "password"
                  ? "bg-blue-600/20 border-blue-500"
                  : "bg-white/5 border-white/10 hover:bg-white/10"
              }`}
            >
              <div className="flex items-center gap-2 sm:gap-2.5">
                <span className="text-base sm:text-lg md:text-xl">🔒</span>
                <div>
                  <p className="font-medium text-white text-[11px] sm:text-xs md:text-sm">
                    Forgot Password?
                  </p>
                  <p className="text-gray-400 text-[9px] sm:text-[10px]">
                    Reset your password
                  </p>
                </div>
              </div>
            </button>

            <button
              type="button"
              onClick={() => setRecoveryType("email")}
              className={`w-full text-left p-2 sm:p-2.5 rounded-xl border transition-all duration-200 ${
                recoveryType === "email"
                  ? "bg-blue-600/20 border-blue-500"
                  : "bg-white/5 border-white/10 hover:bg-white/10"
              }`}
            >
              <div className="flex items-center gap-2 sm:gap-2.5">
                <span className="text-base sm:text-lg md:text-xl">📧</span>
                <div>
                  <p className="font-medium text-white text-[11px] sm:text-xs md:text-sm">
                    Forgot Email ID?
                  </p>
                  <p className="text-gray-400 text-[9px] sm:text-[10px]">
                    Recover your email
                  </p>
                </div>
              </div>
            </button>

            <button
              type="button"
              onClick={() => setRecoveryType("both")}
              className={`w-full text-left p-2 sm:p-2.5 rounded-xl border transition-all duration-200 ${
                recoveryType === "both"
                  ? "bg-blue-600/20 border-blue-500"
                  : "bg-white/5 border-white/10 hover:bg-white/10"
              }`}
            >
              <div className="flex items-center gap-2 sm:gap-2.5">
                <span className="text-base sm:text-lg md:text-xl">🔄</span>
                <div>
                  <p className="font-medium text-white text-[11px] sm:text-xs md:text-sm">
                    Forgot Both?
                  </p>
                  <p className="text-gray-400 text-[9px] sm:text-[10px]">
                    Recover email & password
                  </p>
                </div>
              </div>
            </button>
          </div>

          {/* Email info - Compact */}
          <div className="mb-4 p-1.5 sm:p-2 bg-blue-600/10 rounded-xl border border-blue-500/30">
            <p className="text-[9px] sm:text-[10px] text-center text-blue-300">
              📧 OTP to: <span className="font-mono">{registeredEmail || "admin@jansahay.ai"}</span>
            </p>
          </div>

          {error && (
            <div className="bg-red-500/10 border border-red-500/30 text-red-300 text-[10px] p-2 rounded-xl mb-3">
              {error}
            </div>
          )}

          <button
            type="button"
            onClick={handleSendOTP}
            disabled={loading}
            className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-2 sm:py-2 rounded-xl font-medium text-[11px] sm:text-xs md:text-sm hover:from-blue-700 hover:to-purple-700 transition-all duration-200 disabled:opacity-50 shadow-lg"
          >
            {loading ? "Sending..." : "Request Reset Link"}
          </button>

          <div className="mt-3 sm:mt-4 text-center">
            <Link href="/admin/login" className="text-[9px] sm:text-[10px] md:text-xs text-blue-400 hover:text-blue-300 transition">
              ← Back to Login
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}