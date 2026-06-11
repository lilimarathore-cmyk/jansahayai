// components/AccessibilityControls.tsx
"use client";

interface Props {
  highContrast: boolean;
  setHighContrast: (value: boolean) => void;
  isMobile?: boolean;
  onStopAudio?: () => void;
}

export default function AccessibilityControls({ highContrast, setHighContrast, isMobile = false, onStopAudio }: Props) {
  return (
    <div className="space-y-2 mt-2">
      <button
        onClick={() => setHighContrast(!highContrast)}
        className={`flex items-center gap-2 w-full justify-center px-3 py-2 rounded-lg text-sm font-medium transition-all ${
          highContrast ? "bg-yellow-500 text-black" : "bg-gray-200 text-gray-700 hover:bg-gray-300"
        }`}
      >
        <span>🌙</span> हाई कंट्रास्ट
      </button>
      <button
        onClick={onStopAudio}
        className="flex items-center gap-2 w-full justify-center px-3 py-2 rounded-lg text-sm font-medium bg-gray-200 text-gray-700 hover:bg-gray-300 transition-all"
      >
        <span>🔇</span> आवाज बंद
      </button>
    </div>
  );
}