// app/voice-chat/layout.tsx
export default function VoiceChatLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="h-screen flex flex-col bg-gray-50 dark:bg-gray-900">
      {children}
    </div>
  )
}