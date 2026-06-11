//frontend/app/admin/show-email/page.tsx
"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import Image from "next/image";

export default function ShowEmail() {
  const [email, setEmail] = useState("");

  useEffect(() => {
    const recoveredEmail = localStorage.getItem("recovered_email");
    if (recoveredEmail) {
      setEmail(recoveredEmail);
      localStorage.removeItem("recovered_email");
    } else {
      const adminAccount = JSON.parse(localStorage.getItem("admin_account") || "{}");
      setEmail(adminAccount.email || "admin@jansahay.ai");
    }
  }, []);

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
            <h2 className="text-base sm:text-lg md:text-xl font-semibold text-white">Your Email Address</h2>
            <p className="text-gray-400 text-xs sm:text-sm mt-1">
              Your registered email address is:
            </p>
          </div>

          {/* Email Display Box */}
          <div className="mb-5 p-3 sm:p-4 bg-blue-600/10 rounded-xl border border-blue-500/30">
            <p className="text-sm sm:text-base md:text-lg font-mono text-blue-300 break-all text-center">
              {email}
            </p>
          </div>

          <Link
            href="/admin/login"
            className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-2.5 sm:py-3 rounded-xl font-medium text-sm sm:text-base hover:from-blue-700 hover:to-purple-700 transition-all block text-center shadow-lg"
          >
            Go to Login
          </Link>

          <div className="mt-4 text-center">
            <Link href="/admin/forgot-credentials" className="text-xs sm:text-sm text-blue-400 hover:text-blue-300 transition">
              ← Back
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}