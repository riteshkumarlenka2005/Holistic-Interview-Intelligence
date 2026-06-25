/**
 * FAQSection Component
 * 
 * Premium FAQ accordion section with smooth animations and industrial design.
 * Fully responsive and theme-aware for light/dark modes.
 */
import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, HelpCircle } from 'lucide-react';

interface FAQItem {
    question: string;
    answer: string;
}

const faqData: FAQItem[] = [
    {
        question: "What is InterviewPro and how does it work?",
        answer: "InterviewPro is an AI-powered interview preparation platform that analyzes your verbal and non-verbal communication during practice sessions. You record yourself answering interview questions, and our advanced AI provides real-time feedback on your eye contact, facial expressions, voice modulation, and answer quality to help you improve."
    },
    {
        question: "Is my data safe and private?",
        answer: "Absolutely. We take privacy very seriously. All your recordings and personal data are encrypted end-to-end. We never share your data with third parties, and you can delete your data at any time. We are fully GDPR compliant and follow industry-best security practices."
    },
    {
        question: "What types of interviews can I practice?",
        answer: "InterviewPro supports a wide range of interview types including behavioral interviews, technical interviews, case studies, product management interviews, and general HR rounds. We have tailored question banks for different industries including tech, finance, consulting, and more."
    },
    {
        question: "Do I need any special equipment?",
        answer: "No special equipment is required! You just need a device with a camera and microphone – your laptop, tablet, or smartphone works perfectly. We recommend a quiet environment with good lighting for the best results."
    },
    {
        question: "How accurate is the AI feedback?",
        answer: "Our AI models are trained on thousands of real interviews and validated by professional recruiters. The feedback accuracy for communication metrics like eye contact and speech patterns exceeds 92%. We continuously improve our models based on user feedback and the latest research."
    },
    {
        question: "Can I track my progress over time?",
        answer: "Yes! InterviewPro provides detailed analytics dashboards that track your improvement across multiple dimensions – confidence scores, communication clarity, body language, and answer structure. You can see trends over time and identify areas that need more practice."
    },
    {
        question: "Is there a free trial available?",
        answer: "Yes, we offer a free tier that includes 3 practice sessions per month with basic feedback. Our premium plans unlock unlimited practice, advanced AI analysis, personalized coaching tips, and access to our entire question library."
    },
    {
        question: "How is InterviewPro different from other interview prep tools?",
        answer: "Unlike traditional platforms that focus only on content, InterviewPro analyzes the complete picture – how you communicate, not just what you say. Our multimodal AI evaluates synchrony between your verbal and non-verbal signals, providing holistic feedback that mirrors what real interviewers assess."
    }
];

const FAQItemComponent = ({ item, isOpen, onClick, index }: {
    item: FAQItem;
    isOpen: boolean;
    onClick: () => void;
    index: number;
}) => {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: index * 0.05 }}
            className="border-b border-border-color last:border-b-0"
        >
            <button
                onClick={onClick}
                className="w-full py-6 flex items-center justify-between text-left group focus:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 rounded-lg"
                aria-expanded={isOpen}
            >
                <span className="font-heading text-lg font-bold text-foreground dark:text-white pr-8 group-hover:text-primary transition-colors duration-300">
                    {item.question}
                </span>
                <motion.div
                    animate={{ rotate: isOpen ? 180 : 0 }}
                    transition={{ duration: 0.3, ease: "easeInOut" }}
                    className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 dark:bg-primary/20 flex items-center justify-center group-hover:bg-primary/20 dark:group-hover:bg-primary/30 transition-colors duration-300"
                >
                    <ChevronDown className="w-5 h-5 text-primary" />
                </motion.div>
            </button>

            <AnimatePresence initial={false}>
                {isOpen && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.3, ease: "easeInOut" }}
                        className="overflow-hidden"
                    >
                        <div className="pb-6 pr-12">
                            <p className="font-paragraph text-foreground-muted dark:text-foreground/80 leading-relaxed">
                                {item.answer}
                            </p>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    );
};

const FAQSection = () => {
    const [openIndex, setOpenIndex] = useState<number | null>(0);

    const handleClick = (index: number) => {
        setOpenIndex(openIndex === index ? null : index);
    };

    return (
        <section className="relative py-24 bg-background overflow-hidden">
            {/* Background decorations */}
            <div className="absolute inset-0 grid-pattern pointer-events-none" />
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-primary/5 dark:bg-primary/10 rounded-full blur-[120px] pointer-events-none" />

            <div className="max-w-4xl mx-auto px-6 lg:px-12 relative z-10">
                {/* Section Header */}
                <motion.div
                    className="text-center mb-16"
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6 }}
                >
                    <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 dark:bg-primary/20 rounded-full mb-6">
                        <HelpCircle className="w-4 h-4 text-primary" />
                        <span className="font-paragraph text-sm font-semibold text-primary uppercase tracking-wider">
                            Got Questions?
                        </span>
                    </div>

                    <h2 className="font-heading text-4xl lg:text-5xl font-black text-foreground dark:text-white mb-4">
                        Frequently Asked{' '}
                        <span className="text-primary">Questions</span>
                    </h2>

                    <p className="font-paragraph text-lg text-foreground-muted dark:text-foreground/70 max-w-2xl mx-auto">
                        Everything you need to know about InterviewPro. Can't find the answer you're looking for?
                        Feel free to contact our support team.
                    </p>
                </motion.div>

                {/* FAQ Accordion */}
                <motion.div
                    className="bg-card-bg dark:bg-card-bg/50 rounded-2xl border border-border-color shadow-premium p-6 lg:p-10"
                    initial={{ opacity: 0, y: 40 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6, delay: 0.2 }}
                >
                    {faqData.map((item, index) => (
                        <FAQItemComponent
                            key={index}
                            item={item}
                            isOpen={openIndex === index}
                            onClick={() => handleClick(index)}
                            index={index}
                        />
                    ))}
                </motion.div>

                {/* Contact CTA */}
                <motion.div
                    className="text-center mt-12"
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.5, delay: 0.4 }}
                >
                    <p className="font-paragraph text-foreground-muted dark:text-foreground/60 mb-4">
                        Still have questions?
                    </p>
                    <a
                        href="mailto:support@interviewpro.ai"
                        className="inline-flex items-center gap-2 px-6 py-3 bg-primary text-white font-paragraph font-semibold rounded-lg hover:bg-accent-purple transition-all duration-300 shadow-sm hover:shadow-md"
                    >
                        Contact Support
                    </a>
                </motion.div>
            </div>
        </section>
    );
};

export default FAQSection;
