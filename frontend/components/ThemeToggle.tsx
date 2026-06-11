// components/ThemeToggle.tsx
"use client"

import { useEffect, useState } from "react"

export default function ThemeToggle() {
  const [theme, setTheme] = useState<"light" | "dark">("light")

  useEffect(() => {
    const stored = localStorage.getItem("theme") as "light" | "dark" | null
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches
    
    if (stored) {
      setTheme(stored)
      document.documentElement.classList.add(stored)
    } else if (prefersDark) {
      setTheme("dark")
      document.documentElement.classList.add("dark")
    } else {
      document.documentElement.classList.add("light")
    }
  }, [])

  useEffect(() => {
    document.documentElement.classList.remove("light", "dark")
    document.documentElement.classList.add(theme)
    localStorage.setItem("theme", theme)
  }, [theme])

  const toggle = () => setTheme(theme === "light" ? "dark" : "light")

  return (
    <button
      onClick={toggle}
      className="p-2 rounded-full bg-gray-200 dark:bg-gray-700 transition-colors hover:scale-105 transform"
      aria-label="थीम बदलें"
    >
      {theme === "light" ? "🌙" : "☀️"}
    </button>
  )
}