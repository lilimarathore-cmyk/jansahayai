// app/voice-chat/page.tsx
"use client"

import { useState, useEffect, useRef, useCallback } from "react"
import VoiceMicButton from "../../components/VoiceMicButton"
import VoiceChatMessage from "../../components/VoiceChatMessage"
import { sendMessage } from "../../services/api"
import { speak, stopSpeaking, cleanTextForSpeech } from "../../services/speech"

interface Message {
  id: string
  sender: "user" | "bot"
  text: string
  timestamp: Date
}

export default function VoiceChatPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputText, setInputText] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)
  const recognitionRef = useRef<any>(null)

  // Scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Welcome message on first load
  useEffect(() => {
    if (messages.length === 0) {
      const welcomeMsg: Message = {
        id: Date.now().toString(),
        sender: "bot",
        text: "नमस्ते! 🙏\n\nमैं **दिव्यांगBot** हूँ। मैं छत्तीसगढ़ की सरकारी योजनाओं के बारे में जानकारी देती हूँ।\n\n**आप मुझसे पूछ सकते हैं:**\n\n📌 **दिव्यांग योजनाएं** - \"दिव्यांग योजनाओं के बारे में बताओ\"\n📌 **विधवा पेंशन** - \"विधवा पेंशन / तलाकशुदा पेंशन के बारे में बताओ\"\n📌 **वृद्धावस्था पेंशन** - \"बुजुर्ग पेंशन के बारे में बताओ\"\n📌 **परिवार सहायता योजनाएं** - \"परिवार सहायता योजनाओं के बारे में बताओ\"\n📌 **टीजी कार्ड** - \"टीजी कार्ड कैसे बनेगा?\"\n\nया सीधे अपना सवाल लिखें या बोलें। मैं आपकी पूरी मदद करूंगी। 😊",
        timestamp: new Date()
      }
      setMessages([welcomeMsg])
      setTimeout(() => {
        speak(cleanTextForSpeech(welcomeMsg.text), "hi-IN")
      }, 500)
    }
  }, [])

  // Initialize speech recognition
  useEffect(() => {
    if (typeof window !== "undefined") {
      const SpeechRecognition = (window as any).SpeechRecognition || 
                               (window as any).webkitSpeechRecognition
      
      if (SpeechRecognition) {
        const recognition = new SpeechRecognition()
        recognition.continuous = false
        recognition.interimResults = false
        recognition.lang = "hi-IN"
        
        recognition.onstart = () => {
          setIsRecording(true)
        }
        
        recognition.onend = () => {
          setIsRecording(false)
        }
        
        recognition.onerror = (event: any) => {
          console.error("Recognition error:", event.error)
          setIsRecording(false)
          if (event.error === "no-speech") {
            const errorMsg: Message = {
              id: Date.now().toString(),
              sender: "bot",
              text: "कोई आवाज़ नहीं मिली। कृपया फिर से बोलें।",
              timestamp: new Date()
            }
            setMessages(prev => [...prev, errorMsg])
            speak(cleanTextForSpeech(errorMsg.text), "hi-IN")
          }
        }
        
        recognition.onresult = (event: any) => {
          const text = event.results[0][0].transcript
          console.log("Voice input:", text)
          handleSendMessage(text)
        }
        
        recognitionRef.current = recognition
      }
    }
  }, [])

  const startVoiceRecording = () => {
    if (recognitionRef.current && !isRecording && !isLoading) {
      try {
        recognitionRef.current.start()
      } catch (error) {
        console.error("Start error:", error)
      }
    }
  }

  const handleSendMessage = async (text: string) => {
    if (!text.trim() || isLoading) return
    
    // Add user message
    const userMsg: Message = {
      id: Date.now().toString(),
      sender: "user",
      text: text.trim(),
      timestamp: new Date()
    }
    setMessages(prev => [...prev, userMsg])
    setInputText("")
    setIsLoading(true)
    
    try {
      const data = await sendMessage(text.trim())
      const botReply = data.response || "मुझे समझ नहीं आया। कृपया फिर से पूछें।"
      
      const botMsg: Message = {
        id: (Date.now() + 1).toString(),
        sender: "bot",
        text: botReply,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, botMsg])
      
      // Speak bot reply (cleaned)
      const cleanedText = cleanTextForSpeech(botReply)
      await speak(cleanedText, "hi-IN")
      
    } catch (error) {
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        sender: "bot",
        text: "सर्वर कनेक्शन में समस्या है। कृपया बाद में प्रयास करें।",
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMsg])
      speak(cleanTextForSpeech(errorMsg.text), "hi-IN")
    }
    
    setIsLoading(false)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      if (inputText.trim() && !isLoading) {
        handleSendMessage(inputText)
      }
    }
  }

  const stopBotSpeaking = () => {
    stopSpeaking()
    setIsSpeaking(false)
  }

  return (
    <div className="flex flex-col h-full bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-4 shadow-sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center text-white text-xl shadow-md">
              🎤
            </div>
            <div>
              <h1 className="text-lg font-semibold text-gray-800 dark:text-white">
                वॉयस चैट
              </h1>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {isRecording ? "🎤 सुन रहा हूँ..." : isLoading ? "🤔 सोच रहा हूँ..." : isSpeaking ? "🔊 बोल रहा हूँ..." : "✅ तैयार"}
              </p>
            </div>
          </div>
          {isSpeaking && (
            <button
              onClick={stopBotSpeaking}
              className="px-3 py-1.5 text-xs bg-red-500 text-white rounded-lg hover:bg-red-600 transition"
            >
              रोकें
            </button>
          )}
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => (
          <VoiceChatMessage
            key={msg.id}
            sender={msg.sender}
            text={msg.text}
            timestamp={msg.timestamp}
            onSpeak={msg.sender === "bot" ? () => speak(cleanTextForSpeech(msg.text), "hi-IN") : undefined}
          />
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 dark:bg-gray-800 rounded-2xl rounded-bl-none px-4 py-3">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.15s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.3s' }}></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-4">
        <div className="flex gap-3 items-end">
          {/* Voice Mic Button */}
          <VoiceMicButton
            onStart={startVoiceRecording}
            isRecording={isRecording}
            disabled={isLoading}
          />

          {/* Text Input */}
          <div className="flex-1">
            <textarea
              ref={inputRef}
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="या यहाँ लिखें..."
              rows={1}
              className="w-full px-4 py-3 border-2 border-gray-200 dark:border-gray-700 rounded-xl focus:outline-none focus:border-purple-500 dark:bg-gray-700 dark:text-white resize-none"
              disabled={isLoading}
            />
          </div>

          {/* Send Button */}
          <button
            onClick={() => handleSendMessage(inputText)}
            disabled={!inputText.trim() || isLoading}
            className="bg-gradient-to-r from-purple-500 to-pink-500 text-white px-5 py-3 rounded-xl font-medium disabled:opacity-50 transition-all shadow-md"
          >
            📤
          </button>
        </div>
        <p className="text-xs text-gray-400 text-center mt-3">
          🎤 माइक बटन दबाएं और बोलें | ✍️ लिखकर भी भेज सकते हैं
        </p>
      </div>
    </div>
  )
}