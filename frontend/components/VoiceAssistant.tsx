// components/VoiceAssistant.tsx
"use client";

import { useState, useEffect, useRef } from "react";
import { speak, stopSpeaking } from "../services/speech";

interface VoiceAssistantProps {
  onCommand: (command: string) => void;
  isVoiceMode: boolean;
  onToggleVoiceMode: () => void;
  currentMode: "voice" | "normal";
  onNewChat?: () => void;
  onOpenHistory?: () => void;
  onLargeText?: () => void;
  onHighContrast?: () => void;
  onStopAudio?: () => void;
  onClearChat?: () => void;
}

export default function VoiceAssistant({
  onCommand,
  isVoiceMode,
  onToggleVoiceMode,
  onNewChat,
  onOpenHistory,
  onHighContrast,
  onStopAudio,
  onClearChat,
}: VoiceAssistantProps) {
  const [isListening, setIsListening] = useState(false);
  const [commandStatus, setCommandStatus] = useState("");
  const recognitionRef = useRef<any>(null);
  const isVoiceModeRef = useRef(isVoiceMode);

  useEffect(() => {
    isVoiceModeRef.current = isVoiceMode;
  }, [isVoiceMode]);

  const processVoiceCommand = (command: string) => {
    const normalized = command.toLowerCase().trim();

    if (normalized.includes("namaste") || normalized.includes("नमस्ते")) {
      speak("नमस्ते! मैं आपकी कैसे मदद कर सकता हूँ?", "hi-IN");
      onCommand("नमस्ते");
      setCommandStatus("✅ Namaste");
      setTimeout(() => setCommandStatus(""), 2000);
    } else if (normalized.includes("new chat") || normalized.includes("नई चैट")) {
      speak("नई चैट शुरू हो रही है", "hi-IN");
      if (onNewChat) onNewChat();
      onCommand("new_chat");
      setCommandStatus("✅ New Chat");
      setTimeout(() => setCommandStatus(""), 2000);
    } else if (normalized.includes("history") || normalized.includes("इतिहास")) {
      speak("चैट इतिहास खोल रहे हैं", "hi-IN");
      if (onOpenHistory) onOpenHistory();
      onCommand("open_history");
      setCommandStatus("✅ History");
      setTimeout(() => setCommandStatus(""), 2000);
    } else if (normalized.includes("high contrast") || normalized.includes("हाई कंट्रास्ट")) {
      speak("हाई कंट्रास्ट मोड", "hi-IN");
      if (onHighContrast) onHighContrast();
      onCommand("high_contrast");
      setCommandStatus("✅ High Contrast");
      setTimeout(() => setCommandStatus(""), 2000);
    } else if (normalized.includes("stop audio") || normalized.includes("आवाज बंद")) {
      speak("आवाज़ बंद की जा रही है", "hi-IN");
      if (onStopAudio) onStopAudio();
      stopSpeaking();
      onCommand("stop_audio");
      setCommandStatus("✅ Audio Off");
      setTimeout(() => setCommandStatus(""), 2000);
    } else if (normalized.includes("clear chat") || normalized.includes("चैट साफ़")) {
      speak("चैट साफ़ कर रहे हैं", "hi-IN");
      if (onClearChat) onClearChat();
      onCommand("clear_chat");
      setCommandStatus("✅ Chat Cleared");
      setTimeout(() => setCommandStatus(""), 2000);
    } else if (normalized.includes("time") || normalized.includes("समय")) {
      const now = new Date();
      const time = now.toLocaleTimeString("hi-IN", { hour: "2-digit", minute: "2-digit" });
      speak(`अभी समय ${time} है`, "hi-IN");
      onCommand(`समय ${time}`);
      setCommandStatus("✅ Time");
      setTimeout(() => setCommandStatus(""), 2000);
    } else if (normalized.includes("help") || normalized.includes("मदद")) {
      const helpText = "मैं ये काम कर सकता हूँ: नई चैट, इतिहास, हाई कंट्रास्ट, आवाज बंद, चैट साफ़, समय बताना";
      speak(helpText, "hi-IN");
      onCommand("help");
      setCommandStatus("✅ Help");
      setTimeout(() => setCommandStatus(""), 2000);
    } else if (normalized.includes("goodbye") || normalized.includes("अलविदा")) {
      speak("अलविदा, फिर मिलेंगे!", "hi-IN");
      onCommand("अलविदा");
      setCommandStatus("✅ Goodbye");
      setTimeout(() => setCommandStatus(""), 2000);
    } else if (command.length > 2) {
      onCommand(command);
      setCommandStatus(`✅ "${command.substring(0, 30)}..."`);
      setTimeout(() => setCommandStatus(""), 2500);
    }
  };

  useEffect(() => {
    if (typeof window !== "undefined") {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = "hi-IN";

        recognition.onresult = (event: any) => {
          let finalTranscript = "";
          for (let i = event.resultIndex; i < event.results.length; i++) {
            if (event.results[i].isFinal) finalTranscript += event.results[i][0].transcript;
          }
          if (finalTranscript && isVoiceModeRef.current) processVoiceCommand(finalTranscript);
        };

        recognition.onerror = (event: any) => {
          if (event.error === "no-speech") {
            setCommandStatus("कोई आवाज़ नहीं मिली");
            setTimeout(() => setCommandStatus(""), 2000);
          }
        };

        recognition.onend = () => {
          setIsListening(false);
          if (isVoiceModeRef.current && recognitionRef.current) {
            setTimeout(() => {
              if (isVoiceModeRef.current && recognitionRef.current) {
                try {
                  recognitionRef.current.start();
                  setIsListening(true);
                } catch (e) {}
              }
            }, 500);
          }
        };

        recognition.onstart = () => setIsListening(true);
        recognitionRef.current = recognition;
      }
    }
    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (e) {}
      }
    };
  }, []);

  useEffect(() => {
    if (isVoiceMode && recognitionRef.current) {
      try {
        recognitionRef.current.start();
        setIsListening(true);
        speak("वॉयस मोड चालू है", "hi-IN");
      } catch (e) {}
    } else if (!isVoiceMode && recognitionRef.current) {
      try {
        recognitionRef.current.stop();
        setIsListening(false);
      } catch (e) {}
    }
  }, [isVoiceMode]);

  return (
    <>
      <button
        onClick={onToggleVoiceMode}
        className={`fixed bottom-20 right-4 z-50 p-3 md:p-4 rounded-full shadow-lg transition-all transform hover:scale-110 ${
          isVoiceMode ? "bg-red-500 hover:bg-red-600 animate-pulse" : "bg-[#1E3A8A] hover:bg-[#1E3A8A]/90"
        }`}
      >
        {isListening ? <span className="text-xl">🎤</span> : <span className="text-xl">🎙️</span>}
      </button>

      {commandStatus && (
        <div className="fixed bottom-32 right-4 z-50 bg-black/80 text-white px-3 py-1.5 rounded-full text-xs animate-fadeIn">
          {commandStatus}
        </div>
      )}

      {isVoiceMode && (
        <div className="fixed top-4 right-4 z-50 bg-[#1E3A8A] text-white px-3 py-1.5 rounded-full text-xs flex items-center gap-2 shadow-lg">
          <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
          🎤 वॉयस मोड
        </div>
      )}
    </>
  );
}