/**
 * AI Service for Interview Question Generation
 * 
 * Calls the server-side API endpoint to generate questions
 * one at a time for unlimited question flow.
 */

/**
 * Generate a SINGLE new interview question using AI
 * @param sessionType - The type of interview session (Behavioral, Technical, HR)
 * @param previousQuestions - Array of previously asked questions to avoid repeats
 * @returns A single interview question
 */
export async function generateSingleQuestion(
    sessionType: string,
    previousQuestions: string[] = []
): Promise<{ question: string; source: string }> {
    try {
        console.log('[GeminiService] Requesting new question for:', sessionType);

        const response = await fetch('/api/generate-questions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ sessionType, previousQuestions }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        console.log('[GeminiService] Received question, source:', data.source);

        return {
            question: data.question || getRandomFallbackQuestion(sessionType),
            source: data.source || 'fallback'
        };
    } catch (error) {
        console.error('[GeminiService] Error calling server API:', error);
        return {
            question: getRandomFallbackQuestion(sessionType),
            source: 'fallback'
        };
    }
}

// Fallback questions for emergency use
const FALLBACK_QUESTIONS: Record<string, string[]> = {
    Behavioral: [
        "Tell me about yourself and your background.",
        "Why are you interested in this position?",
        "What are your greatest strengths?",
        "Describe a challenging situation and how you handled it.",
        "Where do you see yourself in 5 years?",
        "Tell me about a time you showed leadership.",
        "How do you handle stress and pressure?",
        "Describe a time when you had to work with a difficult colleague.",
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
    ]
};

function getRandomFallbackQuestion(sessionType: string): string {
    const pool = FALLBACK_QUESTIONS[sessionType] || FALLBACK_QUESTIONS.Behavioral;
    return pool[Math.floor(Math.random() * pool.length)];
}

// Legacy function for backwards compatibility
export async function generateInterviewQuestions(
    sessionType: string,
    count: number = 8
): Promise<string[]> {
    // Generate first question
    const result = await generateSingleQuestion(sessionType, []);
    return [result.question];
}

export function getFallbackQuestions(sessionType: string): string[] {
    return FALLBACK_QUESTIONS[sessionType] || FALLBACK_QUESTIONS.Behavioral;
}

export default {
    generateSingleQuestion,
    generateInterviewQuestions,
    getFallbackQuestions
};
