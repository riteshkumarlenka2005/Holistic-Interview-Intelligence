/**
 * ResourceSection Component
 * Horizontal scrollable section for curated resource categories
 */
import { useRef } from 'react';
import { motion } from 'framer-motion';
import { ChevronLeft, ChevronRight, Sparkles, TrendingUp, GraduationCap, Trophy } from 'lucide-react';
import { LearningResources } from '@/entities';
import { ResourceCard } from './ResourceCard';

interface ResourceSectionProps {
    title: string;
    subtitle?: string;
    icon?: React.ReactNode;
    resources: LearningResources[];
    completedIds?: Set<string>;
    progressMap?: Map<string, number>;
    variant?: 'horizontal' | 'grid';
    maxItems?: number;
}

export function ResourceSection({
    title,
    subtitle,
    icon,
    resources,
    completedIds = new Set(),
    progressMap = new Map(),
    variant = 'horizontal',
    maxItems = 6
}: ResourceSectionProps) {
    const scrollRef = useRef<HTMLDivElement>(null);

    const displayResources = resources.slice(0, maxItems);

    const scroll = (direction: 'left' | 'right') => {
        if (scrollRef.current) {
            const scrollAmount = 340; // Card width + gap
            scrollRef.current.scrollBy({
                left: direction === 'left' ? -scrollAmount : scrollAmount,
                behavior: 'smooth'
            });
        }
    };

    if (displayResources.length === 0) return null;

    return (
        <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="mb-12"
        >
            {/* Section Header */}
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                    {icon && (
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary/20 to-secondary/20 
                            flex items-center justify-center">
                            {icon}
                        </div>
                    )}
                    <div>
                        <h2 className="font-heading text-xl font-bold text-foreground">
                            {title}
                        </h2>
                        {subtitle && (
                            <p className="text-sm text-foreground/60 mt-0.5">{subtitle}</p>
                        )}
                    </div>
                </div>

                {/* Scroll Controls */}
                {variant === 'horizontal' && displayResources.length > 3 && (
                    <div className="flex items-center gap-2">
                        <button
                            onClick={() => scroll('left')}
                            className="w-9 h-9 rounded-full border border-lavender-200 bg-white 
                         flex items-center justify-center text-foreground/60
                         hover:border-primary/40 hover:text-primary transition-all"
                            aria-label="Scroll left"
                        >
                            <ChevronLeft className="w-5 h-5" />
                        </button>
                        <button
                            onClick={() => scroll('right')}
                            className="w-9 h-9 rounded-full border border-lavender-200 bg-white 
                         flex items-center justify-center text-foreground/60
                         hover:border-primary/40 hover:text-primary transition-all"
                            aria-label="Scroll right"
                        >
                            <ChevronRight className="w-5 h-5" />
                        </button>
                    </div>
                )}
            </div>

            {/* Content */}
            {variant === 'horizontal' ? (
                <div
                    ref={scrollRef}
                    className="flex gap-6 overflow-x-auto pb-4 scrollbar-hide 
                     -mx-2 px-2 snap-x snap-mandatory"
                    style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
                >
                    {displayResources.map((resource, index) => (
                        <div
                            key={resource._id}
                            className="w-80 shrink-0 snap-start"
                        >
                            <ResourceCard
                                resource={resource}
                                index={index}
                                isCompleted={completedIds.has(resource._id || '')}
                                progress={progressMap.get(resource._id || '') || 0}
                            />
                        </div>
                    ))}
                </div>
            ) : (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {displayResources.map((resource, index) => (
                        <ResourceCard
                            key={resource._id}
                            resource={resource}
                            index={index}
                            isCompleted={completedIds.has(resource._id || '')}
                            progress={progressMap.get(resource._id || '') || 0}
                        />
                    ))}
                </div>
            )}
        </motion.section>
    );
}

// Preset section configurations
export const SectionPresets = {
    recommended: {
        title: 'Recommended for You',
        subtitle: 'Personalized picks based on your learning journey',
        icon: <Sparkles className="w-5 h-5 text-primary" />
    },
    popular: {
        title: 'Most Popular',
        subtitle: 'Top resources loved by our community',
        icon: <TrendingUp className="w-5 h-5 text-amber-500" />
    },
    beginner: {
        title: 'Beginner Friendly',
        subtitle: 'Start your interview preparation here',
        icon: <GraduationCap className="w-5 h-5 text-emerald-500" />
    },
    advanced: {
        title: 'Interview Ready',
        subtitle: 'Advanced techniques for experienced candidates',
        icon: <Trophy className="w-5 h-5 text-rose-500" />
    }
};

export default ResourceSection;
