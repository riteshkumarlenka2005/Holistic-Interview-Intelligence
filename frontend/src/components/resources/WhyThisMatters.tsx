/**
 * WhyThisMatters Component
 * Explains relevance and real-world application of the resource
 */
import { motion } from 'framer-motion';
import { HelpCircle, CheckCircle2, Target, Briefcase, MessageSquare } from 'lucide-react';
import { LearningResources } from '@/entities';

interface WhyThisMattersProps {
    resource: LearningResources;
    skillFocus: string;
}

// Generate contextual "Why This Matters" content
function generateWhyContent(skillFocus: string): {
    whyImportant: string;
    whenToUse: string[];
    realScenarios: string[];
} {
    const content: Record<string, {
        whyImportant: string;
        whenToUse: string[];
        realScenarios: string[];
    }> = {
        'Confidence': {
            whyImportant: 'Confidence is often the deciding factor between equally qualified candidates. Interviewers perceive confident candidates as more competent, trustworthy, and capable of handling challenges.',
            whenToUse: [
                'Opening moments when making first impressions',
                'Answering unexpected or challenging questions',
                'Discussing achievements without sounding arrogant',
                'Negotiating salary or asking about growth'
            ],
            realScenarios: [
                '"Tell me about yourself" - Your opening sets the tone for the entire interview',
                'When asked about a failure - Confident recovery shows resilience',
                'Salary discussions - Confidence signals you know your worth'
            ]
        },
        'STAR Method': {
            whyImportant: 'The STAR method transforms rambling answers into focused, compelling stories. Recruiters are trained to listen for this structure, and using it shows interview preparation.',
            whenToUse: [
                'Any question starting with "Tell me about a time..."',
                'Behavioral interview questions',
                'Questions about past experiences or achievements',
                'Describing challenges you\'ve overcome'
            ],
            realScenarios: [
                '"Describe a conflict with a colleague" - Structure prevents over-explaining',
                '"Tell me about your biggest achievement" - Results-focused ending impresses',
                'Panel interviews where multiple people are evaluating your responses'
            ]
        },
        'Body Language': {
            whyImportant: 'Studies show 55% of communication is non-verbal. Your body language can either reinforce your words or completely undermine them. Interviewers make judgments within seconds.',
            whenToUse: [
                'From the moment you enter the building',
                'During the handshake and greeting',
                'While listening to questions and explanations',
                'When making key points in your answers'
            ],
            realScenarios: [
                'Video interviews where your face and upper body are center stage',
                'Panel interviews where you need to engage multiple people',
                'High-pressure moments when nerves might show physically'
            ]
        },
        'Communication': {
            whyImportant: 'Clear communication demonstrates critical thinking, respect for the interviewer\'s time, and your ability to work effectively in teams. Poor communication is a top reason candidates are rejected.',
            whenToUse: [
                'Explaining complex projects or technical concepts',
                'Asking clarifying questions before answering',
                'Following up on answers when prompted',
                'Closing the interview with your own questions'
            ],
            realScenarios: [
                'Cross-functional role interviews requiring translation of technical to business terms',
                'When your answer isn\'t landing - knowing when and how to adjust',
                'Asking questions that show genuine research and interest'
            ]
        },
        'Technical': {
            whyImportant: 'Technical interviews assess not just what you know, but how you think and learn. Companies want to see problem-solving approaches, not just correct answers.',
            whenToUse: [
                'Live coding or whiteboard sessions',
                'System design discussions',
                'Explaining past technical decisions',
                'When you don\'t immediately know the answer'
            ],
            realScenarios: [
                'Stuck on a coding problem - how you ask for hints matters',
                'Explaining trade-offs in your design choices',
                'Discussing a bug or failure in production and how you resolved it'
            ]
        }
    };

    return content[skillFocus] || content['Communication'];
}

export function WhyThisMatters({ resource, skillFocus }: WhyThisMattersProps) {
    const content = generateWhyContent(skillFocus);

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="bg-white border border-lavender-200 rounded-2xl overflow-hidden"
        >
            {/* Header */}
            <div className="px-6 lg:px-8 py-5 border-b border-lavender-100 bg-gradient-to-r from-primary/5 to-secondary/5">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
                        <HelpCircle className="w-5 h-5 text-primary" />
                    </div>
                    <div>
                        <h2 className="font-heading text-xl font-bold text-foreground">
                            Why This Matters
                        </h2>
                        <p className="text-sm text-foreground/60">Real-world relevance</p>
                    </div>
                </div>
            </div>

            {/* Content */}
            <div className="px-6 lg:px-8 py-6 space-y-6">
                {/* Why Important */}
                <div>
                    <p className="font-paragraph text-foreground/80 leading-relaxed">
                        {content.whyImportant}
                    </p>
                </div>

                {/* When to Use */}
                <div className="p-5 bg-lavender-50/50 rounded-xl border border-lavender-100">
                    <div className="flex items-center gap-2 mb-4">
                        <Target className="w-5 h-5 text-primary" />
                        <h3 className="font-heading text-base font-semibold text-foreground">
                            When to use this skill
                        </h3>
                    </div>
                    <ul className="space-y-2">
                        {content.whenToUse.map((item, index) => (
                            <motion.li
                                key={index}
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ duration: 0.3, delay: index * 0.1 }}
                                className="flex items-start gap-2"
                            >
                                <CheckCircle2 className="w-4 h-4 text-primary shrink-0 mt-0.5" />
                                <span className="text-sm text-foreground/70">{item}</span>
                            </motion.li>
                        ))}
                    </ul>
                </div>

                {/* Real Interview Scenarios */}
                <div className="p-5 bg-secondary/5 rounded-xl border border-secondary/20">
                    <div className="flex items-center gap-2 mb-4">
                        <MessageSquare className="w-5 h-5 text-secondary" />
                        <h3 className="font-heading text-base font-semibold text-foreground">
                            Real interview scenarios
                        </h3>
                    </div>
                    <div className="space-y-3">
                        {content.realScenarios.map((scenario, index) => (
                            <motion.div
                                key={index}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.3, delay: 0.2 + index * 0.1 }}
                                className="p-3 bg-white rounded-lg border border-lavender-100"
                            >
                                <p className="text-sm text-foreground/80">{scenario}</p>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </div>
        </motion.div>
    );
}

export default WhyThisMatters;
