// components/VoiceChatMessage.tsx
"use client"

import { useState } from "react"
import { speak, stopSpeaking, cleanTextForSpeech } from "../services/speech"

interface VoiceChatMessageProps {
  sender: "user" | "bot"
  text: string
  timestamp: Date
  onSpeak?: () => void
}

export default function VoiceChatMessage({ sender, text, timestamp, onSpeak }: VoiceChatMessageProps) {
  const [isPlaying, setIsPlaying] = useState(false)

  const handleSpeak = () => {
    if (isPlaying) {
      stopSpeaking()
      setIsPlaying(false)
    } else {
      const cleanText = cleanTextForSpeech(text)
      speak(cleanText, "hi-IN")
      setIsPlaying(true)
      const checkInterval = setInterval(() => {
        if (!window.speechSynthesis.speaking) {
          setIsPlaying(false)
          clearInterval(checkInterval)
        }
      }, 500)
    }
  }

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('hi-IN', { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className={`flex ${sender === "user" ? "justify-end" : "justify-start"} animate-fadeIn group`}>
      <div className={`relative max-w-[80%] rounded-2xl shadow-md ${
        sender === "user" 
          ? "bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-br-none" 
          : "bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-white rounded-bl-none"
      }`}>
        <div className="p-3">
          <p className="whitespace-pre-wrap break-words text-sm md:text-base leading-relaxed">
            {text}
          </p>
        </div>
        <div className={`flex items-center justify-between px-3 pb-2 ${
          sender === "user" ? "text-purple-100" : "text-gray-500 dark:text-gray-400"
        }`}>
          <p className="text-[10px]">
            {formatTime(timestamp)}
          </p>
          {sender === "bot" && (
            <button
              onClick={handleSpeak}
              className="p-1 rounded hover:bg-black/10 transition-colors"
              aria-label={isPlaying ? "आवाज़ बंद करें" : "सुनें"}
            >
              {isPlaying ? "🔊" : "🔈"}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}