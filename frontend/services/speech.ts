// services/speech.ts
let currentUtterance: SpeechSynthesisUtterance | null = null;

export function cleanTextForSpeech(text: string): string {
  if (!text) return "";
  let cleaned = text;
  cleaned = cleaned.replace(/[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}]/gu, "");
  cleaned = cleaned.replace(/\*\*([^*]+)\*\*/g, "$1");
  cleaned = cleaned.replace(/[•●○■□▪▫➡→]\s*/gm, "");
  cleaned = cleaned.replace(/[^\w\s\u0900-\u097F]/g, "");
  cleaned = cleaned.replace(/\s+/g, " ");
  return cleaned.trim();
}

export function speak(text: string, lang: string = "hi-IN") {
  if (typeof window === "undefined" || !window.speechSynthesis) return;

  const cleanText = cleanTextForSpeech(text);
  if (!cleanText.trim()) return;

  stopSpeaking();

  const utterance = new SpeechSynthesisUtterance(cleanText);
  utterance.lang = lang;
  utterance.rate = 0.85;
  utterance.pitch = 1;
  utterance.volume = 1;

  const setVoice = () => {
    const voices = window.speechSynthesis.getVoices();
    let hindiVoice = voices.find((voice) => voice.lang.includes("hi") || voice.lang.includes("hin"));
    if (!hindiVoice) hindiVoice = voices.find((voice) => voice.lang.includes("en-IN"));
    if (hindiVoice) utterance.voice = hindiVoice;
  };

  if (window.speechSynthesis.getVoices().length > 0) setVoice();
  else window.speechSynthesis.onvoiceschanged = setVoice;

  utterance.onend = () => {
    currentUtterance = null;
  };

  utterance.onerror = () => {
    currentUtterance = null;
  };

  currentUtterance = utterance;
  window.speechSynthesis.speak(utterance);
}

export function stopSpeaking() {
  if (typeof window !== "undefined" && window.speechSynthesis) {
    window.speechSynthesis.cancel();
    currentUtterance = null;
  }
}

export function isSpeaking(): boolean {
  return typeof window !== "undefined" && window.speechSynthesis && window.speechSynthesis.speaking;
}