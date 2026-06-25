/**
 * LearningSummaryCard Component
 * Displays learning context with skill focus, difficulty, time, and outcomes
 */
import { motion } from 'framer-motion';
import {
    GraduationCap, Clock, Target, Briefcase,
    CheckCircle2, Lightbulb, TrendingUp
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { LearningResources } from '@/entities';

// Learning metadata utilities (matching ResourceCard)
const DIFFICULTY_LEVELS = ['Beginner', 'Intermediate', 'Advanced'] as const;
const SKILL_FOCUSES = ['Confidence', 'STAR Method', 'Body Language', 'Communication', 'Technical'] as const;
const INTERVIEW_TYPES = ['HR', 'Technical', 'Managerial', 'Behavioral'] as const;

interface LearningMeta {
    difficulty: typeof DIFFICULTY_LEVELS[number];
    estimatedTime: string;
    skillFocus: typeof SKILL_FOCUSES[number];
    interviewType: typeof INTERVIEW_TYPES[number];
    learningOutcome: string;
}

// Generate consistent mock metadata based on resource properties
export function generateLearningMeta(resource: LearningResources): LearningMeta {
    const hash = resource._id?.split('').reduce((a, c) => a + c.charCodeAt(0), 0) || 0;

    const outcomes: Record<typeof SKILL_FOCUSES[number], string> = {
        'Confidence': 'present yourself with poise and self-assurance in any interview setting',
        'STAR Method': 'structure behavioral answers clearly using Situation, Task, Action, Result',
        'Body Language': 'communicate non-verbally with open, confident, and engaging posture',
        'Communication': 'articulate your thoughts clearly and connect with interviewers effectively',
        'Technical': 'explain complex concepts simply and demonstrate problem-solving skills'
    };

    const skillFocus = SKILL_FOCUSES[hash % SKILL_FOCUSES.length];

    return {
        difficulty: DIFFICULTY_LEVELS[hash % 3],
        estimatedTime: resource.resourceType === 'Video'
            ? `${10 + (hash % 35)} min video`
            : `${5 + (hash % 15)} min read`,
        skillFocus,
        interviewType: INTERVIEW_TYPES[hash % INTERVIEW_TYPES.length],
        learningOutcome: outcomes[skillFocus],
    };
}

interface LearningSummaryCardProps {
    resource: LearningResources;
    progress?: number;
    isCompleted?: boolean;
    onMarkComplete?: () => void;
    onContinue?: () => void;
}

export function LearningSummaryCard({
    resource,
    progress = 0,
    isCompleted = false,
    onMarkComplete,
    onContinue
}: LearningSummaryCardProps) {
    const meta = generateLearningMeta(resource);

    const getDifficultyStyle = (difficulty: string) => {
        switch (difficulty) {
            case 'Beginner': return { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200' };
            case 'Intermediate': return { bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200' };
            case 'Advanced': return { bg: 'bg-rose-50', text: 'text-rose-700', border: 'border-rose-200' };
            default: return { bg: 'bg-slate-50', text: 'text-slate-700', border: 'border-slate-200' };
        }
    };

    const diffStyle = getDifficultyStyle(meta.difficulty);

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="bg-white border border-lavender-200 rounded-2xl p-6 lg:p-8 shadow-sm"
        >
            {/* Header Row */}
            <div className="flex flex-wrap items-start justify-between gap-4 mb-6">
                <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary/20 to-secondary/20 
                          flex items-center justify-center">
                        <Target className="w-6 h-6 text-primary" />
                    </div>
                    <div>
                        <h3 className="font-heading text-lg font-bold text-foreground">Learning Summary</h3>
                        <p className="text-sm text-foreground/60">What you'll gain from this resource</p>
                    </div>
                </div>

                {/* Progress / Completion Status */}
                <div className="flex items-center gap-3">
                    {isCompleted ? (
                        <div className="flex items-center gap-2 px-4 py-2 bg-emerald-50 border border-emerald-200 rounded-xl">
                            <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                            <span className="text-sm font-semibold text-emerald-700">Completed</span>
                        </div>
                    ) : progress > 0 ? (
                        <button
                            onClick={onContinue}
                            className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-xl
                         hover:bg-primary/90 transition-colors font-medium text-sm"
                        >
                            <TrendingUp className="w-4 h-4" />
                            Continue ({progress}%)
                        </button>
                    ) : (
                        <button
                            onClick={onMarkComplete}
                            className="flex items-center gap-2 px-4 py-2 bg-lavender-100 text-foreground/70 
                         rounded-xl hover:bg-lavender-200 transition-colors font-medium text-sm
                         border border-lavender-200"
                        >
                            <CheckCircle2 className="w-4 h-4" />
                            Mark as Completed
                        </button>
                    )}
                </div>
            </div>

            {/* Metadata Grid */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                {/* Difficulty */}
                <div className={`p-4 rounded-xl ${diffStyle.bg} ${diffStyle.border} border`}>
                    <div className="flex items-center gap-2 mb-1">
                        <GraduationCap className={`w-4 h-4 ${diffStyle.text}`} />
                        <span className="text-xs font-medium text-foreground/50 uppercase tracking-wide">Difficulty</span>
                    </div>
                    <p className={`font-semibold ${diffStyle.text}`}>{meta.difficulty}</p>
                </div>

                {/* Estimated Time */}
                <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
                    <div className="flex items-center gap-2 mb-1">
                        <Clock className="w-4 h-4 text-slate-500" />
                        <span className="text-xs font-medium text-foreground/50 uppercase tracking-wide">Duration</span>
                    </div>
                    <p className="font-semibold text-slate-700">{meta.estimatedTime}</p>
                </div>

                {/* Skill Focus */}
                <div className="p-4 rounded-xl bg-primary/5 border border-primary/20">
                    <div className="flex items-center gap-2 mb-1">
                        <Target className="w-4 h-4 text-primary" />
                        <span className="text-xs font-medium text-foreground/50 uppercase tracking-wide">Skill Focus</span>
                    </div>
                    <p className="font-semibold text-primary">{meta.skillFocus}</p>
                </div>

                {/* Interview Type */}
                <div className="p-4 rounded-xl bg-secondary/5 border border-secondary/20">
                    <div className="flex items-center gap-2 mb-1">
                        <Briefcase className="w-4 h-4 text-secondary" />
                        <span className="text-xs font-medium text-foreground/50 uppercase tracking-wide">Interview Type</span>
                    </div>
                    <p className="font-semibold text-secondary">{meta.interviewType}</p>
                </div>
            </div>

            {/* Learning Outcome */}
            <div className="p-4 rounded-xl bg-gradient-to-r from-primary/5 to-secondary/5 border border-lavender-200">
                <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center shrink-0 mt-0.5">
                        <Lightbulb className="w-4 h-4 text-primary" />
                    </div>
                    <div>
                        <p className="text-xs font-medium text-foreground/50 uppercase tracking-wide mb-1">
                            After completing this, you'll be able to:
                        </p>
                        <p className="font-paragraph text-foreground/80 leading-relaxed">
                            {meta.learningOutcome}
                        </p>
                    </div>
                </div>
            </div>

            {/* Progress Bar (if in progress) */}
            {progress > 0 && progress < 100 && (
                <div className="mt-6 pt-6 border-t border-lavender-100">
                    <div className="flex items-center justify-between text-sm mb-2">
                        <span className="text-foreground/60">Your progress</span>
                        <span className="font-semibold text-primary">{progress}%</span>
                    </div>
                    <div className="h-2 bg-lavender-100 rounded-full overflow-hidden">
                        <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${progress}%` }}
                            transition={{ duration: 0.8, ease: 'easeOut' }}
                            className="h-full bg-gradient-to-r from-primary to-secondary rounded-full"
                        />
                    </div>
                </div>
            )}
        </motion.div>
    );
}

export default LearningSummaryCard;
