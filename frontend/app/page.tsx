// app/page.tsx
"use client";

import { useState, useRef, useEffect } from "react";
import ChatInput from "../components/ChatInput";
import AccessibilityControls from "../components/AccessibilityControls";
import HistoryPanel from "../components/HistoryPanel";
import ChatMessage from "../components/ChatMessage";
import VoiceAssistant from "../components/VoiceAssistant";
import { sendMessage } from "../services/api";
import { speak, stopSpeaking } from "../services/speech";

interface Message {
  sender: "user" | "bot";
  text: string;
  timestamp: Date;
  scheme_id?: string;
  isEligible?: boolean;
}

interface ChatSession {
  id: string;
  title: string;
  messages: Message[];
  timestamp: string;
  preview: string;
}

const QUICK_ACTIONS = [
  { id: "divyang", label: "दिव्यांग योजना", query: "दिव्यांग योजनाओं के बारे में बताओ" },
  { id: "old_age", label: "वृद्ध पेंशन", query: "वृद्धावस्था पेंशन योजना के बारे में बताओ" },
  { id: "widow", label: "विधवा पेंशन", query: "विधवा पेंशन योजना के बारे में बताओ" },
  { id: "talakshuda", label: "तलाकशुदा पेंशन", query: "तलाकशुदा पेंशन योजना के बारे में बताओ" },
  { id: "family", label: "परिवार सहायता", query: "परिवार सहायता योजनाओं के बारे में बताओ" },
  { id: "tg", label: "टीजी कार्ड", query: "टीजी कार्ड के बारे में बताओ" },
];

export default function Home() {
  const [chat, setChat] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [highContrast, setHighContrast] = useState(false);
  const [history, setHistory] = useState<ChatSession[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [isVoiceMode, setIsVoiceMode] = useState(false);
  const [isAccessibilityOpen, setIsAccessibilityOpen] = useState(false);
  const [hasShownWelcome, setHasShownWelcome] = useState(false);

  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
      if (window.innerWidth >= 768) setIsSidebarOpen(true);
    };
    checkMobile();
    window.addEventListener("resize", checkMobile);
    return () => window.removeEventListener("resize", checkMobile);
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chat]);

  useEffect(() => {
    const savedHistory = localStorage.getItem("chatSessions");
    if (savedHistory) {
      try {
        const parsed = JSON.parse(savedHistory);
        setHistory(parsed.slice(0, 15));
      } catch (e) {
        console.error("Error loading history:", e);
      }
    }
  }, []);

  useEffect(() => {
    if (!hasShownWelcome && chat.length === 0) {
      setHasShownWelcome(true);
      setCurrentSessionId(Date.now().toString());
    }
  }, [hasShownWelcome, chat.length]);

  const saveCurrentSession = () => {
    if (chat.length === 0) return;
    const firstUserMessage = chat.find((m) => m.sender === "user")?.text || "नई चैट";
    const title = firstUserMessage.length > 30 ? firstUserMessage.substring(0, 30) + "..." : firstUserMessage;
    const preview = chat[chat.length - 1]?.text.substring(0, 60) || "";

    const newSession: ChatSession = {
      id: currentSessionId || Date.now().toString(),
      title: title,
      messages: [...chat],
      timestamp: new Date().toISOString(),
      preview: preview,
    };

    setHistory((prev) => {
      const existingIndex = prev.findIndex((s) => s.id === newSession.id);
      let updatedHistory;
      if (existingIndex >= 0) {
        updatedHistory = [...prev];
        updatedHistory[existingIndex] = newSession;
      } else {
        updatedHistory = [newSession, ...prev];
      }
      updatedHistory = updatedHistory.slice(0, 15);
      localStorage.setItem("chatSessions", JSON.stringify(updatedHistory));
      return updatedHistory;
    });
  };

  const createNewSession = () => {
    if (chat.length > 0) saveCurrentSession();
    setCurrentSessionId(Date.now().toString());
    setChat([]);
    setHasShownWelcome(false);
    stopSpeaking();
    if (isMobile) setIsSidebarOpen(false);
  };

  const loadSession = (session: ChatSession) => {
    if (chat.length > 0 && currentSessionId) saveCurrentSession();
    setCurrentSessionId(session.id);
    setChat(session.messages);
    stopSpeaking();
    if (isMobile) setIsSidebarOpen(false);
  };

  const deleteSession = (sessionId: string) => {
    setHistory((prev) => {
      const newHistory = prev.filter((s) => s.id !== sessionId);
      localStorage.setItem("chatSessions", JSON.stringify(newHistory));
      if (sessionId === currentSessionId) createNewSession();
      return newHistory;
    });
  };

  const clearAllHistory = () => {
    if (confirm("सभी चैट इतिहास डिलीट करें?")) {
      setHistory([]);
      localStorage.setItem("chatSessions", JSON.stringify([]));
      createNewSession();
    }
  };

  const editAndResendMessage = async (index: number, newText: string) => {
    if (!newText.trim()) return;
    const newChat = chat.slice(0, index);
    setChat(newChat);
    await sendUserMessage(newText);
  };

  const sendUserMessage = async (message: string) => {
    if (!message.trim()) return;

    const userMessage: Message = {
      sender: "user",
      text: message,
      timestamp: new Date(),
    };
    setChat((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      const data = await sendMessage(message);
      const botReply = data.response || "मुझे समझ नहीं आया। कृपया फिर से पूछें।";
      
      const botMessage: Message = {
        sender: "bot",
        text: botReply,
        timestamp: new Date(),
        scheme_id: data.scheme_id,
        isEligible: data.is_eligible
      };
      setChat((prev) => [...prev, botMessage]);

      if (!isVoiceMode) speak(botReply, "hi-IN");

      if (isMobile) setIsSidebarOpen(false);
    } catch (error) {
      const errorMessage: Message = {
        sender: "bot",
        text: "सर्वर कनेक्शन में समस्या है। कृपया बाद में प्रयास करें।",
        timestamp: new Date(),
      };
      setChat((prev) => [...prev, errorMessage]);
    }
    setLoading(false);
  };

  const handleSend = async (message: string) => {
    await sendUserMessage(message);
  };

  const deleteMessage = (index: number) => {
    setChat((prev) => prev.filter((_, i) => i !== index));
  };

  const handleQuickAction = (query: string) => {
    sendUserMessage(query);
  };

  const handleVoiceCommand = (command: string) => {
    if (command === "new_chat") createNewSession();
    else if (command === "open_history") setIsSidebarOpen(true);
    else if (command === "high_contrast") setHighContrast(!highContrast);
    else if (command === "stop_audio") stopSpeaking();
    else if (command === "clear_chat") createNewSession();
    else if (command.length > 2 && !command.includes("चैट") && !command.includes("इतिहास")) {
      sendUserMessage(command);
    }
  };

  useEffect(() => {
    if (chat.length > 0 && currentSessionId) {
      const timer = setTimeout(() => saveCurrentSession(), 1000);
      return () => clearTimeout(timer);
    }
  }, [chat, currentSessionId]);

  return (
    <div className={`flex h-screen bg-[#F8FAFC] ${highContrast ? "high-contrast" : ""}`}>
      {isMobile && (
        <button
          onClick={() => setIsSidebarOpen(!isSidebarOpen)}
          className="fixed top-4 left-4 z-50 bg-[#1E3A8A] text-white p-3 rounded-full shadow-lg transition-transform"
          aria-label="Menu"
        >
          {isSidebarOpen ? "✕" : "☰"}
        </button>
      )}

      <div
        className={`fixed md:static inset-y-0 left-0 z-40 w-72 bg-[#F1F5F9] border-r border-[#E2E8F0] flex flex-col sidebar-transition shadow-md ${
          isMobile ? (isSidebarOpen ? "sidebar-open" : "sidebar-closed") : "sidebar-open"
        }`}
      >
        {isMobile && isSidebarOpen && (
          <button
            onClick={() => setIsSidebarOpen(false)}
            className="absolute top-4 right-4 text-gray-500 text-2xl z-50 w-10 h-10 rounded-full hover:bg-gray-200"
          >
            ✕
          </button>
        )}

        <div className="p-4 pt-safe border-b border-[#E2E8F0]">
          <div className="flex items-center gap-2 mb-1">
            <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center overflow-hidden shadow-sm border border-gray-200">
              <img
                src="/logo.png"
                alt="JanSahayAI Logo"
                className="w-full h-full object-cover object-center"
              />
            </div>
            <h1 className="text-xl font-bold text-[#1E3A8A]">JanSahayAI</h1>
          </div>
          <p className="text-xs text-gray-500">छत्तीसगढ़ शासन | समाज कल्याण विभाग</p>
        </div>

        <div className="p-4">
          <button
            onClick={createNewSession}
            className="w-full bg-[#1E3A8A] text-white px-4 py-2.5 rounded-xl font-medium hover:bg-[#1E3A8A]/90 transition-all flex items-center justify-center gap-2 text-sm"
          >
            <span>+</span> नई चैट
          </button>
        </div>

        <div className="flex-1 overflow-y-auto">
          <HistoryPanel
            history={history}
            currentSessionId={currentSessionId}
            onSelect={loadSession}
            onDelete={deleteSession}
            onClearAll={clearAllHistory}
            isMobile={isMobile}
          />
        </div>

        <div className="border-t border-[#E2E8F0] p-3">
          <button
            onClick={() => setIsAccessibilityOpen(!isAccessibilityOpen)}
            className="w-full flex items-center justify-between text-gray-600 text-sm py-2"
          >
            <span>♿ एक्सेसिबिलिटी</span>
            <span>{isAccessibilityOpen ? "▼" : "▲"}</span>
          </button>
          {isAccessibilityOpen && (
            <AccessibilityControls
              highContrast={highContrast}
              setHighContrast={setHighContrast}
              isMobile={isMobile}
              onStopAudio={() => stopSpeaking()}
            />
          )}
        </div>
      </div>

      {isMobile && isSidebarOpen && (
        <div className="fixed inset-0 bg-black/30 z-30" onClick={() => setIsSidebarOpen(false)} />
      )}

      <div className="flex-1 flex flex-col w-full overflow-hidden bg-[#F8FAFC]">
        <div className="border-b border-[#E2E8F0] p-4 bg-white shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center overflow-hidden shadow-sm border border-gray-200">
                <img
                  src="/logo.png"
                  alt="JanSahayAI Logo"
                  className="w-full h-full object-cover object-center"
                />
              </div>
              <div>
                <h2 className="font-semibold text-gray-800 text-base">JanSahayAI</h2>
                <p className="text-[11px] text-gray-500">छत्तीसगढ़ शासन | समाज कल्याण विभाग</p>
              </div>
            </div>
            <button
              onClick={createNewSession}
              className="px-3 py-1.5 text-sm text-[#1E3A8A] border border-[#1E3A8A] rounded-lg hover:bg-[#1E3A8A]/5 transition-colors flex items-center gap-1"
            >
              <span>+</span> नई चैट
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          <div className="chat-container mx-auto space-y-3">
            {chat.length === 0 && (
              <div className="text-center py-8">
                <div className="w-28 h-28 bg-white rounded-full flex items-center justify-center overflow-hidden mx-auto mb-5 shadow-md border border-gray-200">
                  <img
                    src="/logo.png"
                    alt="JanSahayAI Logo"
                    className="w-full h-full object-cover object-center"
                  />
                </div>
                <h3 className="text-2xl font-semibold text-gray-800">नमस्ते 🙏</h3>
                <p className="text-gray-600 mt-3 max-w-md mx-auto text-base">
                  मैं <span className="font-medium text-[#1E3A8A]">JanSahayAI</span> हूँ।<br />
                  मैं छत्तीसगढ़ की सरकारी योजनाओं की जानकारी देता हूँ।
                </p>
                <div className="quick-actions-grid mt-8">
                  {QUICK_ACTIONS.map((action) => (
                    <button
                      key={action.id}
                      onClick={() => handleQuickAction(action.query)}
                      className="quick-action-btn"
                    >
                      {action.label}
                    </button>
                  ))}
                </div>
                <div className="mt-8 text-sm text-gray-400">
                  💡 आप अपनी समस्या सीधे लिखकर भी पूछ सकते हैं
                </div>
              </div>
            )}

            {chat.map((msg, idx) => (
              <ChatMessage
                key={idx}
                sender={msg.sender}
                text={msg.text}
                timestamp={msg.timestamp}
                scheme_id={msg.scheme_id}
                isEligible={msg.isEligible}
                onEdit={msg.sender === "user" ? (newText) => editAndResendMessage(idx, newText) : undefined}
                onDelete={() => deleteMessage(idx)}
              />
            ))}

            {loading && (
              <div className="flex justify-start">
                <div className="bg-white rounded-2xl rounded-bl-none px-4 py-3 shadow-sm border border-[#E2E8F0]">
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-gray-500">सोच रहा है</span>
                    <div className="flex gap-1">
                      <span className="typing-dot"></span>
                      <span className="typing-dot"></span>
                      <span className="typing-dot"></span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            <div ref={bottomRef} />
          </div>
        </div>

        <div className="border-t border-[#E2E8F0] p-4 bg-white shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)]">
          <div className="chat-container mx-auto">
            <ChatInput onSend={handleSend} isMobile={isMobile} />
          </div>
        </div>
      </div>

      <VoiceAssistant
        onCommand={handleVoiceCommand}
        isVoiceMode={isVoiceMode}
        onToggleVoiceMode={() => setIsVoiceMode(!isVoiceMode)}
        currentMode={isVoiceMode ? "voice" : "normal"}
        onNewChat={createNewSession}
        onOpenHistory={() => setIsSidebarOpen(true)}
        onLargeText={() => {}}
        onHighContrast={() => setHighContrast(!highContrast)}
        onStopAudio={stopSpeaking}
        onClearChat={createNewSession}
      />
    </div>
  );
}