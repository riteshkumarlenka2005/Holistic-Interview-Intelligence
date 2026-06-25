/**
 * ResourceDetailPage - Enhanced Learning Experience
 * 
 * Complete refactor with:
 * - Visual alignment with Resources List Page (lavender theme)
 * - Learning Summary Panel with skill focus, difficulty, outcomes
 * - Progress tracking and completion indicators
 * - Immersive video player experience
 * - Structured content with tips, warnings, takeaways
 * - "Why This Matters" real-world context section
 * - "What's Next" navigation intelligence
 * 
 * Preserves: API logic, routing, TypeScript safety
 */
import { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { useParams, Link } from 'react-router-dom';
import {
  ArrowLeft, AlertCircle, BookOpen, Video,
  FileText, Share2, Bookmark, ChevronRight
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import { Image } from '@/components/ui/image';
import { Badge } from '@/components/ui/badge';
import { BaseCrudService } from '@/integrations';
import { LearningResources } from '@/entities';
import Header from '@/components/Header';
import Footer from '@/components/Footer';

// New learning-focused components
import { LearningSummaryCard, generateLearningMeta } from '@/components/resources/LearningSummaryCard';
import { ContentSection } from '@/components/resources/ContentSection';
import { VideoPlayer } from '@/components/resources/VideoPlayer';
import { WhyThisMatters } from '@/components/resources/WhyThisMatters';
import { NextStepsPanel } from '@/components/resources/NextStepsPanel';

export default function ResourceDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [resource, setResource] = useState<LearningResources | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Learning progress state (mock - would connect to backend)
  const [progress, setProgress] = useState(0);
  const [isCompleted, setIsCompleted] = useState(false);
  const [isBookmarked, setIsBookmarked] = useState(false);

  // Preserve existing data fetching logic
  useEffect(() => {
    const loadResource = async () => {
      if (!id) return;

      try {
        setIsLoading(true);
        const data = await BaseCrudService.getById<LearningResources>('learningresources', id);
        setResource(data);

        // Mock progress based on ID hash for demo
        const hash = id.split('').reduce((a, c) => a + c.charCodeAt(0), 0);
        if (hash % 5 === 0) {
          setIsCompleted(true);
          setProgress(100);
        } else if (hash % 3 === 0) {
          setProgress(30 + (hash % 50));
        }
      } catch (error) {
        console.error('Failed to load resource:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadResource();
  }, [id]);

  const handleMarkComplete = useCallback(() => {
    setIsCompleted(true);
    setProgress(100);
  }, []);

  const handleContinue = useCallback(() => {
    // Scroll to content
    document.getElementById('main-content')?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  const handleShare = useCallback(() => {
    if (navigator.share) {
      navigator.share({
        title: resource?.resourceTitle || 'Learning Resource',
        url: window.location.href
      });
    } else {
      navigator.clipboard.writeText(window.location.href);
    }
  }, [resource]);

  // Get learning metadata
  const meta = resource ? generateLearningMeta(resource) : null;

  const getTypeIcon = (type?: string) => {
    switch (type) {
      case 'Video': return Video;
      case 'Article': return FileText;
      default: return BookOpen;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-lavender-50 via-white to-lavender-50/30">
      <Header />

      <div className="w-full py-8 px-6 lg:px-16">
        <div className="max-w-5xl mx-auto">

          {/* Breadcrumb Navigation */}
          <motion.nav
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="flex items-center gap-2 text-sm text-foreground/60 mb-8"
          >
            <Link to="/resources" className="hover:text-primary transition-colors">
              Resources
            </Link>
            <ChevronRight className="w-4 h-4" />
            <span className="text-foreground font-medium truncate max-w-[200px]">
              {resource?.resourceTitle || 'Loading...'}
            </span>
          </motion.nav>

          {/* Back Button and Actions */}
          <div className="flex items-center justify-between gap-4 mb-8">
            <Link to="/resources">
              <Button
                variant="outline"
                className="border-lavender-200 text-foreground/70 hover:bg-lavender-50 
                           hover:text-foreground rounded-xl"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Resources
              </Button>
            </Link>

            {resource && (
              <div className="flex items-center gap-2">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setIsBookmarked(!isBookmarked)}
                  className={`rounded-xl ${isBookmarked ? 'text-primary' : 'text-foreground/50'}`}
                >
                  <Bookmark className={`w-5 h-5 ${isBookmarked ? 'fill-current' : ''}`} />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={handleShare}
                  className="rounded-xl text-foreground/50 hover:text-foreground"
                >
                  <Share2 className="w-5 h-5" />
                </Button>
              </div>
            )}
          </div>

          {/* Main Content */}
          <div className="min-h-[600px]">
            {isLoading ? (
              // Loading State
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="space-y-6"
              >
                {/* Loading skeleton */}
                <div className="bg-white rounded-2xl border border-lavender-200 p-8 animate-pulse">
                  <div className="flex gap-4 mb-6">
                    <div className="w-12 h-12 rounded-xl bg-lavender-100" />
                    <div className="flex-1 space-y-2">
                      <div className="h-6 bg-lavender-100 rounded w-1/3" />
                      <div className="h-4 bg-lavender-100 rounded w-1/4" />
                    </div>
                  </div>
                  <div className="grid grid-cols-4 gap-4">
                    {[...Array(4)].map((_, i) => (
                      <div key={i} className="h-20 bg-lavender-100 rounded-xl" />
                    ))}
                  </div>
                </div>
                <div className="aspect-video bg-lavender-100 rounded-2xl animate-pulse" />
              </motion.div>
            ) : !resource ? (
              // Not Found State
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.4 }}
                className="text-center py-24"
              >
                <div className="w-24 h-24 mx-auto mb-6 rounded-full bg-rose-50 
                                flex items-center justify-center">
                  <AlertCircle className="w-12 h-12 text-rose-400" />
                </div>
                <h2 className="font-heading text-3xl font-bold text-foreground mb-4">
                  Resource Not Found
                </h2>
                <p className="font-paragraph text-foreground/60 mb-8 max-w-md mx-auto">
                  This resource may have been moved or removed.
                  Let's find something else to help your interview preparation.
                </p>
                <Link to="/resources">
                  <Button className="bg-primary text-white hover:bg-primary/90 rounded-xl h-12 px-6">
                    Browse All Resources
                  </Button>
                </Link>
              </motion.div>
            ) : (
              // Resource Content
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.5 }}
                className="space-y-8"
              >
                {/* Hero Header */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5 }}
                  className="bg-white border border-lavender-200 rounded-2xl p-6 lg:p-8"
                >
                  {/* Type and Tags */}
                  <div className="flex flex-wrap items-center gap-3 mb-4">
                    {(() => {
                      const TypeIcon = getTypeIcon(resource.resourceType);
                      return (
                        <Badge
                          variant="outline"
                          className="bg-primary/5 text-primary border-primary/20 rounded-lg px-3 py-1"
                        >
                          <TypeIcon className="w-3.5 h-3.5 mr-1.5" />
                          {resource.resourceType || 'Resource'}
                        </Badge>
                      );
                    })()}
                    {resource.tags && resource.tags.split(',').slice(0, 3).map((tag, idx) => (
                      <Badge
                        key={idx}
                        variant="outline"
                        className="bg-secondary/5 text-secondary border-secondary/20 rounded-lg px-3 py-1"
                      >
                        {tag.trim()}
                      </Badge>
                    ))}
                  </div>

                  {/* Title */}
                  <h1 className="font-heading text-3xl lg:text-4xl font-bold text-foreground mb-4 leading-tight">
                    {resource.resourceTitle || 'Untitled Resource'}
                  </h1>

                  {/* Description */}
                  {resource.description && (
                    <p className="font-paragraph text-lg text-foreground/70 leading-relaxed max-w-3xl">
                      {resource.description}
                    </p>
                  )}
                </motion.div>

                {/* Learning Summary Panel */}
                <LearningSummaryCard
                  resource={resource}
                  progress={progress}
                  isCompleted={isCompleted}
                  onMarkComplete={handleMarkComplete}
                  onContinue={handleContinue}
                />

                {/* Video Player (if video) */}
                {resource.videoUrl && (
                  <VideoPlayer
                    videoUrl={resource.videoUrl}
                    thumbnailUrl={resource.thumbnailImage}
                    title={resource.resourceTitle || 'Video Content'}
                    duration={meta?.estimatedTime}
                    progress={progress}
                  />
                )}

                {/* Thumbnail (if article with image, no video) */}
                {resource.thumbnailImage && !resource.videoUrl && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                    className="rounded-2xl overflow-hidden border border-lavender-200"
                  >
                    <Image
                      src={resource.thumbnailImage}
                      alt={resource.resourceTitle || 'Resource thumbnail'}
                      width={1200}
                      className="w-full aspect-video object-cover"
                    />
                  </motion.div>
                )}

                {/* Why This Matters */}
                {meta && (
                  <WhyThisMatters
                    resource={resource}
                    skillFocus={meta.skillFocus}
                  />
                )}

                {/* Main Content Body */}
                <div id="main-content">
                  {resource.contentBody && (
                    <ContentSection
                      content={resource.contentBody}
                      resourceType={resource.resourceType}
                    />
                  )}
                </div>

                {/* What's Next Panel */}
                <NextStepsPanel
                  currentResource={resource}
                  skillFocus={meta?.skillFocus}
                />
              </motion.div>
            )}
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
}
