// components/HistoryPanel.tsx
"use client";

import { useState, useMemo } from "react";

interface ChatSession {
  id: string;
  title: string;
  messages: any[];
  timestamp: string;
  preview: string;
}

interface Props {
  history: ChatSession[];
  currentSessionId: string | null;
  onSelect: (session: ChatSession) => void;
  onDelete?: (id: string) => void;
  onClearAll?: () => void;
  isMobile?: boolean;
}

function groupByDate(items: ChatSession[]) {
  const groups: { title: string; items: ChatSession[] }[] = [];
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);
  const weekAgo = new Date(today);
  weekAgo.setDate(weekAgo.getDate() - 7);

  const todayItems: ChatSession[] = [];
  const yesterdayItems: ChatSession[] = [];
  const weekItems: ChatSession[] = [];
  const olderItems: ChatSession[] = [];

  items.forEach((item) => {
    const date = new Date(item.timestamp);
    date.setHours(0, 0, 0, 0);
    if (date.getTime() === today.getTime()) todayItems.push(item);
    else if (date.getTime() === yesterday.getTime()) yesterdayItems.push(item);
    else if (date > weekAgo) weekItems.push(item);
    else olderItems.push(item);
  });

  if (todayItems.length) groups.push({ title: "आज", items: todayItems });
  if (yesterdayItems.length) groups.push({ title: "कल", items: yesterdayItems });
  if (weekItems.length) groups.push({ title: "पिछले 7 दिन", items: weekItems });
  if (olderItems.length) groups.push({ title: "पुराना", items: olderItems });
  return groups;
}

export default function HistoryPanel({ history, currentSessionId, onSelect, onDelete, onClearAll, isMobile }: Props) {
  const [hoverId, setHoverId] = useState<string | null>(null);
  const groups = useMemo(() => groupByDate(history), [history]);

  if (history.length === 0) {
    return (
      <div className="flex-1 p-6 text-center">
        <span className="text-3xl block mb-2">💬</span>
        <p className="text-xs text-gray-500">कोई इतिहास नहीं</p>
        <p className="text-[10px] text-gray-400 mt-1">नई चैट शुरू करें</p>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <div className="flex-1 overflow-y-auto px-3 pb-3">
        {groups.map((group, gidx) => (
          <div key={gidx} className="mb-4">
            <h3 className="text-[10px] font-semibold text-gray-400 mb-2 uppercase tracking-wider px-1">{group.title}</h3>
            <div className="space-y-1.5">
              {group.items.map((item) => (
                <div
                  key={item.id}
                  className="relative"
                  onMouseEnter={() => setHoverId(item.id)}
                  onMouseLeave={() => setHoverId(null)}
                >
                  <button
                    onClick={() => onSelect(item)}
                    className={`w-full text-left p-2.5 rounded-lg transition-all ${
                      currentSessionId === item.id
                        ? "bg-[#1E3A8A]/10 border-l-2 border-[#1E3A8A]"
                        : hoverId === item.id
                        ? "bg-gray-200"
                        : "hover:bg-gray-100"
                    }`}
                  >
                    <p className="text-sm font-medium text-gray-800 truncate">{item.title}</p>
                    <p className="text-[11px] text-gray-500 truncate mt-0.5">{item.preview || "कोई संदेश नहीं"}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <p className="text-[9px] text-gray-400">{new Date(item.timestamp).toLocaleDateString("hi-IN")}</p>
                      <p className="text-[9px] text-gray-400">• {item.messages.length}</p>
                    </div>
                  </button>

                  {onDelete && hoverId === item.id && currentSessionId !== item.id && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        if (confirm("यह चैट डिलीट करें?")) onDelete(item.id);
                      }}
                      className="absolute right-2 top-1/2 transform -translate-y-1/2 p-1 bg-red-500 text-white rounded text-xs shadow"
                    >
                      🗑️
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {onClearAll && history.length > 0 && (
        <div className="p-3 border-t border-[#E2E8F0]">
          <button onClick={onClearAll} className="w-full py-2 text-xs text-red-500 hover:text-red-700 transition-colors">
            🗑️ सभी हटाएं
          </button>
        </div>
      )}
    </div>
  );
}