/**
 * ContentSection Component
 * Structured content display with visual sections, callouts, and key takeaways
 */
import { motion } from 'framer-motion';
import {
    BookOpen, Lightbulb, AlertTriangle, CheckCircle2,
    Quote, ArrowRight, Star
} from 'lucide-react';

interface ContentSectionProps {
    content: string;
    resourceType?: string;
}

interface ParsedSection {
    type: 'paragraph' | 'tip' | 'warning' | 'takeaway' | 'quote' | 'heading';
    content: string;
}

// Parse content into structured sections
function parseContent(content: string): ParsedSection[] {
    const lines = content.split('\n').filter(line => line.trim());
    const sections: ParsedSection[] = [];

    let currentParagraph: string[] = [];

    const flushParagraph = () => {
        if (currentParagraph.length > 0) {
            sections.push({
                type: 'paragraph',
                content: currentParagraph.join(' ').trim()
            });
            currentParagraph = [];
        }
    };

    for (const line of lines) {
        const trimmed = line.trim();

        // Detect tips (lines with keywords)
        if (trimmed.toLowerCase().includes('tip:') ||
            trimmed.toLowerCase().includes('pro tip:') ||
            trimmed.toLowerCase().startsWith('💡')) {
            flushParagraph();
            sections.push({ type: 'tip', content: trimmed.replace(/^(💡|tip:|pro tip:)/i, '').trim() });
        }
        // Detect warnings/mistakes
        else if (trimmed.toLowerCase().includes('mistake:') ||
            trimmed.toLowerCase().includes('avoid:') ||
            trimmed.toLowerCase().includes('warning:') ||
            trimmed.toLowerCase().startsWith('⚠️')) {
            flushParagraph();
            sections.push({ type: 'warning', content: trimmed.replace(/^(⚠️|mistake:|avoid:|warning:)/i, '').trim() });
        }
        // Detect takeaways
        else if (trimmed.toLowerCase().includes('key takeaway:') ||
            trimmed.toLowerCase().includes('remember:') ||
            trimmed.toLowerCase().startsWith('✅')) {
            flushParagraph();
            sections.push({ type: 'takeaway', content: trimmed.replace(/^(✅|key takeaway:|remember:)/i, '').trim() });
        }
        // Detect headings (short lines that look like titles)
        else if (trimmed.length < 60 &&
            (trimmed.endsWith(':') || /^[A-Z][^.!?]*$/.test(trimmed)) &&
            !trimmed.includes(',')) {
            flushParagraph();
            sections.push({ type: 'heading', content: trimmed.replace(/:$/, '') });
        }
        // Detect quotes
        else if (trimmed.startsWith('"') && trimmed.endsWith('"')) {
            flushParagraph();
            sections.push({ type: 'quote', content: trimmed.slice(1, -1) });
        }
        // Regular paragraph content
        else {
            currentParagraph.push(trimmed);
            // Split into paragraphs after ~3-4 sentences
            if (currentParagraph.join(' ').split(/[.!?]/).length > 4) {
                flushParagraph();
            }
        }
    }

    flushParagraph();

    // If no special sections detected, create some based on content length
    if (sections.filter(s => s.type !== 'paragraph').length === 0 && sections.length > 2) {
        // Add a synthetic tip from middle content
        const midIndex = Math.floor(sections.length / 2);
        if (sections[midIndex]?.type === 'paragraph') {
            sections[midIndex] = {
                type: 'tip',
                content: sections[midIndex].content.split('.').slice(0, 2).join('.') + '.'
            };
        }
    }

    return sections;
}

// Generate key takeaways from content
function generateTakeaways(content: string, skillFocus: string): string[] {
    // In production, this would use NLP. For now, extract key sentences.
    const sentences = content.split(/[.!?]/).filter(s => s.trim().length > 20);
    const takeaways: string[] = [];

    // Default takeaways based on skill focus
    const defaultTakeaways: Record<string, string[]> = {
        'Confidence': [
            'Maintain steady eye contact to project assurance',
            'Use deliberate pauses instead of filler words',
            'Prepare key stories so you speak with conviction'
        ],
        'STAR Method': [
            'Always start with a clear, concise Situation',
            'Quantify your Results with specific metrics',
            'Keep your Action section focused on YOUR contributions'
        ],
        'Body Language': [
            'Sit up straight with shoulders back and relaxed',
            'Use natural hand gestures to emphasize points',
            'Mirror the interviewer\'s energy level subtly'
        ],
        'Communication': [
            'Listen fully before formulating your response',
            'Structure answers with a clear beginning, middle, end',
            'Ask clarifying questions to show engagement'
        ],
        'Technical': [
            'Think out loud to show your problem-solving process',
            'It\'s okay to ask clarifying questions',
            'Start with a brute force solution, then optimize'
        ]
    };

    return defaultTakeaways[skillFocus] || defaultTakeaways['Communication'];
}

export function ContentSection({ content, resourceType }: ContentSectionProps) {
    const sections = parseContent(content);
    const takeaways = generateTakeaways(content, 'Confidence');

    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
            className="space-y-6"
        >
            {/* Main Content Section */}
            <div className="bg-white border border-lavender-200 rounded-2xl overflow-hidden">
                {/* Header */}
                <div className="px-6 lg:px-8 py-5 border-b border-lavender-100 bg-lavender-50/50">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
                            <BookOpen className="w-5 h-5 text-primary" />
                        </div>
                        <div>
                            <h2 className="font-heading text-xl font-bold text-foreground">
                                {resourceType === 'Video' ? 'Video Transcript & Notes' : 'Learning Content'}
                            </h2>
                            <p className="text-sm text-foreground/60">Study this material carefully</p>
                        </div>
                    </div>
                </div>

                {/* Content Body */}
                <div className="px-6 lg:px-8 py-6 space-y-6">
                    {sections.map((section, index) => (
                        <motion.div
                            key={index}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.3, delay: index * 0.05 }}
                        >
                            {section.type === 'paragraph' && (
                                <p className="font-paragraph text-foreground/80 leading-relaxed">
                                    {section.content}
                                </p>
                            )}

                            {section.type === 'heading' && (
                                <h3 className="font-heading text-lg font-bold text-foreground mt-8 mb-4 
                               flex items-center gap-2">
                                    <div className="w-1 h-6 bg-primary rounded-full" />
                                    {section.content}
                                </h3>
                            )}

                            {section.type === 'tip' && (
                                <div className="flex gap-4 p-4 bg-emerald-50 border border-emerald-200 rounded-xl">
                                    <div className="w-10 h-10 rounded-lg bg-emerald-100 flex items-center justify-center shrink-0">
                                        <Lightbulb className="w-5 h-5 text-emerald-600" />
                                    </div>
                                    <div>
                                        <p className="text-xs font-semibold text-emerald-700 uppercase tracking-wide mb-1">
                                            Interview Tip
                                        </p>
                                        <p className="font-paragraph text-emerald-800">{section.content}</p>
                                    </div>
                                </div>
                            )}

                            {section.type === 'warning' && (
                                <div className="flex gap-4 p-4 bg-amber-50 border border-amber-200 rounded-xl">
                                    <div className="w-10 h-10 rounded-lg bg-amber-100 flex items-center justify-center shrink-0">
                                        <AlertTriangle className="w-5 h-5 text-amber-600" />
                                    </div>
                                    <div>
                                        <p className="text-xs font-semibold text-amber-700 uppercase tracking-wide mb-1">
                                            Common Mistake
                                        </p>
                                        <p className="font-paragraph text-amber-800">{section.content}</p>
                                    </div>
                                </div>
                            )}

                            {section.type === 'takeaway' && (
                                <div className="flex gap-4 p-4 bg-primary/5 border border-primary/20 rounded-xl">
                                    <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
                                        <CheckCircle2 className="w-5 h-5 text-primary" />
                                    </div>
                                    <div>
                                        <p className="text-xs font-semibold text-primary uppercase tracking-wide mb-1">
                                            Key Takeaway
                                        </p>
                                        <p className="font-paragraph text-foreground/80">{section.content}</p>
                                    </div>
                                </div>
                            )}

                            {section.type === 'quote' && (
                                <div className="flex gap-4 p-4 bg-lavender-50 border-l-4 border-primary rounded-r-xl">
                                    <Quote className="w-6 h-6 text-primary/50 shrink-0" />
                                    <p className="font-paragraph text-foreground/80 italic">{section.content}</p>
                                </div>
                            )}
                        </motion.div>
                    ))}
                </div>
            </div>

            {/* Key Takeaways Summary */}
            <div className="bg-gradient-to-br from-primary/5 to-secondary/5 border border-lavender-200 rounded-2xl p-6 lg:p-8">
                <div className="flex items-center gap-3 mb-5">
                    <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
                        <Star className="w-5 h-5 text-primary" />
                    </div>
                    <h3 className="font-heading text-xl font-bold text-foreground">Key Takeaways</h3>
                </div>

                <div className="space-y-3">
                    {takeaways.map((takeaway, index) => (
                        <motion.div
                            key={index}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ duration: 0.3, delay: 0.3 + index * 0.1 }}
                            className="flex items-start gap-3"
                        >
                            <div className="w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center shrink-0 mt-0.5">
                                <CheckCircle2 className="w-4 h-4 text-primary" />
                            </div>
                            <p className="font-paragraph text-foreground/80">{takeaway}</p>
                        </motion.div>
                    ))}
                </div>
            </div>
        </motion.div>
    );
}

export default ContentSection;
