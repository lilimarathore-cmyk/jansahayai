// components/VoiceButton.tsx
"use client";

import { useState, useEffect, useRef } from "react";

interface Props {
  onResult: (text: string) => void;
  language?: string;
  isMobile?: boolean;
}

export default function VoiceButton({ onResult, language = "hi-IN", isMobile = false }: Props) {
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    if (typeof window !== "undefined") {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

      if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = language;

        recognition.onstart = () => setIsListening(true);
        recognition.onend = () => setIsListening(false);
        recognition.onerror = (event: any) => {
          console.error("Voice error:", event.error);
          setIsListening(false);
          if (event.error === "not-allowed") alert("कृपया माइक्रोफोन परमिशन दें");
        };
        recognition.onresult = (event: any) => {
          const text = event.results[0][0].transcript;
          console.log("Voice input:", text);
          onResult(text);
        };
        recognitionRef.current = recognition;
      } else {
        alert("आपका ब्राउज़र वॉयस इनपुट सपोर्ट नहीं करता। कृपया Chrome या Edge इस्तेमाल करें।");
      }
    }
  }, [language, onResult]);

  const toggleListening = () => {
    if (!recognitionRef.current) return;
    if (isListening) recognitionRef.current.stop();
    else recognitionRef.current.start();
  };

  return (
    <button
      onClick={toggleListening}
      className={`p-2 rounded-full transition-all ${
        isListening ? "bg-red-600 text-white animate-pulse" : "text-[#1E3A8A] hover:bg-gray-100"
      }`}
      aria-label={isListening ? "सुनना बंद करें" : "बोलें"}
    >
      {isListening ? "⏹️" : "🎤"}
    </button>
  );
}