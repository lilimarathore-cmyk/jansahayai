// frontend/app/admin/layout.tsx
"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import Image from "next/image";
import { 
  LayoutDashboard, 
  FolderKanban, 
  PlusCircle, 
  BarChart3, 
  MessageSquare, 
  Settings,
  LogOut,
  Sun,
  Moon,
  ChevronLeft,
  ChevronRight,
  Menu,
  User,
} from "lucide-react";

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [collapsed, setCollapsed] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const pathname = usePathname();
  const router = useRouter();

  const authPages = [
    "/admin/login", 
    "/admin/forgot-credentials", 
    "/admin/reset-credentials",
    "/admin/verify-otp",
    "/admin/show-email"
  ];

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
      if (window.innerWidth < 768) setCollapsed(true);
      else setCollapsed(false);
    };
    checkMobile();
    window.addEventListener("resize", checkMobile);
    return () => window.removeEventListener("resize", checkMobile);
  }, []);

  useEffect(() => {
    const savedTheme = localStorage.getItem("admin_theme");
    if (savedTheme === "dark") {
      setDarkMode(true);
      document.documentElement.classList.add("dark");
    }
  }, []);

  useEffect(() => {
    const isLoggedIn = localStorage.getItem("admin_logged_in");
    if (!authPages.includes(pathname) && !isLoggedIn) {
      router.push("/admin/login");
    }
  }, [pathname, router]);

  const handleLogout = () => {
    localStorage.removeItem("admin_logged_in");
    localStorage.removeItem("admin_email");
    router.push("/admin/login");
  };

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    if (!darkMode) {
      document.documentElement.classList.add("dark");
      localStorage.setItem("admin_theme", "dark");
    } else {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("admin_theme", "light");
    }
  };

  const menuItems = [
    { href: "/admin", label: "Dashboard", icon: LayoutDashboard, color: "text-indigo-500" },
    { href: "/admin/schemes", label: "Scheme Management", icon: FolderKanban, color: "text-emerald-500" },
    { href: "/admin/schemes/add", label: "Add New Scheme", icon: PlusCircle, color: "text-purple-500" },
    { href: "/admin/analytics", label: "Analytics", icon: BarChart3, color: "text-orange-500" },
    { href: "/admin/complaints", label: "Complaints", icon: MessageSquare, color: "text-rose-500" },
    { href: "/admin/settings", label: "Settings", icon: Settings, color: "text-gray-500" },
  ];

  const currentPageLabel = menuItems.find(item => item.href === pathname)?.label || "Dashboard";

  if (authPages.includes(pathname)) {
    return <>{children}</>;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-100 dark:from-gray-900 dark:via-gray-900 dark:to-gray-800">
      {/* Sidebar */}
      <aside
        className={`fixed left-0 top-0 h-full bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl shadow-2xl transition-all duration-300 z-50 border-r border-gray-200/50 dark:border-gray-800/50 ${
          collapsed ? "w-20" : "w-72"
        } ${isMobile && collapsed ? "-translate-x-full" : "translate-x-0"}`}
      >
        {/* Logo Area - With Actual Logo Image */}
        <div className={`px-6 py-6 border-b border-gray-200/50 dark:border-gray-800/50 ${collapsed ? "px-4" : ""}`}>
          {!collapsed ? (
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-xl flex items-center justify-center shadow-lg overflow-hidden">
                <Image
                  src="/logo.png"
                  alt="JanSahayAI Logo"
                  width={40}
                  height={40}
                  className="object-cover w-full h-full"
                />
              </div>
              <div>
                <h1 className="text-lg font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                  JanSahayAI
                </h1>
                <p className="text-[10px] text-gray-400 uppercase tracking-wider">Admin Portal</p>
              </div>
            </div>
          ) : (
            <div className="flex justify-center">
              <div className="w-10 h-10 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-xl flex items-center justify-center shadow-lg overflow-hidden">
                <Image
                  src="/logo.png"
                  alt="JanSahayAI Logo"
                  width={40}
                  height={40}
                  className="object-cover w-full h-full"
                />
              </div>
            </div>
          )}
        </div>

        {/* User Info */}
        {!collapsed && (
          <div className="mx-4 mt-6 p-4 bg-gradient-to-br from-indigo-50 to-purple-50 dark:from-indigo-950/30 dark:to-purple-950/30 rounded-2xl border border-indigo-100 dark:border-indigo-800/30">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-full flex items-center justify-center shadow-md">
                <User className="w-6 h-6 text-white" />
              </div>
              <div>
                <p className="text-sm font-semibold text-gray-800 dark:text-white">Admin User</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">admin@jansahay.ai</p>
              </div>
            </div>
          </div>
        )}

        {/* Navigation */}
        <nav className="mt-6 px-4 space-y-1.5">
          {menuItems.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;
            return (
              <Link
                key={item.label}
                href={item.href}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group ${
                  isActive
                    ? "bg-gradient-to-r from-indigo-500 to-purple-500 text-white shadow-lg shadow-indigo-500/20"
                    : "text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800"
                } ${collapsed ? "justify-center" : ""}`}
              >
                <Icon className={`w-5 h-5 ${!isActive && item.color}`} />
                {!collapsed && <span className="text-sm font-medium">{item.label}</span>}
                {collapsed && (
                  <div className="absolute left-full ml-3 px-3 py-2 bg-gray-900 text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 transition pointer-events-none whitespace-nowrap z-50 shadow-xl">
                    {item.label}
                  </div>
                )}
              </Link>
            );
          })}
        </nav>

        {/* Bottom Section */}
        <div className="absolute bottom-0 left-0 right-0 p-4 space-y-2 border-t border-gray-200/50 dark:border-gray-800/50">
          <button
            onClick={toggleDarkMode}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 ${
              collapsed ? "justify-center" : ""
            }`}
          >
            {darkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            {!collapsed && <span className="text-sm">{darkMode ? "Light Mode" : "Dark Mode"}</span>}
          </button>
          
          <button
            onClick={handleLogout}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 text-red-500 hover:bg-red-50 dark:hover:bg-red-950/20 ${
              collapsed ? "justify-center" : ""
            }`}
          >
            <LogOut className="w-5 h-5" />
            {!collapsed && <span className="text-sm">Logout</span>}
          </button>
        </div>

        {/* Collapse Toggle */}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="absolute -right-3 top-24 bg-white dark:bg-gray-800 rounded-full p-1 shadow-md border border-gray-200 dark:border-gray-700"
        >
          {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </aside>

      {/* Mobile Overlay */}
      {isMobile && !collapsed && (
        <div className="fixed inset-0 bg-black/50 z-40 backdrop-blur-sm" onClick={() => setCollapsed(true)} />
      )}

      {/* Main Content */}
      <main className={`transition-all duration-300 min-h-screen ${collapsed ? "ml-20" : "ml-72"}`}>
        {/* Top Header */}
        <header className="sticky top-0 z-30 bg-white/70 dark:bg-gray-900/70 backdrop-blur-xl border-b border-gray-200/50 dark:border-gray-800/50">
          <div className="flex items-center justify-between px-6 py-4">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setCollapsed(!collapsed)}
                className="lg:hidden text-gray-600 dark:text-gray-300"
              >
                <Menu className="w-5 h-5" />
              </button>
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                  {currentPageLabel}
                </h1>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                  {new Date().toLocaleDateString("en-IN", { 
                    weekday: 'long', 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric' 
                  })}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="hidden md:flex items-center gap-2 px-3 py-1.5 bg-emerald-50 dark:bg-emerald-950/30 rounded-full">
                <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
                <span className="text-xs text-emerald-600 dark:text-emerald-400">System Online</span>
              </div>
              <div className="w-9 h-9 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-full flex items-center justify-center shadow-md overflow-hidden">
                <Image
                  src="/logo.png"
                  alt="Avatar"
                  width={36}
                  height={36}
                  className="object-cover w-full h-full"
                />
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <div className="p-6">{children}</div>
      </main>
    </div>
  );
}