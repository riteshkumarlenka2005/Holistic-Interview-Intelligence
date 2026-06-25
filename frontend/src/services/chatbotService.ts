/**
 * Chatbot Service
 * Frontend service to interact with the AI chatbot API
 */

export interface ChatMessage {
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
}

interface ChatResponse {
    message: string;
    success: boolean;
    error?: string;
}

/**
 * Send a message to the AI chatbot and get a response
 * @param message - The user's message
 * @param history - Previous conversation messages for context
 * @returns The assistant's response
 */
export async function sendChatMessage(
    message: string,
    history: ChatMessage[] = []
): Promise<ChatResponse> {
    try {
        console.log('[ChatbotService] Sending message:', message.substring(0, 30));

        const response = await fetch('/api/chatbot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message,
                history: history.map(msg => ({
                    role: msg.role,
                    content: msg.content
                }))
            }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data: ChatResponse = await response.json();

        console.log('[ChatbotService] Response received, success:', data.success);

        return data;

    } catch (error) {
        console.error('[ChatbotService] Error:', error);
        return {
            message: "Sorry, I couldn't connect to the server. Please check your connection and try again.",
            success: false,
            error: error instanceof Error ? error.message : 'Unknown error'
        };
    }
}

// Example conversation starters for the chatbot
export const CONVERSATION_STARTERS = [
    "How can I prepare for a technical interview?",
    "What are common behavioral interview questions?",
    "Tips for staying calm during interviews?",
    "How does the Live Practice feature work?",
];

export default {
    sendChatMessage,
    CONVERSATION_STARTERS
};
