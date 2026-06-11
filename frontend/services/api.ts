// ============================================
// FILE: frontend/services/api.ts
// FIX 1: Send actual session_id to backend
// CHANGE: sessionId parameter properly used
// ============================================

export async function sendMessage(message: string, sessionId: string = "default") {
  try {
    const res = await fetch("http://127.0.0.1:8000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      // ✅ FIX: Send actual sessionId
      body: JSON.stringify({ message: message, session_id: sessionId }),
    });

    if (!res.ok) throw new Error("API Error");

    const data = await res.json();

    // Return complete response with scheme_id and is_eligible
    if (data.response) {
      return { 
        response: data.response,
        scheme_id: data.scheme_id,
        is_eligible: data.is_eligible
      };
    }
    else if (data.reply) {
      return { 
        response: data.reply,
        scheme_id: data.scheme_id,
        is_eligible: data.is_eligible
      };
    }
    else if (data.message) {
      return { 
        response: data.message,
        scheme_id: data.scheme_id,
        is_eligible: data.is_eligible
      };
    }
    else {
      return { 
        response: "मुझे समझ नहीं आया। कृपया फिर से पूछें।",
        scheme_id: undefined,
        is_eligible: false
      };
    }
  } catch (error) {
    console.error("API Error:", error);
    throw error;
  }
}