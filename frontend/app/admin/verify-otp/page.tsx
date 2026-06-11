//frontend/app/admin/verify-otp/page.tsx
"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import Image from "next/image";

export default function VerifyOTP() {
  const router = useRouter();
  const [otp, setOtp] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState("");
  const [recoveryType, setRecoveryType] = useState("");
  const [timeLeft, setTimeLeft] = useState(300);
  const [canResend, setCanResend] = useState(false);

  useEffect(() => {
    const resetEmail = localStorage.getItem("reset_email");
    const storedType = localStorage.getItem("recovery_type");
    const expiry = parseInt(localStorage.getItem("otp_expiry") || "0");
    
    if (!resetEmail) {
      router.push("/admin/forgot-credentials");
      return;
    }
    
    setEmail(resetEmail);
    setRecoveryType(storedType || "password");

    if (expiry > 0) {
      const remaining = Math.max(0, Math.floor((expiry - Date.now()) / 1000));
      setTimeLeft(remaining);
      setCanResend(remaining === 0);
    }
  }, [router]);

  useEffect(() => {
    if (timeLeft <= 0) {
      setCanResend(true);
      return;
    }

    const interval = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(interval);
          setCanResend(true);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [timeLeft]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  const handleVerifyOTP = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    const storedOtp = localStorage.getItem("reset_otp");
    const expiry = parseInt(localStorage.getItem("otp_expiry") || "0");

    if (Date.now() > expiry) {
      setError("OTP has expired");
      setLoading(false);
      return;
    }

    if (otp !== storedOtp) {
      setError("Invalid OTP");
      setLoading(false);
      return;
    }

    if (recoveryType === "email") {
      const adminAccount = JSON.parse(localStorage.getItem("admin_account") || "{}");
      localStorage.setItem("recovered_email", adminAccount.email);
      router.push("/admin/show-email");
      setLoading(false);
      return;
    }

    const token = Math.floor(10000000 + Math.random() * 90000000).toString();
    localStorage.setItem("reset_token", token);
    router.push("/admin/reset-credentials");
    setLoading(false);
  };

  const handleResendOTP = async () => {
    if (!canResend) return;
    
    setLoading(true);
    setError("");

    const adminAccount = JSON.parse(localStorage.getItem("admin_account") || "{}");

    if (!adminAccount.email) {
      setError("No admin account found");
      setLoading(false);
      return;
    }

    const generatedOtp = Math.floor(100000 + Math.random() * 900000).toString();
    const newExpiry = Date.now() + 300000;
    
    localStorage.setItem("reset_otp", generatedOtp);
    localStorage.setItem("otp_expiry", newExpiry.toString());
    
    setTimeLeft(300);
    setCanResend(false);
    
    alert(`Your new OTP is: ${generatedOtp}`);
    setLoading(false);
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center bg-gradient-to-br from-[#0A0F1C] via-[#0F172A] to-[#1E1B4B] overflow-hidden">
      {/* Subtle Background Orbs - Reduced opacity */}
      <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-500 rounded-full blur-3xl opacity-5 animate-pulse" />
      <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-500 rounded-full blur-3xl opacity-5 animate-pulse delay-1000" />

      <div className="relative z-10 w-full px-4 sm:px-6">
        <div className="mx-auto w-full max-w-[90%] sm:max-w-md md:max-w-lg">
          {/* Clean Card - No extra effects */}
          <div className="bg-white/5 backdrop-blur-sm rounded-2xl shadow-xl border border-white/10">
            <div className="p-5 sm:p-6 md:p-8">
              
              {/* Logo Section - Clean */}
              <div className="text-center mb-5 sm:mb-6">
                <div className="w-12 h-12 sm:w-14 sm:h-14 md:w-16 md:h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center mx-auto shadow-md overflow-hidden">
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
                <p className="text-blue-300/60 text-xs sm:text-sm md:text-base font-medium tracking-wide mt-0.5">
                  Admin Portal
                </p>
              </div>

              {/* Title Section - Simple */}
              <div className="text-center mb-6 sm:mb-7">
                <h2 className="text-base sm:text-lg md:text-xl font-semibold text-white">
                  Verify OTP
                </h2>
                <p className="text-gray-400 text-xs sm:text-sm mt-1">
                  Enter 6-digit code sent to your email
                </p>
                <p className="text-gray-500 text-[10px] sm:text-xs mt-2 font-mono break-all">
                  {email}
                </p>
              </div>

              <form onSubmit={handleVerifyOTP} className="space-y-4">
                {/* OTP Input - Clean */}
                <div>
                  <input
                    type="text"
                    value={otp}
                    onChange={(e) => setOtp(e.target.value)}
                    placeholder="000000"
                    maxLength={6}
                    required
                    className="w-full px-4 py-3 bg-white/5 border border-white/15 rounded-xl text-white text-center text-xl sm:text-2xl tracking-[0.2em] font-mono focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 transition-all"
                    autoFocus
                  />
                </div>

                {/* Timer - Simple Text */}
                {!canResend && (
                  <div className="text-center">
                    <p className="text-xs text-gray-400">
                      Valid for <span className="text-blue-400 font-mono">{formatTime(timeLeft)}</span>
                    </p>
                  </div>
                )}

                {/* Expired Message - Simple */}
                {canResend && (
                  <div className="text-center">
                    <p className="text-xs text-red-400">OTP has expired</p>
                  </div>
                )}

                {error && (
                  <div className="bg-red-500/10 border border-red-500/20 text-red-300 text-xs p-2.5 rounded-xl">
                    {error}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-2.5 rounded-xl font-medium text-sm hover:opacity-90 transition-all disabled:opacity-50"
                >
                  {loading ? "Verifying..." : "Verify OTP"}
                </button>
              </form>

              {/* Footer - Clean */}
              <div className="mt-5 pt-4 border-t border-white/10 text-center">
                {canResend ? (
                  <button
                    onClick={handleResendOTP}
                    disabled={loading}
                    className="text-xs text-blue-400 hover:text-blue-300 transition"
                  >
                    Resend OTP
                  </button>
                ) : (
                  <Link href="/admin/forgot-credentials" className="text-xs text-gray-400 hover:text-gray-300 transition">
                    ← Back
                  </Link>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}