// components/ChatInput.tsx
"use client";

import { useState, useRef, useEffect } from "react";
import VoiceButton from "./VoiceButton";

interface Props {
  onSend: (message: string) => void;
  placeholder?: string;
  isMobile?: boolean;
}

export default function ChatInput({ onSend, isMobile = false }: Props) {
  const [message, setMessage] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSend = () => {
    if (!message.trim()) return;
    onSend(message.trim());
    setMessage("");
    setTimeout(() => inputRef.current?.focus(), 0);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="relative w-full">
      <input
        ref={inputRef}
        type="text"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder="अपनी समस्या लिखें या योजना पूछें…"
        className="w-full border border-[#E2E8F0] rounded-full px-5 py-3.5 pr-24 text-sm focus:outline-none focus:ring-2 focus:ring-[#1E3A8A] focus:border-transparent bg-white text-gray-800 transition-all"
        aria-label="मैसेज टाइप करें"
      />
      <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex items-center gap-1">
        <VoiceButton onResult={onSend} language="hi-IN" isMobile={isMobile} />
        <button
          onClick={handleSend}
          disabled={!message.trim()}
          className="bg-[#16A34A] text-white px-5 py-2 rounded-full font-medium hover:bg-[#15803D] disabled:opacity-50 transition-all text-sm"
          aria-label="भेजें"
        >
          ➤
        </button>
      </div>
    </div>
  );
}