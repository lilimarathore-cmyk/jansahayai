//frontend/app/admin/login/page.tsx
"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import Image from "next/image";

export default function AdminLogin() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const router = useRouter();

  // Check if already logged in
  useEffect(() => {
    const isLoggedIn = localStorage.getItem("admin_logged_in");
    if (isLoggedIn === "true") {
      router.push("/admin");
    }
  }, [router]);

  // Initialize default admin account if not exists
  useEffect(() => {
    if (!localStorage.getItem("admin_account")) {
      const defaultAdmin = {
        id: "admin_001",
        name: "Super Admin",
        email: "admin@jansahay.ai",
        password: "Admin@123",
        role: "super_admin",
        created_at: new Date().toISOString()
      };
      localStorage.setItem("admin_account", JSON.stringify(defaultAdmin));
      localStorage.setItem("admin_exists", "true");
    }
  }, []);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    const adminAccount = JSON.parse(localStorage.getItem("admin_account") || "{}");

    if (email === adminAccount.email && password === adminAccount.password) {
      localStorage.setItem("admin_logged_in", "true");
      localStorage.setItem("admin_email", email);
      localStorage.setItem("admin_name", adminAccount.name);

      if (rememberMe) {
        localStorage.setItem("remember_me", "true");
      }

      router.push("/admin");
    } else {
      setError("❌ Invalid email or password");
    }

    setLoading(false);
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center bg-gradient-to-br from-[#0A0F1C] via-[#0F172A] to-[#1E1B4B] overflow-hidden">
      {/* Background Effects */}
      <div className="absolute -top-40 -right-40 w-96 h-96 bg-blue-500 rounded-full blur-3xl opacity-10 animate-pulse" />
      <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-purple-500 rounded-full blur-3xl opacity-10 animate-pulse" />

      {/* Responsive Box */}
      <div className="relative z-10 w-full px-4 sm:px-6">
        <div className="mx-auto w-full max-w-[90%] sm:max-w-md md:max-w-lg lg:max-w-md xl:max-w-lg bg-white/5 backdrop-blur-xl rounded-2xl shadow-2xl border border-white/10 p-5 sm:p-6 md:p-8">
          
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

          {/* Welcome Section */}
          <div className="text-center mb-5 sm:mb-6">
            <h2 className="text-base sm:text-lg md:text-xl font-semibold text-white">
              Welcome Back
            </h2>
            <p className="text-gray-400 text-xs sm:text-sm mt-1">
              Sign in to access your secure dashboard
            </p>
          </div>

          <form onSubmit={handleLogin} className="space-y-4 sm:space-y-5">
            <div>
              <label className="block text-xs sm:text-sm font-medium text-gray-300 mb-1.5 tracking-wide">
                Email Address
              </label>
              <div className="relative group">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm sm:text-base">✉️</span>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="admin@jansahay.ai"
                  required
                  className="w-full pl-9 sm:pl-10 pr-3 py-2.5 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 text-sm sm:text-base focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs sm:text-sm font-medium text-gray-300 mb-1.5 tracking-wide">
                Password
              </label>
              <div className="relative group">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm sm:text-base">🔒</span>
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
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
            </div>

            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="w-3.5 h-3.5 bg-white/5 border border-white/20 rounded focus:ring-blue-500"
                />
                <span className="text-xs sm:text-sm text-gray-400">Remember me</span>
              </label>
              <Link href="/admin/forgot-credentials" className="text-xs sm:text-sm text-blue-400 hover:text-blue-300 transition">
                Forgot Credentials?
              </Link>
            </div>

            {error && (
              <div className="bg-red-500/10 border border-red-500/30 text-red-300 text-xs sm:text-sm p-2.5 rounded-xl">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-2.5 sm:py-3 rounded-xl font-medium text-sm sm:text-base hover:from-blue-700 hover:to-purple-700 transition-all duration-200 disabled:opacity-50 shadow-lg"
            >
              {loading ? "Signing in..." : "Sign In"}
            </button>
          </form>

          {/* Demo Credentials */}
          <div className="mt-5 pt-4 border-t border-white/10">
            <div className="text-center">
              <p className="text-[10px] sm:text-xs text-gray-500 tracking-wide mb-1.5">DEMO CREDENTIALS</p>
              <div className="flex items-center justify-center gap-2 text-xs sm:text-sm">
                <code className="text-gray-400 bg-white/5 px-2 py-0.5 rounded font-mono">
                  admin@jansahay.ai
                </code>
                <span className="text-gray-500">/</span>
                <code className="text-gray-400 bg-white/5 px-2 py-0.5 rounded font-mono">
                  Admin@123
                </code>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}