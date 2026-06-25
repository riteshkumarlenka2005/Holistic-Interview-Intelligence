export { renderers } from '../../renderers.mjs';

const OPENROUTER_API_KEY = "";
const OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions";
const SITE_URL = "http://localhost:4321";
const QUESTION_POOLS = {
  Behavioral: [
    "Tell me about yourself and your background.",
    "Why are you interested in this position?",
    "What are your greatest strengths?",
    "Describe a challenging situation and how you handled it.",
    "Where do you see yourself in 5 years?",
    "Tell me about a time you showed leadership.",
    "How do you handle stress and pressure?",
    "Describe a time when you had to work with a difficult colleague.",
    "Give an example of a goal you set and how you achieved it.",
    "Tell me about a time you failed and what you learned.",
    "How do you prioritize tasks when you have multiple deadlines?",
    "Describe a situation where you had to adapt to change.",
    "Tell me about a time you went above and beyond.",
    "How do you handle conflict in the workplace?",
    "Describe your approach to problem-solving.",
    "Tell me about a time you received constructive criticism.",
    "How do you stay motivated during repetitive tasks?",
    "Describe a time you had to make a difficult decision.",
    "Tell me about your greatest professional achievement.",
    "How do you handle situations when you don't know the answer?"
  ],
  Technical: [
    "Explain your understanding of data structures and algorithms.",
    "Walk me through your approach to solving complex technical problems.",
    "Describe a challenging technical project you've worked on.",
    "How do you stay updated with new technologies?",
    "Explain the concept of object-oriented programming.",
    "What is your experience with version control systems?",
    "How do you approach debugging a difficult issue?",
    "Describe your experience with system design.",
    "What programming languages are you most proficient in?",
    "Explain the difference between SQL and NoSQL databases.",
    "How do you ensure code quality in your projects?",
    "Describe your experience with cloud platforms.",
    "What is your approach to writing clean, maintainable code?",
    "Explain the concept of API design and REST principles.",
    "How do you handle performance optimization?",
    "Describe your experience with testing methodologies.",
    "What is your understanding of microservices architecture?",
    "How do you approach learning a new programming language?",
    "Explain the importance of documentation in software development.",
    "Describe your experience with CI/CD pipelines."
  ],
  HR: [
    "Why do you want to work for our company?",
    "What motivates you in your career?",
    "How do you handle feedback and criticism?",
    "Describe your ideal work environment.",
    "What are your salary expectations?",
    "How do you prioritize work-life balance?",
    "Tell me about your career goals.",
    "Why are you leaving your current job?",
    "What do you know about our company culture?",
    "How would your previous colleagues describe you?",
    "What are your hobbies and interests outside of work?",
    "How do you handle working under tight deadlines?",
    "What makes you unique compared to other candidates?",
    "Describe your management style if you lead a team.",
    "How do you handle disagreements with your supervisor?",
    "What professional development activities do you pursue?",
    "How do you contribute to a positive team environment?",
    "What are your expectations from this role?",
    "How do you handle multiple competing priorities?",
    "What questions do you have for us?"
  ]
};
function getRandomFallbackQuestion(sessionType, previousQuestions = []) {
  const pool = QUESTION_POOLS[sessionType] || QUESTION_POOLS.Behavioral;
  const availableQuestions = pool.filter((q) => !previousQuestions.includes(q));
  if (availableQuestions.length === 0) {
    return pool[Math.floor(Math.random() * pool.length)];
  }
  return availableQuestions[Math.floor(Math.random() * availableQuestions.length)];
}
function buildSingleQuestionPrompt(sessionType, previousQuestions = []) {
  const sessionDescriptions = {
    Behavioral: "a behavioral interview question that assesses soft skills, teamwork, problem-solving abilities, leadership, or past experiences using the STAR method",
    Technical: "a technical interview question covering programming concepts, system design, algorithms, data structures, debugging approaches, or technology-specific knowledge",
    HR: "an HR interview question focusing on career goals, company culture fit, salary expectations, work preferences, motivation, or professional development"
  };
  const description = sessionDescriptions[sessionType] || sessionDescriptions.Behavioral;
  let prompt = `You are an expert interview coach. Generate exactly ONE ${description}.

Requirements:
- The question should be commonly asked in real interviews
- The question should be clear and professional
- Output ONLY the question itself, nothing else
- No numbering, no bullets, no prefixes
- Make it unique and different from typical questions`;
  if (previousQuestions.length > 0) {
    const recentQuestions = previousQuestions.slice(-5);
    prompt += `

Do NOT generate any of these questions (already asked):
${recentQuestions.map((q) => `- ${q}`).join("\n")}`;
  }
  prompt += `

Generate the question now:`;
  return prompt;
}
async function callOpenRouter(prompt) {
  const response = await fetch(OPENROUTER_BASE_URL, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${OPENROUTER_API_KEY}`,
      "Content-Type": "application/json",
      "HTTP-Referer": SITE_URL,
      "X-Title": "Holistic Interview Intelligence"
    },
    body: JSON.stringify({
      model: "google/gemini-2.0-flash-001",
      messages: [
        {
          role: "user",
          content: prompt
        }
      ],
      max_tokens: 200,
      temperature: 0.9
      // Higher temperature for more variety
    })
  });
  if (!response.ok) {
    const errorText = await response.text();
    console.error("[API] OpenRouter error response:", errorText);
    throw new Error(`OpenRouter API error: ${response.status} - ${errorText}`);
  }
  const data = await response.json();
  if (!data.choices || !data.choices[0] || !data.choices[0].message) {
    throw new Error("Invalid response structure from OpenRouter");
  }
  return data.choices[0].message.content.trim();
}
const POST = async ({ request }) => {
  let sessionType = "Behavioral";
  let previousQuestions = [];
  try {
    const body = await request.json();
    sessionType = body.sessionType || "Behavioral";
    previousQuestions = body.previousQuestions || [];
    console.log("[API] Generating single question for:", sessionType);
    const prompt = buildSingleQuestionPrompt(sessionType, previousQuestions);
    const question = await Promise.race([
      callOpenRouter(prompt),
      new Promise(
        (_, reject) => setTimeout(() => reject(new Error("Timeout")), 15e3)
      )
    ]);
    console.log("[API] Generated question:", question.substring(0, 50) + "...");
    let cleanQuestion = question.replace(/^\d+[.):\-]\s*/, "").replace(/^[-•*]\s*/, "").replace(/^\*\*/, "").replace(/\*\*$/, "").replace(/^["']|["']$/g, "").trim();
    if (!cleanQuestion || cleanQuestion.length < 10) {
      console.error("[API] Invalid question, using fallback");
      return new Response(JSON.stringify({
        question: getRandomFallbackQuestion(sessionType, previousQuestions),
        source: "fallback"
      }), {
        status: 200,
        headers: { "Content-Type": "application/json" }
      });
    }
    return new Response(JSON.stringify({
      question: cleanQuestion,
      source: "openrouter"
    }), {
      status: 200,
      headers: { "Content-Type": "application/json" }
    });
  } catch (error) {
    console.error("[API] Error generating question:", error);
    return new Response(JSON.stringify({
      question: getRandomFallbackQuestion(sessionType, previousQuestions),
      source: "fallback",
      error: error instanceof Error ? error.message : "Unknown error"
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
