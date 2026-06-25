/**
 * NextStepsPanel Component
 * Navigation intelligence with related resources and CTAs
 */
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import {
    ArrowRight, BookOpen, Sparkles, Target,
    Video, FileText, Zap, GraduationCap
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { LearningResources } from '@/entities';

interface NextStepsPanelProps {
    currentResource: LearningResources;
    relatedResources?: LearningResources[];
    skillFocus?: string;
}

// Generate mock related resources based on current resource
function generateRelatedResources(current: LearningResources): Array<{
    id: string;
    title: string;
    type: string;
    duration: string;
    icon: typeof BookOpen;
}> {
    const hash = current._id?.split('').reduce((a, c) => a + c.charCodeAt(0), 0) || 0;

    const relatedOptions = [
        { title: 'Mastering the STAR Method', type: 'Video', duration: '12 min', icon: Video },
        { title: 'Body Language Essentials', type: 'Article', duration: '8 min read', icon: FileText },
        { title: 'Confidence Building Exercises', type: 'Guide', duration: '15 min', icon: BookOpen },
        { title: 'Common Interview Mistakes', type: 'Video', duration: '10 min', icon: Video },
        { title: 'Technical Interview Prep', type: 'Tutorial', duration: '20 min', icon: GraduationCap },
        { title: 'First Impressions Guide', type: 'Article', duration: '6 min read', icon: FileText },
    ];

    // Select 3 related resources based on hash
    const selected = [];
    for (let i = 0; i < 3; i++) {
        const index = (hash + i * 7) % relatedOptions.length;
        selected.push({
            ...relatedOptions[index],
            id: `related-${i}`
        });
    }

    return selected;
}

export function NextStepsPanel({
    currentResource,
    relatedResources,
    skillFocus = 'Communication'
}: NextStepsPanelProps) {
    const mockRelated = generateRelatedResources(currentResource);

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="space-y-6"
        >
            {/* What's Next Header */}
            <div className="bg-gradient-to-r from-primary/10 via-secondary/10 to-primary/10 
                      border border-lavender-200 rounded-2xl p-6 lg:p-8">
                <div className="flex items-center gap-3 mb-4">
                    <div className="w-12 h-12 rounded-xl bg-primary/20 flex items-center justify-center">
                        <Sparkles className="w-6 h-6 text-primary" />
                    </div>
                    <div>
                        <h2 className="font-heading text-2xl font-bold text-foreground">What's Next?</h2>
                        <p className="text-foreground/60">Continue your learning journey</p>
                    </div>
                </div>

                <p className="font-paragraph text-foreground/70 mb-6 leading-relaxed">
                    Great progress! Now that you've completed this resource, here are some recommended
                    next steps to reinforce your learning and build on these skills.
                </p>

                {/* Primary CTAs */}
                <div className="flex flex-wrap gap-4">
                    <Link to="/practice">
                        <Button className="bg-primary text-white hover:bg-primary/90 rounded-xl h-12 px-6
                               shadow-lg shadow-primary/25 transition-all hover:shadow-xl">
                            <Target className="w-5 h-5 mr-2" />
                            Practice This Skill
                            <ArrowRight className="w-4 h-4 ml-2" />
                        </Button>
                    </Link>
                    <Link to="/resources">
                        <Button variant="outline" className="border-primary/30 text-primary hover:bg-primary/10 
                                                  rounded-xl h-12 px-6">
                            <BookOpen className="w-5 h-5 mr-2" />
                            Browse More Resources
                        </Button>
                    </Link>
                </div>
            </div>

            {/* Related Resources */}
            <div className="bg-white border border-lavender-200 rounded-2xl p-6 lg:p-8">
                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-secondary/10 flex items-center justify-center">
                            <Zap className="w-5 h-5 text-secondary" />
                        </div>
                        <h3 className="font-heading text-xl font-bold text-foreground">
                            Recommended for You
                        </h3>
                    </div>
                    <Link
                        to="/resources"
                        className="text-sm font-medium text-primary hover:text-primary/80 
                       flex items-center gap-1 transition-colors"
                    >
                        View all
                        <ArrowRight className="w-4 h-4" />
                    </Link>
                </div>

                <div className="grid md:grid-cols-3 gap-4">
                    {mockRelated.map((related, index) => {
                        const IconComponent = related.icon;
                        return (
                            <motion.div
                                key={related.id}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.3, delay: index * 0.1 }}
                            >
                                <Link
                                    to="/resources"
                                    className="block group p-4 bg-lavender-50/50 border border-lavender-200 rounded-xl
                             hover:border-primary/40 hover:bg-lavender-50 transition-all duration-300"
                                >
                                    <div className="flex items-start gap-3">
                                        <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center
                                    shrink-0 group-hover:bg-primary/20 transition-colors">
                                            <IconComponent className="w-5 h-5 text-primary" />
                                        </div>
                                        <div className="min-w-0">
                                            <h4 className="font-heading text-sm font-semibold text-foreground 
                                     group-hover:text-primary transition-colors line-clamp-2">
                                                {related.title}
                                            </h4>
                                            <div className="flex items-center gap-2 mt-1 text-xs text-foreground/50">
                                                <span>{related.type}</span>
                                                <span>•</span>
                                                <span>{related.duration}</span>
                                            </div>
                                        </div>
                                    </div>
                                </Link>
                            </motion.div>
                        );
                    })}
                </div>
            </div>

            {/* Learning Path CTA */}
            <div className="bg-gradient-to-br from-primary/5 to-secondary/5 border border-lavender-200 
                      rounded-2xl p-6 lg:p-8 text-center">
                <GraduationCap className="w-12 h-12 text-primary mx-auto mb-4" />
                <h3 className="font-heading text-xl font-bold text-foreground mb-2">
                    Keep Learning
                </h3>
                <p className="font-paragraph text-foreground/60 max-w-md mx-auto mb-6">
                    You're making great progress! Continue your interview preparation journey
                    and track your improvement over time.
                </p>
                <Link to="/progress">
                    <Button variant="outline" className="border-primary text-primary hover:bg-primary 
                                                hover:text-white rounded-xl h-11 px-6 transition-all">
                        View Your Progress
                        <ArrowRight className="w-4 h-4 ml-2" />
                    </Button>
                </Link>
            </div>
        </motion.div>
    );
}

export default NextStepsPanel;
