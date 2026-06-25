/**
 * ResourceCard Component
 * Enhanced card with learning metadata, progress indicators, and premium styling
 */
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import {
    BookOpen, Video, FileText, Clock, Target, Briefcase,
    GraduationCap, CheckCircle2, Play
} from 'lucide-react';
import { Image } from '@/components/ui/image';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { LearningResources } from '@/entities';

// Learning metadata utilities
const DIFFICULTY_LEVELS = ['Beginner', 'Intermediate', 'Advanced'] as const;
const SKILL_FOCUSES = ['Confidence', 'STAR Method', 'Body Language', 'Communication', 'Technical'] as const;
const INTERVIEW_TYPES = ['HR', 'Technical', 'Managerial', 'Behavioral'] as const;

interface ResourceMeta {
    difficulty: typeof DIFFICULTY_LEVELS[number];
    estimatedTime: string;
    skillFocus: typeof SKILL_FOCUSES[number];
    interviewType: typeof INTERVIEW_TYPES[number];
}

// Generate mock learning metadata based on resource properties
function generateMeta(resource: LearningResources): ResourceMeta {
    // Use resource ID hash for consistent mock data
    const hash = resource._id?.split('').reduce((a, c) => a + c.charCodeAt(0), 0) || 0;

    return {
        difficulty: DIFFICULTY_LEVELS[hash % 3],
        estimatedTime: resource.resourceType === 'Video'
            ? `${10 + (hash % 35)} min video`
            : `${5 + (hash % 15)} min read`,
        skillFocus: SKILL_FOCUSES[hash % SKILL_FOCUSES.length],
        interviewType: INTERVIEW_TYPES[hash % INTERVIEW_TYPES.length],
    };
}

interface ResourceCardProps {
    resource: LearningResources;
    index?: number;
    isCompleted?: boolean;
    progress?: number;
    onMarkComplete?: (id: string) => void;
    variant?: 'default' | 'compact' | 'featured';
}

export function ResourceCard({
    resource,
    index = 0,
    isCompleted = false,
    progress = 0,
    onMarkComplete,
    variant = 'default'
}: ResourceCardProps) {
    const meta = generateMeta(resource);

    const getTypeIcon = (type?: string) => {
        switch (type) {
            case 'Video': return Video;
            case 'Article': return FileText;
            default: return BookOpen;
        }
    };

    const TypeIcon = getTypeIcon(resource.resourceType);

    const getDifficultyColor = (difficulty: string) => {
        switch (difficulty) {
            case 'Beginner': return 'bg-emerald-50 text-emerald-700 border-emerald-200';
            case 'Intermediate': return 'bg-amber-50 text-amber-700 border-amber-200';
            case 'Advanced': return 'bg-rose-50 text-rose-700 border-rose-200';
            default: return 'bg-slate-50 text-slate-700 border-slate-200';
        }
    };

    if (variant === 'compact') {
        return (
            <Link to={`/resources/${resource._id}`} className="block group">
                <motion.div
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3, delay: index * 0.05 }}
                    className="flex items-center gap-4 p-4 bg-white/80 border border-lavender-200 rounded-xl 
                     hover:border-primary/40 hover:shadow-md transition-all duration-300"
                >
                    <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-primary/10 to-secondary/10 
                          flex items-center justify-center shrink-0">
                        <TypeIcon className="w-6 h-6 text-primary" />
                    </div>
                    <div className="flex-1 min-w-0">
                        <h4 className="font-heading text-sm font-semibold text-foreground truncate">
                            {resource.resourceTitle || 'Untitled'}
                        </h4>
                        <div className="flex items-center gap-2 mt-1">
                            <span className="text-xs text-foreground/60">{meta.estimatedTime}</span>
                            <span className="text-foreground/30">•</span>
                            <span className="text-xs text-foreground/60">{meta.difficulty}</span>
                        </div>
                    </div>
                    {isCompleted && (
                        <CheckCircle2 className="w-5 h-5 text-emerald-500 shrink-0" />
                    )}
                </motion.div>
            </Link>
        );
    }

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: index * 0.05 }}
            className="group"
        >
            <Link to={`/resources/${resource._id}`}>
                <div className={`
          relative bg-white border border-lavender-200 rounded-2xl overflow-hidden
          transition-all duration-300 h-full
          hover:border-primary/40 hover:shadow-xl hover:shadow-primary/10
          ${isCompleted ? 'ring-2 ring-emerald-200' : ''}
        `}>
                    {/* Completion Badge */}
                    {isCompleted && (
                        <div className="absolute top-3 right-3 z-10">
                            <div className="flex items-center gap-1.5 px-2.5 py-1 bg-emerald-500 text-white 
                              rounded-full text-xs font-medium shadow-lg">
                                <CheckCircle2 className="w-3.5 h-3.5" />
                                Completed
                            </div>
                        </div>
                    )}

                    {/* Thumbnail */}
                    {resource.thumbnailImage ? (
                        <div className="aspect-video overflow-hidden relative">
                            <Image
                                src={resource.thumbnailImage}
                                alt={resource.resourceTitle || 'Resource thumbnail'}
                                width={400}
                                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                            />
                            {/* Play overlay for videos */}
                            {resource.resourceType === 'Video' && (
                                <div className="absolute inset-0 flex items-center justify-center bg-black/20 
                                opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                                    <div className="w-14 h-14 rounded-full bg-white/90 flex items-center justify-center 
                                  shadow-lg transform group-hover:scale-110 transition-transform">
                                        <Play className="w-6 h-6 text-primary ml-1" />
                                    </div>
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="aspect-video bg-gradient-to-br from-lavender-100 to-primary/10 
                            flex items-center justify-center">
                            <TypeIcon className="w-16 h-16 text-primary/40" />
                        </div>
                    )}

                    {/* Content */}
                    <div className="p-5">
                        {/* Type & Skill Tags */}
                        <div className="flex items-center gap-2 mb-3 flex-wrap">
                            <Badge variant="outline" className={`text-xs ${getDifficultyColor(meta.difficulty)}`}>
                                <GraduationCap className="w-3 h-3 mr-1" />
                                {meta.difficulty}
                            </Badge>
                            <Badge variant="outline" className="text-xs bg-slate-50 text-slate-600 border-slate-200">
                                <Clock className="w-3 h-3 mr-1" />
                                {meta.estimatedTime}
                            </Badge>
                        </div>

                        {/* Title */}
                        <h3 className="font-heading text-lg font-bold text-foreground mb-2 line-clamp-2 
                           group-hover:text-primary transition-colors">
                            {resource.resourceTitle || 'Untitled Resource'}
                        </h3>

                        {/* Description */}
                        <p className="font-paragraph text-sm text-foreground/70 line-clamp-2 mb-4">
                            {resource.description || 'Explore this learning resource to enhance your interview skills.'}
                        </p>

                        {/* Learning Focus */}
                        <div className="flex items-center gap-3 text-xs text-foreground/60 mb-3">
                            <span className="flex items-center gap-1">
                                <Target className="w-3.5 h-3.5" />
                                {meta.skillFocus}
                            </span>
                            <span className="flex items-center gap-1">
                                <Briefcase className="w-3.5 h-3.5" />
                                {meta.interviewType}
                            </span>
                        </div>

                        {/* Progress Bar (if in progress) */}
                        {progress > 0 && progress < 100 && (
                            <div className="mt-auto pt-3 border-t border-lavender-100">
                                <div className="flex items-center justify-between text-xs mb-1.5">
                                    <span className="text-foreground/60">Your progress</span>
                                    <span className="font-medium text-primary">{progress}%</span>
                                </div>
                                <Progress value={progress} className="h-1.5" />
                            </div>
                        )}
                    </div>
                </div>
            </Link>
        </motion.div>
    );
}

/**
 * ResourceMeta Component
 * Displays learning metadata badges inline
 */
interface ResourceMetaProps {
    resource: LearningResources;
    showAll?: boolean;
}

export function ResourceMeta({ resource, showAll = false }: ResourceMetaProps) {
    const meta = generateMeta(resource);

    return (
        <div className="flex items-center gap-2 flex-wrap">
            <span className="inline-flex items-center gap-1 text-xs text-foreground/60">
                <Clock className="w-3 h-3" />
                {meta.estimatedTime}
            </span>
            <span className="text-foreground/30">•</span>
            <span className="inline-flex items-center gap-1 text-xs text-foreground/60">
                <GraduationCap className="w-3 h-3" />
                {meta.difficulty}
            </span>
            {showAll && (
                <>
                    <span className="text-foreground/30">•</span>
                    <span className="inline-flex items-center gap-1 text-xs text-foreground/60">
                        <Target className="w-3 h-3" />
                        {meta.skillFocus}
                    </span>
                </>
            )}
        </div>
    );
}

export default ResourceCard;
