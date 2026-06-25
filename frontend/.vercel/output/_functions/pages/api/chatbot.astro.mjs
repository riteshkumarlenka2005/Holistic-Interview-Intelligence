export { renderers } from '../../renderers.mjs';

const OPENROUTER_API_KEY = "";
const OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions";
const SITE_URL = "http://localhost:4321";
const SYSTEM_PROMPT = `You are an expert interview coach and career advisor for the Holistic Interview Intelligence platform. Your role is to help users prepare for interviews and succeed in their job search.

IMPORTANT RULES:
1. ONLY respond to questions related to:
   - Interview preparation and tips
   - Common interview questions and how to answer them
   - Resume and cover letter advice
   - Career guidance and job search strategies
   - Behavioral interview techniques (STAR method)
   - Technical interview preparation
   - HR interview best practices
   - Body language and communication tips
   - Salary negotiation
   - Follow-up etiquette
   - Using the Holistic Interview Intelligence platform features

2. If a user asks about topics unrelated to interviews or careers, politely redirect them:
   "I'm here to help you ace your interviews! While I can't help with that topic, I'd be happy to assist with interview prep, resume tips, or career advice. What would you like to know?"

3. Keep responses concise, actionable, and encouraging.

4. When explaining the platform features, mention:
   - Live Practice Sessions with AI-powered analysis
   - Real-time emotion and confidence detection
   - AI-generated interview questions
   - Progress tracking and performance analytics
   - Resource library with guides and tips`;
const POST = async ({ request }) => {
  try {
    const body = await request.json();
    const userMessage = body.message || "";
    const conversationHistory = body.history || [];
    if (!userMessage.trim()) {
      return new Response(JSON.stringify({
        error: "Message is required"
      }), {
        status: 400,
        headers: { "Content-Type": "application/json" }
      });
    }
    console.log("[Chatbot API] Processing message:", userMessage.substring(0, 50));
    const messages = [
      {
        role: "system",
        content: SYSTEM_PROMPT
      }
    ];
    for (const msg of conversationHistory) {
      messages.push({
        role: msg.role,
        content: msg.content
      });
    }
    messages.push({
      role: "user",
      content: userMessage
    });
    console.log("[Chatbot API] Calling OpenRouter API...");
    const response = await fetch(OPENROUTER_BASE_URL, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${OPENROUTER_API_KEY}`,
        "Content-Type": "application/json",
        "HTTP-Referer": SITE_URL,
        "X-Title": "Holistic Interview Intelligence Chatbot"
      },
      body: JSON.stringify({
        model: "google/gemini-2.0-flash-001",
        messages,
        max_tokens: 500,
        temperature: 0.7
      })
    });
    const responseText = await response.text();
    console.log("[Chatbot API] Response status:", response.status);
    if (!response.ok) {
      console.error("[Chatbot API] OpenRouter API error:", responseText);
      throw new Error(`API error: ${response.status}`);
    }
    const data = JSON.parse(responseText);
    if (!data.choices || !data.choices[0]?.message?.content) {
      console.error("[Chatbot API] Invalid response structure:", JSON.stringify(data));
      throw new Error("Invalid response structure");
    }
    const assistantMessage = data.choices[0].message.content.trim();
    console.log("[Chatbot API] Response generated successfully");
    return new Response(JSON.stringify({
      message: assistantMessage,
      success: true
    }), {
      status: 200,
      headers: { "Content-Type": "application/json" }
    });
  } catch (error) {
    console.error("[Chatbot API] Error:", error);
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    return new Response(JSON.stringify({
      message: "I'm having trouble connecting right now. Please try again in a moment. In the meantime, feel free to explore our Practice Sessions or Resource Library!",
      success: false,
      error: errorMessage
    }), {
      status: 200,
      headers: { "Content-Type": "application/json" }
    });
  }
};

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
   __proto__: null,
   POST
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
