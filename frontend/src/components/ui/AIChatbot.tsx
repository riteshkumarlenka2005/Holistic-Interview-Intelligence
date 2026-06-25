/**
 * AI Chatbot Component
 * Floating chat widget for interview-related assistance
 */
import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageCircle, X, Send, Sparkles, Bot, User, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { sendChatMessage, CONVERSATION_STARTERS, type ChatMessage } from '@/services/chatbotService';

export default function AIChatbot() {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    // Scroll to bottom when messages change
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    // Focus input when chat opens
    useEffect(() => {
        if (isOpen) {
            setTimeout(() => inputRef.current?.focus(), 300);
        }
    }, [isOpen]);

    const handleSendMessage = async (message?: string) => {
        const messageToSend = message || inputValue.trim();
        if (!messageToSend || isLoading) return;

        // Add user message
        const userMessage: ChatMessage = {
            role: 'user',
            content: messageToSend,
            timestamp: new Date()
        };
        setMessages(prev => [...prev, userMessage]);
        setInputValue('');
        setIsLoading(true);

        // Get AI response
        const response = await sendChatMessage(messageToSend, messages);

        // Add assistant message
        const assistantMessage: ChatMessage = {
            role: 'assistant',
            content: response.message,
            timestamp: new Date()
        };
        setMessages(prev => [...prev, assistantMessage]);
        setIsLoading(false);
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    };

    return (
        <>
            {/* Floating Chat Button */}
            <AnimatePresence>
                {!isOpen && (
                    <motion.button
                        initial={{ scale: 0, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        exit={{ scale: 0, opacity: 0 }}
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => setIsOpen(true)}
                        className="fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full bg-gradient-to-br from-primary to-accent-purple shadow-lg shadow-primary/40 flex items-center justify-center text-white cursor-pointer group"
                        aria-label="Open AI Chat Assistant"
                    >
                        {/* Glow effect */}
                        <div className="absolute inset-0 rounded-full bg-gradient-to-br from-primary to-accent-purple blur-lg opacity-60 group-hover:opacity-80 transition-opacity" />

                        {/* Pulse animation */}
                        <div className="absolute inset-0 rounded-full bg-primary animate-ping opacity-30" />

                        <MessageCircle className="w-6 h-6 relative z-10" />

                        {/* Sparkle indicator */}
                        <motion.div
                            className="absolute -top-1 -right-1 w-5 h-5 bg-amber-400 rounded-full flex items-center justify-center"
                            animate={{ scale: [1, 1.2, 1] }}
                            transition={{ repeat: Infinity, duration: 2 }}
                        >
                            <Sparkles className="w-3 h-3 text-white" />
                        </motion.div>
                    </motion.button>
                )}
            </AnimatePresence>

            {/* Chat Panel */}
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0, y: 20, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: 20, scale: 0.95 }}
                        transition={{ type: 'spring', stiffness: 300, damping: 25 }}
                        className="fixed bottom-6 right-6 z-50 w-[380px] h-[520px] bg-card-bg/95 backdrop-blur-xl border border-border-color rounded-2xl shadow-2xl shadow-black/20 flex flex-col overflow-hidden"
                    >
                        {/* Header */}
                        <div className="bg-gradient-to-r from-primary to-accent-purple p-4 flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center">
                                    <Bot className="w-5 h-5 text-white" />
                                </div>
                                <div>
                                    <h3 className="font-heading font-bold text-white text-sm">Interview AI Assistant</h3>
                                    <p className="text-white/80 text-xs">Powered by Gemini</p>
                                </div>
                            </div>
                            <motion.button
                                whileHover={{ scale: 1.1, rotate: 90 }}
                                whileTap={{ scale: 0.95 }}
                                onClick={() => setIsOpen(false)}
                                className="w-8 h-8 bg-white/20 hover:bg-white/30 rounded-lg flex items-center justify-center text-white transition-colors"
                                aria-label="Close chat"
                            >
                                <X className="w-4 h-4" />
                            </motion.button>
                        </div>

                        {/* Messages Area */}
                        <div className="flex-1 overflow-y-auto p-4 space-y-4">
                            {messages.length === 0 ? (
                                <div className="h-full flex flex-col items-center justify-center text-center px-4">
                                    <div className="w-16 h-16 bg-gradient-to-br from-primary/20 to-accent-purple/20 rounded-2xl flex items-center justify-center mb-4">
                                        <Sparkles className="w-8 h-8 text-primary" />
                                    </div>
                                    <h4 className="font-heading font-bold text-foreground mb-2">How can I help you?</h4>
                                    <p className="text-muted text-sm mb-4">Ask me anything about interviews, career tips, or using the platform!</p>

                                    {/* Quick starters */}
                                    <div className="space-y-2 w-full">
                                        {CONVERSATION_STARTERS.map((starter, index) => (
                                            <motion.button
                                                key={index}
                                                initial={{ opacity: 0, y: 10 }}
                                                animate={{ opacity: 1, y: 0 }}
                                                transition={{ delay: index * 0.1 }}
                                                onClick={() => handleSendMessage(starter)}
                                                className="w-full p-3 text-left text-sm bg-secondary/80 hover:bg-secondary border border-border-color rounded-xl text-foreground transition-all hover:border-primary/50"
                                            >
                                                {starter}
                                            </motion.button>
                                        ))}
                                    </div>
                                </div>
                            ) : (
                                <>
                                    {messages.map((msg, index) => (
                                        <motion.div
                                            key={index}
                                            initial={{ opacity: 0, y: 10 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
                                        >
                                            <div className={`w-8 h-8 rounded-lg flex-shrink-0 flex items-center justify-center ${msg.role === 'user'
                                                    ? 'bg-gradient-to-br from-primary to-accent-purple'
                                                    : 'bg-secondary border border-border-color'
                                                }`}>
                                                {msg.role === 'user'
                                                    ? <User className="w-4 h-4 text-white" />
                                                    : <Bot className="w-4 h-4 text-primary" />
                                                }
                                            </div>
                                            <div className={`max-w-[75%] p-3 rounded-xl text-sm ${msg.role === 'user'
                                                    ? 'bg-gradient-to-br from-primary to-accent-purple text-white rounded-tr-sm'
                                                    : 'bg-secondary border border-border-color text-foreground rounded-tl-sm'
                                                }`}>
                                                {msg.content}
                                            </div>
                                        </motion.div>
                                    ))}

                                    {/* Loading indicator */}
                                    {isLoading && (
                                        <motion.div
                                            initial={{ opacity: 0, y: 10 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            className="flex gap-3"
                                        >
                                            <div className="w-8 h-8 rounded-lg bg-secondary border border-border-color flex items-center justify-center">
                                                <Bot className="w-4 h-4 text-primary" />
                                            </div>
                                            <div className="bg-secondary border border-border-color p-3 rounded-xl rounded-tl-sm">
                                                <div className="flex gap-1">
                                                    <motion.div
                                                        className="w-2 h-2 bg-primary rounded-full"
                                                        animate={{ y: [0, -5, 0] }}
                                                        transition={{ repeat: Infinity, duration: 0.6, delay: 0 }}
                                                    />
                                                    <motion.div
                                                        className="w-2 h-2 bg-primary rounded-full"
                                                        animate={{ y: [0, -5, 0] }}
                                                        transition={{ repeat: Infinity, duration: 0.6, delay: 0.1 }}
                                                    />
                                                    <motion.div
                                                        className="w-2 h-2 bg-primary rounded-full"
                                                        animate={{ y: [0, -5, 0] }}
                                                        transition={{ repeat: Infinity, duration: 0.6, delay: 0.2 }}
                                                    />
                                                </div>
                                            </div>
                                        </motion.div>
                                    )}
                                </>
                            )}
                            <div ref={messagesEndRef} />
                        </div>

                        {/* Input Area */}
                        <div className="p-4 border-t border-border-color bg-secondary/50">
                            <div className="flex gap-2">
                                <input
                                    ref={inputRef}
                                    type="text"
                                    value={inputValue}
                                    onChange={(e) => setInputValue(e.target.value)}
                                    onKeyPress={handleKeyPress}
                                    placeholder="Ask about interviews..."
                                    disabled={isLoading}
                                    className="flex-1 px-4 py-2.5 bg-card-bg border border-border-color rounded-xl text-sm text-foreground placeholder-muted focus:outline-none focus:border-primary/50 transition-colors disabled:opacity-50"
                                />
                                <Button
                                    onClick={() => handleSendMessage()}
                                    disabled={!inputValue.trim() || isLoading}
                                    className="w-10 h-10 p-0 bg-gradient-to-br from-primary to-accent-purple rounded-xl text-white disabled:opacity-50"
                                >
                                    {isLoading ? (
                                        <Loader2 className="w-4 h-4 animate-spin" />
                                    ) : (
                                        <Send className="w-4 h-4" />
                                    )}
                                </Button>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </>
    );
}
