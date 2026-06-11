"use client";

import { useState, useEffect } from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, PieChart, Pie, Cell, AreaChart, Area,
} from "recharts";

const API = "http://127.0.0.1:8000";

interface Overview {
  total_conversations: number;
  unique_users: number;
  total_messages: number;
  fallback_rate: number;
  success_rate: number;
  eligible_count: number;
  fallback_count: number;
  total_schemes: number;
  active_schemes: number;
}
interface IntentItem  { intent: string; label: string; count: number; }
interface SchemeItem  { scheme_id: string; scheme_name: string; count: number; }
interface DayItem     { date: string; label: string; count: number; }
interface QueryItem   { query: string; count: number; }
interface CatItem     { category: string; label: string; count: number; }

const COLORS = [
  "#6366f1","#8b5cf6","#06b6d4","#10b981",
  "#f59e0b","#ef4444","#ec4899","#14b8a6",
  "#f97316","#3b82f6","#a855f7","#22c55e",
];

const STAT_CARDS = [
  { key:"total_messages",     icon:"💬", label:"Total Messages",    subKey:"",               grad:"from-indigo-500 to-indigo-600",  bg:"from-indigo-50 to-indigo-100/60",  text:"text-indigo-600" },
  { key:"unique_users",       icon:"👥", label:"Unique Users",      subKey:"",               grad:"from-violet-500 to-purple-600",  bg:"from-violet-50 to-purple-100/60",  text:"text-violet-600" },
  { key:"eligible_count",     icon:"✅", label:"Eligible Users",    subKey:"success_rate",   grad:"from-emerald-500 to-teal-600",   bg:"from-emerald-50 to-teal-100/60",   text:"text-emerald-600" },
  { key:"fallback_count",     icon:"⚠️", label:"Fallback Count",   subKey:"fallback_rate",  grad:"from-orange-400 to-amber-500",   bg:"from-orange-50 to-amber-100/60",   text:"text-orange-500" },
  { key:"total_schemes",      icon:"📋", label:"Total Schemes",     subKey:"",               grad:"from-sky-500 to-blue-600",       bg:"from-sky-50 to-blue-100/60",       text:"text-sky-600" },
  { key:"active_schemes",     icon:"🟢", label:"Active Schemes",    subKey:"",               grad:"from-teal-500 to-cyan-600",      bg:"from-teal-50 to-cyan-100/60",      text:"text-teal-600" },
  { key:"inactive_schemes",   icon:"🔴", label:"Inactive Schemes",  subKey:"",               grad:"from-rose-400 to-red-500",       bg:"from-rose-50 to-red-100/60",       text:"text-rose-500" },
  { key:"total_conversations",icon:"🗣️",label:"Total Sessions",    subKey:"",               grad:"from-pink-500 to-fuchsia-600",   bg:"from-pink-50 to-fuchsia-100/60",   text:"text-pink-600" },
];

function getValue(key: string, ov: Overview | null): number {
  if (!ov) return 0;
  if (key === "inactive_schemes") return ov.total_schemes - ov.active_schemes;
  return (ov as any)[key] ?? 0;
}

function StatCard({ icon, label, value, subLabel, grad, bg, text }: {
  icon: string; label: string; value: number; subLabel: string;
  grad: string; bg: string; text: string;
}) {
  return (
    <div className={`relative overflow-hidden rounded-2xl bg-gradient-to-br ${bg} border border-white/80 shadow-sm hover:shadow-lg transition-all duration-300 group p-5 cursor-default`}>
      <div className={`absolute -right-5 -top-5 w-24 h-24 rounded-full bg-gradient-to-br ${grad} opacity-10 group-hover:opacity-20 transition-opacity duration-300`} />
      <div className={`absolute -right-3 -bottom-8 w-20 h-20 rounded-full bg-gradient-to-br ${grad} opacity-5`} />
      <div className="relative flex items-start justify-between">
        <div className="flex-1">
          <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-2">{label}</p>
          <p className={`text-3xl font-extrabold ${text} tabular-nums`}>{value.toLocaleString()}</p>
          {subLabel && <p className="text-xs text-gray-400 mt-1">{subLabel}</p>}
        </div>
        <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${grad} flex items-center justify-center text-xl shadow-lg flex-shrink-0`}>
          {icon}
        </div>
      </div>
    </div>
  );
}

function SectionCard({ title, children, className = "" }: {
  title: string; children: React.ReactNode; className?: string;
}) {
  return (
    <div className={`bg-white rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow duration-300 overflow-hidden ${className}`}>
      <div className="px-6 py-4 border-b border-gray-50 bg-gray-50/40">
        <h3 className="text-sm font-bold text-gray-700">{title}</h3>
      </div>
      <div className="p-6">{children}</div>
    </div>
  );
}

function CustomTooltip({ active, payload, label }: any) {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white border border-gray-100 rounded-xl shadow-xl px-4 py-3 text-sm">
        <p className="font-semibold text-gray-500 mb-1">{label}</p>
        <p className="text-indigo-600 font-extrabold text-xl">{payload[0].value}</p>
      </div>
    );
  }
  return null;
}

function EmptyState({ msg }: { msg: string }) {
  return (
    <div className="h-48 flex flex-col items-center justify-center gap-3 text-gray-300">
      <div className="text-5xl">📭</div>
      <p className="text-sm text-gray-400">{msg}</p>
    </div>
  );
}

export default function AnalyticsPage() {
  const [overview, setOverview]       = useState<Overview | null>(null);
  const [intents, setIntents]         = useState<IntentItem[]>([]);
  const [schemes, setSchemes]         = useState<SchemeItem[]>([]);
  const [daily, setDaily]             = useState<DayItem[]>([]);
  const [queries, setQueries]         = useState<QueryItem[]>([]);
  const [categories, setCategories]   = useState<CatItem[]>([]);
  const [loading, setLoading]         = useState(true);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());

  const fetchAll = async () => {
    setLoading(true);
    try {
      const [ov, in_, sc, da, qu, ca] = await Promise.all([
        fetch(`${API}/admin/analytics/overview`).then(r => r.json()),
        fetch(`${API}/admin/analytics/intents`).then(r => r.json()),
        fetch(`${API}/admin/analytics/schemes`).then(r => r.json()),
        fetch(`${API}/admin/analytics/daily`).then(r => r.json()),
        fetch(`${API}/admin/analytics/top-queries`).then(r => r.json()),
        fetch(`${API}/admin/analytics/categories`).then(r => r.json()),
      ]);
      setOverview(ov);
      setIntents(in_.data || []);
      setSchemes(sc.data || []);
      setDaily(da.data || []);
      setQueries(qu.data || []);
      setCategories(ca.data || []);
      setLastRefresh(new Date());
    } catch (e) {
      console.error("Analytics fetch error:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAll(); }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center space-y-4">
          <div className="relative w-16 h-16 mx-auto">
            <div className="w-16 h-16 border-4 border-indigo-100 rounded-full" />
            <div className="absolute inset-0 w-16 h-16 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin" />
          </div>
          <div>
            <p className="font-bold text-gray-700">Loading Analytics</p>
            <p className="text-sm text-gray-400 mt-1">Fetching latest data...</p>
          </div>
        </div>
      </div>
    );
  }

  const totalMsgs = overview?.total_messages ?? 1;
  const maxCat    = categories[0]?.count ?? 1;

  return (
    <div className="max-w-7xl mx-auto pb-16 space-y-6">

      {/* ── Header ─────────────────────────────────────────────────────────── */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-extrabold text-gray-900">📊 Analytics Dashboard</h1>
          <p className="text-sm text-gray-400 mt-0.5">JanSahayAI chatbot usage &amp; scheme insights</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="text-right hidden sm:block">
            <p className="text-[10px] text-gray-400 uppercase tracking-wide">Last refreshed</p>
            <p className="text-xs font-bold text-gray-600">{lastRefresh.toLocaleTimeString("hi-IN")}</p>
          </div>
          <button
            onClick={fetchAll}
            className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 text-white text-sm font-semibold rounded-xl hover:from-indigo-700 hover:to-purple-700 shadow-md hover:shadow-lg transition-all duration-200 active:scale-95"
          >
            🔄 Refresh
          </button>
        </div>
      </div>

      {/* ── Stat Cards ─────────────────────────────────────────────────────── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {STAT_CARDS.map((c) => {
          const val = getValue(c.key, overview);
          let subLabel = "";
          if (c.subKey === "success_rate") subLabel = `${overview?.success_rate ?? 0}% success rate`;
          else if (c.subKey === "fallback_rate") subLabel = `${overview?.fallback_rate ?? 0}% fallback rate`;
          return (
            <StatCard key={c.key} icon={c.icon} label={c.label} value={val}
              subLabel={subLabel} grad={c.grad} bg={c.bg} text={c.text} />
          );
        })}
      </div>

      {/* ── Charts Row 1: Activity + Intent ────────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-5">

        {/* Daily Activity */}
        <SectionCard title="📈 Last 7 Days Activity" className="lg:col-span-3">
          {daily.length === 0 || daily.every(d => d.count === 0) ? (
            <EmptyState msg="Nayi chats ke baad data dikhega" />
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={daily} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%"  stopColor="#6366f1" stopOpacity={0.2} />
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" vertical={false} />
                <XAxis dataKey="label" tick={{ fontSize: 11, fill: "#9ca3af" }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: "#9ca3af" }} axisLine={false} tickLine={false} />
                <Tooltip content={<CustomTooltip />} />
                <Area type="monotone" dataKey="count" stroke="#6366f1" strokeWidth={3}
                  fill="url(#areaGrad)"
                  dot={{ fill: "#6366f1", r: 5, strokeWidth: 2, stroke: "#fff" }}
                  activeDot={{ r: 7, strokeWidth: 0, fill: "#4f46e5" }} />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </SectionCard>

        {/* Intent Distribution */}
        <SectionCard title="🎯 Intent Distribution" className="lg:col-span-2">
          {intents.length === 0 ? (
            <EmptyState msg="Intent data nahi hai abhi" />
          ) : (
            <div className="space-y-4">
              <ResponsiveContainer width="100%" height={130}>
                <PieChart>
                  <Pie data={intents} dataKey="count" nameKey="label"
                    cx="50%" cy="50%" outerRadius={55} innerRadius={30} paddingAngle={3}>
                    {intents.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                  </Pie>
                  <Tooltip formatter={(v, n) => [v, n]} />
                </PieChart>
              </ResponsiveContainer>
              <div className="space-y-2">
                {intents.slice(0, 5).map((item, i) => (
                  <div key={i} className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full flex-shrink-0" style={{ backgroundColor: COLORS[i % COLORS.length] }} />
                    <span className="text-xs text-gray-500 flex-1 truncate">{item.label}</span>
                    <div className="w-16 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                      <div className="h-full rounded-full transition-all duration-700"
                        style={{ width: `${Math.min(100, Math.round((item.count / totalMsgs) * 100))}%`, backgroundColor: COLORS[i % COLORS.length] }} />
                    </div>
                    <span className="text-xs font-bold text-gray-700 w-6 text-right">{item.count}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </SectionCard>
      </div>

      {/* ── Charts Row 2: Schemes + Categories ─────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">

        {/* Most Viewed Schemes */}
        <SectionCard title="🔥 Most Viewed Schemes">
          {schemes.length === 0 ? (
            <EmptyState msg="Scheme data nahi hai abhi" />
          ) : (
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={schemes} layout="vertical" margin={{ left: 8, right: 20, top: 4, bottom: 4 }}>
                <defs>
                  <linearGradient id="barGrad" x1="0" y1="0" x2="1" y2="0">
                    <stop offset="0%"   stopColor="#6366f1" />
                    <stop offset="100%" stopColor="#8b5cf6" />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" horizontal={false} />
                <XAxis type="number" tick={{ fontSize: 11, fill: "#9ca3af" }} axisLine={false} tickLine={false} />
                <YAxis type="category" dataKey="scheme_name" tick={{ fontSize: 10, fill: "#6b7280" }}
                  width={145} tickFormatter={(v) => v.length > 20 ? v.slice(0, 20) + "…" : v}
                  axisLine={false} tickLine={false} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="count" fill="url(#barGrad)" radius={[0, 6, 6, 0]} maxBarSize={16} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </SectionCard>

        {/* Category Distribution — Horizontal Bar Style */}
        <SectionCard title="📂 Scheme Category Distribution">
          {categories.length === 0 ? (
            <EmptyState msg="Category data nahi hai abhi" />
          ) : (
            <div className="space-y-3 max-h-64 overflow-y-auto pr-1">
              {categories.map((item, i) => {
                const pct = Math.round((item.count / maxCat) * 100);
                return (
                  <div key={i} className="group">
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-2">
                        <div className="w-2.5 h-2.5 rounded-full flex-shrink-0 shadow-sm"
                          style={{ backgroundColor: COLORS[i % COLORS.length] }} />
                        <span className="text-xs font-medium text-gray-700">{item.label}</span>
                      </div>
                      <span className="text-xs font-bold text-gray-500 tabular-nums">{item.count}</span>
                    </div>
                    <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className="h-full rounded-full transition-all duration-700 group-hover:opacity-80"
                        style={{ width: `${pct}%`, backgroundColor: COLORS[i % COLORS.length] }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </SectionCard>
      </div>

      {/* ── Top Queries Table ───────────────────────────────────────────────── */}
      <SectionCard title="📋 Top 10 Most Asked Questions">
        {queries.length === 0 ? (
          <div className="py-12 flex flex-col items-center gap-3 text-gray-300">
            <div className="text-5xl">🔍</div>
            <p className="text-sm text-gray-400">Query data nahi hai — nayi chats ke baad dikhega</p>
          </div>
        ) : (
          <div className="overflow-hidden rounded-xl border border-gray-100">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gradient-to-r from-gray-50 to-white border-b border-gray-100">
                  <th className="text-left px-4 py-3.5 text-[10px] font-bold text-gray-400 uppercase tracking-widest w-12">#</th>
                  <th className="text-left px-4 py-3.5 text-[10px] font-bold text-gray-400 uppercase tracking-widest">Question</th>
                  <th className="text-right px-4 py-3.5 text-[10px] font-bold text-gray-400 uppercase tracking-widest w-28">Frequency</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {queries.map((q, i) => (
                  <tr key={i} className="hover:bg-indigo-50/40 transition-colors group">
                    <td className="px-4 py-3.5">
                      {i < 3 ? (
                        <span className="text-lg">{["🥇","🥈","🥉"][i]}</span>
                      ) : (
                        <span className="w-6 h-6 rounded-full bg-gray-100 text-gray-400 text-xs font-bold flex items-center justify-center">
                          {i + 1}
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3.5 text-gray-700 group-hover:text-indigo-700 transition-colors font-medium">
                      {q.query}
                    </td>
                    <td className="px-4 py-3.5 text-right">
                      <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-indigo-50 text-indigo-600 border border-indigo-100">
                        {q.count}×
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </SectionCard>

      {/* ── Info Banner ─────────────────────────────────────────────────────── */}
      <div className="flex items-start gap-4 p-5 bg-gradient-to-r from-blue-50 via-indigo-50 to-purple-50 border border-blue-100 rounded-2xl">
        <div className="w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center text-xl flex-shrink-0">ℹ️</div>
        <div>
          <p className="text-sm font-bold text-blue-800">Data Tracking Note</p>
          <p className="text-xs text-blue-600 mt-1 leading-relaxed">
            Intent, fallback aur eligibility data sirf nayi chats mein track hoga (logging add hone ke baad).
            Purane 133 messages mein yeh fields nahi hain — isliye abhi <strong>0</strong> dikh raha hai.
          </p>
        </div>
      </div>

    </div>
  );
}
