// components/VoiceMicButton.tsx
"use client"

interface VoiceMicButtonProps {
  onStart: () => void
  isRecording: boolean
  disabled?: boolean
}

export default function VoiceMicButton({ onStart, isRecording, disabled }: VoiceMicButtonProps) {
  return (
    <button
      onClick={onStart}
      disabled={disabled || isRecording}
      className={`p-4 rounded-xl transition-all transform hover:scale-105 shadow-lg ${
        isRecording 
          ? "bg-red-600 hover:bg-red-700 animate-pulse" 
          : "bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
      } disabled:opacity-50 disabled:scale-100`}
      aria-label={isRecording ? "सुन रहा हूँ..." : "बोलें"}
    >
      {isRecording ? (
        <div className="relative">
          <span className="text-2xl">⏹️</span>
          <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-300 rounded-full animate-ping"></span>
        </div>
      ) : (
        <span className="text-2xl">🎤</span>
      )}
    </button>
  )
}