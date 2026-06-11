// frontend/app/landing.tsx
'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { useRouter } from 'next/navigation';

export default function LandingPage() {
  const router = useRouter();
  const [isListening, setIsListening] = useState(false);
  const [status, setStatus] = useState('');
  const [statusType, setStatusType] = useState('');
  const [selectedOption, setSelectedOption] = useState<string | null>(null);
  const recognitionRef = useRef<any>(null);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  // ============ AUDIO FEEDBACK ============
  const playSound = useCallback((type: string) => {
    try {
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();
      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);

      switch (type) {
        case 'welcome':
          oscillator.type = 'sine';
          oscillator.frequency.setValueAtTime(523, audioContext.currentTime);
          oscillator.frequency.setValueAtTime(659, audioContext.currentTime + 0.1);
          oscillator.frequency.setValueAtTime(784, audioContext.currentTime + 0.2);
          gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
          gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
          oscillator.start(audioContext.currentTime);
          oscillator.stop(audioContext.currentTime + 0.5);
          break;
        case 'ding':
          oscillator.type = 'sine';
          oscillator.frequency.setValueAtTime(880, audioContext.currentTime);
          gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
          gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.2);
          oscillator.start(audioContext.currentTime);
          oscillator.stop(audioContext.currentTime + 0.2);
          break;
        case 'error':
          oscillator.type = 'square';
          oscillator.frequency.setValueAtTime(200, audioContext.currentTime);
          gainNode.gain.setValueAtTime(0.2, audioContext.currentTime);
          gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);
          oscillator.start(audioContext.currentTime);
          oscillator.stop(audioContext.currentTime + 0.3);
          break;
      }
    } catch (e) {
      console.log('Audio not supported');
    }
  }, []);

  // ============ VOICE INSTRUCTIONS ============
  const speakInstructions = useCallback(() => {
    if ('speechSynthesis' in window) {
      const instructions = `JanSahayAI mein aapka swagat hai. Yeh Chhattisgarh sarkar ki yojnaon ki jankari dene wala sahayak hai. Aapke paas do options hain. Option 1: Voice Assistant. Isme aap sirf bolkar baat kar sakte hain. Option 2: Chat Assistant. Isme aap likhkar ya bolkar baat kar sakte hain. Voice Assistant ke liye ONE bolein ya 1 press karein. Chat Assistant ke liye TWO bolein ya 2 press karein.`;
      
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(instructions);
      utterance.lang = 'hi-IN';
      utterance.rate = 0.9;
      window.speechSynthesis.speak(utterance);
    }
  }, []);

  // ============ VOICE RECOGNITION ============
  const startVoiceRecognition = useCallback(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
      console.log('Voice recognition not supported');
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = 'hi-IN';
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => {
      setIsListening(true);
    };

    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript.toLowerCase().trim();
      console.log('User said:', transcript);
      
      const voicePatterns = ['one', '1', 'वन', 'एक', 'voice', 'वॉइस', 'first', 'पहला'];
      const chatPatterns = ['two', '2', 'टू', 'दो', 'chat', 'चैट', 'second', 'दूसरा', 'text', 'टेक्स्ट'];

      let option: string | null = null;
      
      for (const pattern of voicePatterns) {
        if (transcript.includes(pattern)) { option = '1'; break; }
      }
      if (!option) {
        for (const pattern of chatPatterns) {
          if (transcript.includes(pattern)) { option = '2'; break; }
        }
      }

      if (option) {
        selectOption(option);
      } else {
        playSound('error');
        setStatus('Samajh nahi aaya. "One" ya "Two" bolein.');
        setStatusType('error');
        setTimeout(() => {
          setStatus('');
          if (!selectedOption) startVoiceRecognition();
        }, 2000);
      }
    };

    recognition.onerror = (event: any) => {
      console.log('Recognition error:', event.error);
      setIsListening(false);
      if (!selectedOption) {
        setTimeout(() => startVoiceRecognition(), 1000);
      }
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognition.start();
    recognitionRef.current = recognition;

    timeoutRef.current = setTimeout(() => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
        setIsListening(false);
      }
    }, 10000);
  }, [selectedOption, playSound]);

  // ============ SELECT OPTION ============
  const selectOption = useCallback((option: string) => {
    if (selectedOption) return;
    
    setSelectedOption(option);
    setIsListening(false);
    
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    if (recognitionRef.current) recognitionRef.current.stop();
    
    playSound('ding');
    
    const modeName = option === '1' ? 'Voice Assistant' : 'Chat Assistant';
    setStatus(`${modeName} mode activated. Opening...`);
    setStatusType('success');

    if ('speechSynthesis' in window) {
      const msg = option === '1' 
        ? 'Voice Assistant mode activated. Aap apni samasya batayen.'
        : 'Chat Assistant mode activated.';
      const utterance = new SpeechSynthesisUtterance(msg);
      utterance.lang = 'hi-IN';
      utterance.rate = 0.9;
      window.speechSynthesis.cancel();
      window.speechSynthesis.speak(utterance);
    }

    setTimeout(() => {
      const page = option === '1' ? '/voice_chat' : '/chat';
      router.push(page);
    }, 800);
  }, [selectedOption, router, playSound]);

  // ============ KEYBOARD HANDLER ============
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === '1' || e.key === '2') {
        e.preventDefault();
        selectOption(e.key);
      } else if (e.key === 'Escape' && isListening) {
        setIsListening(false);
        if (recognitionRef.current) recognitionRef.current.stop();
        setStatus('Cancelled. Press 1 or 2.');
        setStatusType('error');
        setTimeout(() => setStatus(''), 2000);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isListening, selectOption]);

  // ============ INITIALIZE ============
  useEffect(() => {
    console.log('🚀 Landing Page Initialized');
    
    setTimeout(() => playSound('welcome'), 300);
    setTimeout(() => speakInstructions(), 800);
    setTimeout(() => startVoiceRecognition(), 5000);

    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      if (recognitionRef.current) recognitionRef.current.stop();
    };
  }, [playSound, speakInstructions, startVoiceRecognition]);

  return (
    <main className="min-h-screen bg-[#0a0a0a] flex items-center justify-center p-6">
      <div className="text-center w-full max-w-[500px]">
        
        {/* Header */}
        <div className="mb-10 animate-fade-in-down">
          <div className="text-6xl mb-3 animate-pulse">🙏</div>
          <h1 className="text-4xl font-bold text-[#FFD700] mb-2" style={{ textShadow: '0 0 20px rgba(255,215,0,0.3)' }}>
            JanSahayAI
          </h1>
          <p className="text-lg text-gray-400 tracking-wide">छत्तीसगढ़ सरकार योजना सहायक</p>
        </div>

        {/* Cards */}
        <div className="flex flex-col gap-5 mb-8">
          
          {/* Voice Card */}
          <button
            onClick={() => selectOption('1')}
            className={`w-full bg-[#1a1a1a] border-3 rounded-2xl p-8 flex items-center gap-6 text-left transition-all duration-300 outline-none
              ${selectedOption === '1' 
                ? 'border-[#FFD700] scale-105 shadow-[0_0_50px_rgba(255,215,0,0.6)]' 
                : 'border-[#FF6B6B] hover:border-[#ff4444] hover:scale-[1.03] hover:shadow-[0_0_40px_rgba(255,107,107,0.4)]'
              }
              focus-visible:border-[#FFD700] focus-visible:shadow-[0_0_30px_rgba(255,215,0,0.5)] focus-visible:outline-3 focus-visible:outline-[#FFD700] focus-visible:outline-offset-4
            `}
            aria-label="Voice Assistant. दिव्यांग के लिए. Press 1 or say One."
          >
            <div className="w-16 h-16 rounded-full bg-[#FF6B6B] flex items-center justify-center text-3xl font-bold text-black shrink-0 shadow-lg">
              1
            </div>
            <div className="flex-1">
              <span className="text-4xl block mb-1">🎤</span>
              <h2 className="text-xl font-bold text-white mb-1">Voice Assistant</h2>
              <p className="text-sm text-gray-500">बोलकर बात करें • दिव्यांग के लिए</p>
              <span className="inline-block mt-2 px-3 py-1 bg-white/10 rounded-full text-xs text-gray-400">
                Press <kbd className="bg-[#333] px-1.5 py-0.5 rounded text-white">1</kbd> or Say "One"
              </span>
              <br />
              <span className="inline-block mt-1 px-2 py-0.5 bg-[#FF6B6B]/20 rounded-lg text-xs font-bold text-[#FF6B6B]">
                ♿ Accessible
              </span>
            </div>
          </button>

          {/* Chat Card */}
          <button
            onClick={() => selectOption('2')}
            className={`w-full bg-[#1a1a1a] border-3 rounded-2xl p-8 flex items-center gap-6 text-left transition-all duration-300 outline-none
              ${selectedOption === '2' 
                ? 'border-[#FFD700] scale-105 shadow-[0_0_50px_rgba(255,215,0,0.6)]' 
                : 'border-[#4ECDC4] hover:border-[#3dbdb5] hover:scale-[1.03] hover:shadow-[0_0_40px_rgba(78,205,196,0.4)]'
              }
              focus-visible:border-[#FFD700] focus-visible:shadow-[0_0_30px_rgba(255,215,0,0.5)] focus-visible:outline-3 focus-visible:outline-[#FFD700] focus-visible:outline-offset-4
            `}
            aria-label="Chat Assistant. सभी के लिए. Press 2 or say Two."
          >
            <div className="w-16 h-16 rounded-full bg-[#4ECDC4] flex items-center justify-center text-3xl font-bold text-black shrink-0 shadow-lg">
              2
            </div>
            <div className="flex-1">
              <span className="text-4xl block mb-1">💬</span>
              <h2 className="text-xl font-bold text-white mb-1">Chat Assistant</h2>
              <p className="text-sm text-gray-500">लिखकर या बोलकर बात करें • सभी के लिए</p>
              <span className="inline-block mt-2 px-3 py-1 bg-white/10 rounded-full text-xs text-gray-400">
                Press <kbd className="bg-[#333] px-1.5 py-0.5 rounded text-white">2</kbd> or Say "Two"
              </span>
            </div>
          </button>
        </div>

        {/* Listening Indicator */}
        {isListening && (
          <div className="mt-5 animate-fade-in">
            <div className="flex justify-center gap-2.5 mb-4">
              {[0, 1, 2].map((i) => (
                <span
                  key={i}
                  className="w-3.5 h-3.5 rounded-full bg-[#FFD700] animate-bounce"
                  style={{ animationDelay: `${-i * 0.16}s` }}
                />
              ))}
            </div>
            <p className="text-[#FFD700] text-lg">🎤 Listening... "One" ya "Two" bolein</p>
          </div>
        )}

        {/* Status Bar */}
        {status && (
          <div
            className={`fixed top-0 left-0 right-0 p-2 text-center text-sm z-50 ${
              statusType === 'error' ? 'bg-[#ff4444] text-white' : 'bg-[#4CAF50] text-white'
            }`}
            role="alert"
            aria-live="assertive"
          >
            {status}
          </div>
        )}

        {/* Footer */}
        <footer className="text-sm text-gray-600">
          <p>कीबोर्ड: <kbd className="bg-[#333] px-1.5 py-0.5 rounded text-gray-300">1</kbd> या <kbd className="bg-[#333] px-1.5 py-0.5 rounded text-gray-300">2</kbd> दबाएं</p>
        </footer>
      </div>

      <style jsx global>{`
        @keyframes fade-in-down {
          from { opacity: 0; transform: translateY(-30px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes fade-in {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        .animate-fade-in-down { animation: fade-in-down 0.8s ease; }
        .animate-fade-in { animation: fade-in 0.5s ease; }
      `}</style>
    </main>
  );
}