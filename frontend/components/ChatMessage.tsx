// components/ChatMessage.tsx
"use client";

import { useState, useRef, useEffect } from "react";
import { speak, stopSpeaking } from "../services/speech";

interface ChatMessageProps {
  sender: "user" | "bot";
  text: string;
  timestamp: Date;
  onEdit?: (newText: string) => void;
  onDelete?: () => void;
  scheme_id?: string;
  isEligible?: boolean;
}

export default function ChatMessage({ 
  sender, 
  text, 
  timestamp, 
  onEdit, 
  onDelete,
  scheme_id,
  isEligible
}: ChatMessageProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [copied, setCopied] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editText, setEditText] = useState(text);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [showDownload, setShowDownload] = useState(false);
  const [pdfExists, setPdfExists] = useState(false);
  const [detectedSchemeId, setDetectedSchemeId] = useState<string | null>(null);

  useEffect(() => {
    if (isEditing && textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = textareaRef.current.scrollHeight + "px";
      textareaRef.current.focus();
    }
  }, [isEditing]);

  const extractSchemeIdFromMessage = (messageText: string): string | null => {
    const schemeMappings: [string, string][] = [
      ["सामाजिक सुरक्षा दिव्यांग पेंशन योजना", "cg_scheme_001"],
      ["इंदिरा गांधी राष्ट्रीय दिव्यांग पेंशन योजना", "cg_scheme_006"],
      ["दिव्यांगजन विवाह प्रोत्साहन योजना", "cg_scheme_009"],
      ["दिव्यांगजन छात्रवृत्ति योजना", "cg_scheme_010"],
      ["दिव्यांग उच्च शिक्षा प्रोत्साहन योजना", "cg_scheme_011"],
      ["दिव्यांगजन सिविल सेवा प्रोत्साहन योजना", "cg_scheme_012"],
      ["दिव्यांगजन विद्यार्थियों के लिये छात्रावास योजना", "cg_scheme_013"],
      ["दिव्यांगजन हेतु शिविरों का आयोजन", "cg_scheme_014"],
      ["कृत्रिम अंग / सहायक उपकरण प्रदाय योजना", "cg_scheme_015"],
      ["राष्ट्रीय दिव्यांगजन पुनर्वास कार्यक्रम", "cg_scheme_016"],
      ["राष्ट्रीय परिवार सहायता योजना", "cg_scheme_007"],
      ["सुखद सहारा पेंशन योजना", "cg_scheme_002"],
      ["मुख्यमंत्री पेंशन योजना - 2018", "cg_scheme_003"],
      ["इंदिरा गांधी वृद्धावस्था पेंशन योजना", "cg_scheme_004"],
      ["इंदिरा गांधी राष्ट्रीय विधवा पेंशन योजना", "cg_scheme_005"],
      ["उभयलिंगी व्यक्तियों को टी.जी. कार्ड जारी करना", "cg_scheme_008"],
    ];
    for (const [schemeName, schemeId] of schemeMappings) {
      if (messageText.includes(schemeName)) {
        return schemeId;
      }
    }
    return null;
  };

  useEffect(() => {
    if (sender === "bot") {
      // ✅ 1. Welcome Message - STRICT CHECK - NO PDF
      const isWelcomeMessage = text.includes("Namaste!") && 
                               text.includes("Main JanSahayAI hoon") && 
                               text.includes("Aap mujhse pooch sakte hain");
      if (isWelcomeMessage) {
        setShowDownload(false);
        return;
      }

      // ✅ 2. TG Card (Special Case) - ALWAYS PDF
      const isTGCard = text.includes("उभयलिंगी व्यक्तियों को टी.जी. कार्ड जारी करना") ||
                       text.includes("टी.जी. कार्ड") ||
                       text.toLowerCase().includes("tg card") ||
                       text.toLowerCase().includes("transgender card");
      
      if (isTGCard) {
        setDetectedSchemeId("cg_scheme_008");
        setShowDownload(true);
        fetch("/forms/cg_scheme_008.pdf", { method: "HEAD" })
          .then((res) => setPdfExists(res.ok))
          .catch(() => setPdfExists(false));
        return;
      }

      // ✅ 3. Eligibility Check - PDF only if eligible
      const hasEligibility = text.includes("पात्र हैं") || text.includes("✅ **आप");
      const continuationPatterns = [
        "अन्य योजनाओं के लिए नंबर बताएं",
        "अन्य योजना के लिए नंबर बताएं",
        "कोई नंबर बताएं",
      ];
      const isContinuation = continuationPatterns.some((pattern) => text.includes(pattern));

      if (isContinuation && !hasEligibility) {
        setShowDownload(false);
        return;
      }

      if (hasEligibility) {
        let finalSchemeId: string | null = extractSchemeIdFromMessage(text);
        if (!finalSchemeId && scheme_id) {
          finalSchemeId = scheme_id;
        }
        if (finalSchemeId) {
          setDetectedSchemeId(finalSchemeId);
          setShowDownload(true);
          fetch(`/forms/${finalSchemeId}.pdf`, { method: "HEAD" })
            .then((res) => setPdfExists(res.ok))
            .catch(() => setPdfExists(false));
        }
      } else {
        setShowDownload(false);
      }
    }
  }, [sender, text, scheme_id]);

  const handleSpeak = () => {
    if (isPlaying) {
      stopSpeaking();
      setIsPlaying(false);
    } else {
      speak(text, "hi-IN");
      setIsPlaying(true);
      const interval = setInterval(() => {
        if (!window.speechSynthesis.speaking) {
          setIsPlaying(false);
          clearInterval(interval);
        }
      }, 500);
    }
  };

  const handleCopy = async () => {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleEditClick = () => {
    setIsEditing(true);
    setEditText(text);
  };

  const handleSaveEdit = () => {
    if (editText.trim() !== text && editText.trim() !== "") onEdit?.(editText.trim());
    setIsEditing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSaveEdit();
    }
    if (e.key === "Escape") {
      setIsEditing(false);
      setEditText(text);
    }
  };

  // Render message with bold text support (no ** will be visible)
  const renderMessage = () => {
    return (
      <div className="space-y-1.5">
        {text.split("\n").map((line, idx) => {
          const trimmed = line.trim();
          if (trimmed === "") return <div key={idx} className="h-1" />;
          if (trimmed.includes("━━━━")) return <div key={idx} className="border-t border-gray-200 my-2" />;
          
          // Convert **text** to <strong>text</strong> (removes ** from display)
          const formattedLine = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
          
          return (
            <div key={idx} className="text-gray-700 text-sm leading-relaxed">
              <span dangerouslySetInnerHTML={{ __html: formattedLine }} />
            </div>
          );
        })}
      </div>
    );
  };

  if (isEditing) {
    return (
      <div className={`flex ${sender === "user" ? "justify-end" : "justify-start"} animate-fadeIn`}>
        <div className={`max-w-[85%] rounded-2xl p-3 ${sender === "user" ? "bg-[#1E3A8A] text-white" : "bg-white border border-gray-200 text-gray-800"}`}>
          <textarea
            ref={textareaRef}
            value={editText}
            onChange={(e) => setEditText(e.target.value)}
            onKeyDown={handleKeyDown}
            onBlur={handleSaveEdit}
            className={`w-full p-2 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-[#1E3A8A] ${sender === "user" ? "bg-[#1E3A8A]/10 text-white" : "bg-gray-100 text-gray-800"} text-sm`}
            rows={1}
            autoFocus
          />
          <div className="text-[10px] text-center mt-2 opacity-70">⏎ Enter to save • Esc to cancel</div>
        </div>
      </div>
    );
  }

  return (
    <div className={`flex ${sender === "user" ? "justify-end" : "justify-start"} animate-fadeIn group`}>
      <div className={`relative max-w-[85%] rounded-2xl p-4 shadow-sm ${sender === "user" ? "bg-[#E0ECFF] text-gray-800 rounded-br-none" : "bg-white border border-gray-200 text-gray-800 rounded-bl-none"}`}>
        {renderMessage()}

        {showDownload && detectedSchemeId && (
          <div className="mt-3 pt-2 border-t border-gray-200">
            {pdfExists ? (
              <a
                href={`/forms/${detectedSchemeId}.pdf`}
                download
                className="inline-flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white text-sm font-medium px-4 py-2 rounded-lg transition-all duration-200 transform hover:scale-105"
                aria-label="आवेदन फॉर्म डाउनलोड करें"
              >
                <span className="text-base">📥</span>
                <span>डाउनलोड फॉर्म</span>
              </a>
            ) : (
              <button
                disabled
                className="inline-flex items-center gap-2 bg-gray-400 text-white text-sm font-medium px-4 py-2 rounded-lg cursor-not-allowed"
              >
                <span className="text-base">📥</span>
                <span>फॉर्म जल्द आ रहा है</span>
              </button>
            )}
            <p className="text-xs text-gray-500 mt-1">
              {pdfExists ? "फॉर्म डाउनलोड करें, प्रिंट करें और भरकर जमा करें" : "फॉर्म अपलोड किया जा रहा है। कृपया बाद में देखें।"}
            </p>
          </div>
        )}

        <div className={`flex items-center justify-end gap-2 mt-2 text-[10px] text-gray-400`}>
          <span>{new Date(timestamp).toLocaleTimeString("hi-IN", { hour: "2-digit", minute: "2-digit" })}</span>
          <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <button onClick={handleCopy} className="p-1 rounded hover:bg-black/10" aria-label="कॉपी करें">📋</button>
            {sender === "bot" && (
              <button onClick={handleSpeak} className="p-1 rounded hover:bg-black/10" aria-label="सुनें">{isPlaying ? "🔊" : "🔈"}</button>
            )}
            {sender === "user" && onEdit && (
              <button onClick={handleEditClick} className="p-1 rounded hover:bg-black/10" aria-label="एडिट करें">✏️</button>
            )}
            {onDelete && (
              <button onClick={onDelete} className="p-1 rounded hover:bg-black/10" aria-label="डिलीट करें">🗑️</button>
            )}
          </div>
        </div>

        {copied && (
          <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 bg-black text-white text-xs px-2 py-1 rounded whitespace-nowrap z-10">📋 कॉपी हो गया!</div>
        )}
      </div>
    </div>
  );
}