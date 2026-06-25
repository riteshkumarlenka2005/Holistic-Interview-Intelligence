import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Video, Calendar, TrendingUp, Mic, Eye, MessageSquare, Award, AlertCircle, CheckCircle, Lightbulb } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import { BaseCrudService } from '@/integrations';
import { PracticeSessions } from '@/entities';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import { format } from 'date-fns';

export default function SessionDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [session, setSession] = useState<PracticeSessions | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadSession = async () => {
      if (!id) return;
      
      try {
        setIsLoading(true);
        const data = await BaseCrudService.getById<PracticeSessions>('practicesessions', id);
        setSession(data);
      } catch (error) {
        console.error('Failed to load session:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadSession();
  }, [id]);

  const getScoreColor = (score?: number) => {
    if (!score) return 'text-foreground/50';
    if (score >= 80) return 'text-primary';
    if (score >= 60) return 'text-data-accent';
    return 'text-secondary';
  };

  const getScoreLabel = (score?: number) => {
    if (!score) return 'Not Evaluated';
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Fair';
    return 'Needs Improvement';
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Header />

      <div className="w-full py-16 px-8 lg:px-16">
        <div className="max-w-[100rem] mx-auto">
          <Link to="/practice">
            <Button variant="outline" className="border-primary/30 text-primary hover:bg-primary/10 rounded mb-8">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Sessions
            </Button>
          </Link>

          <div className="min-h-[600px]">
            {isLoading ? (
              <div className="flex items-center justify-center py-24">
                <LoadingSpinner />
              </div>
            ) : !session ? (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.6 }}
                className="text-center py-24"
              >
                <AlertCircle className="w-24 h-24 text-primary/30 mx-auto mb-6" />
                <h2 className="font-heading text-3xl font-bold text-foreground mb-4">Session Not Found</h2>
                <p className="font-paragraph text-foreground/70 mb-8">
                  The session you're looking for doesn't exist or has been removed.
                </p>
                <Link to="/practice">
                  <Button className="bg-primary text-primary-foreground hover:bg-primary/90 rounded">
                    View All Sessions
                  </Button>
                </Link>
              </motion.div>
            ) : (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
              >
                {/* Header */}
                <div className="mb-12">
                  <div className="flex flex-wrap items-center gap-4 mb-6">
                    <div className="px-4 py-2 bg-primary/10 border border-primary/30 rounded">
                      <span className="font-paragraph text-sm text-primary">{session.sessionType || 'General'}</span>
                    </div>
                    <div className="flex items-center gap-2 font-paragraph text-sm text-foreground/60">
                      <Calendar className="w-4 h-4" />
                      <span>
                        {session.sessionDateTime 
                          ? format(new Date(session.sessionDateTime), 'MMMM dd, yyyy • h:mm a')
                          : 'No date'}
                      </span>
                    </div>
                  </div>

                  <h1 className="font-heading text-5xl lg:text-6xl font-bold text-foreground mb-4">
                    Interview Session <span className="text-primary">Analysis</span>
                  </h1>
                </div>

                {/* Overall Score */}
                <div className="bg-gradient-to-br from-primary/10 to-secondary/10 border border-primary/30 rounded-lg p-8 mb-12">
                  <div className="grid md:grid-cols-2 gap-8 items-center">
                    <div>
                      <h2 className="font-heading text-2xl font-bold text-foreground mb-4">Overall Readiness Score</h2>
                      <div className={`font-heading text-7xl font-bold ${getScoreColor(session.overallReadinessScore)} mb-4`}>
                        {session.overallReadinessScore || 0}%
                      </div>
                      <div className="inline-flex items-center gap-2 px-4 py-2 bg-background/50 backdrop-blur-sm rounded">
                        <Award className="w-5 h-5 text-primary" />
                        <span className="font-paragraph text-sm text-foreground">
                          {getScoreLabel(session.overallReadinessScore)}
                        </span>
                      </div>
                    </div>

                    <div className="space-y-4">
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-paragraph text-sm text-foreground/70">Interview Readiness</span>
                          <span className="font-paragraph text-sm font-semibold text-primary">
                            {session.overallReadinessScore || 0}%
                          </span>
                        </div>
                        <div className="h-3 bg-background rounded-full overflow-hidden">
                          <div
                            className="h-full bg-gradient-to-r from-primary to-secondary transition-all duration-500"
                            style={{ width: `${session.overallReadinessScore || 0}%` }}
                          />
                        </div>
                      </div>

                      {session.recordingUrl && (
                        <div className="pt-4">
                          <a
                            href={session.recordingUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground rounded hover:bg-primary/90 transition-colors duration-300"
                          >
                            <Video className="w-5 h-5" />
                            <span className="font-paragraph text-sm font-semibold">Watch Recording</span>
                          </a>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Analysis Sections */}
                <div className="grid lg:grid-cols-2 gap-8 mb-12">
                  {/* Verbal Analysis */}
                  <div className="bg-gradient-to-br from-background to-gradient-start/10 border border-primary/30 rounded-lg p-8">
                    <div className="flex items-center gap-4 mb-6">
                      <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
                        <Mic className="w-6 h-6 text-primary" />
                      </div>
                      <h3 className="font-heading text-2xl font-bold text-foreground">Verbal Communication</h3>
                    </div>

                    {session.verbalAnalysisSummary ? (
                      <div className="space-y-4">
                        <p className="font-paragraph text-foreground/80 leading-relaxed">
                          {session.verbalAnalysisSummary}
                        </p>
                      </div>
                    ) : (
                      <p className="font-paragraph text-foreground/50 italic">No verbal analysis available</p>
                    )}
                  </div>

                  {/* Non-Verbal Analysis */}
                  <div className="bg-gradient-to-br from-background to-gradient-start/10 border border-primary/30 rounded-lg p-8">
                    <div className="flex items-center gap-4 mb-6">
                      <div className="w-12 h-12 bg-secondary/10 rounded-lg flex items-center justify-center">
                        <Eye className="w-6 h-6 text-secondary" />
                      </div>
                      <h3 className="font-heading text-2xl font-bold text-foreground">Non-Verbal Communication</h3>
                    </div>

                    {session.nonVerbalAnalysisSummary ? (
                      <div className="space-y-4">
                        <p className="font-paragraph text-foreground/80 leading-relaxed">
                          {session.nonVerbalAnalysisSummary}
                        </p>
                      </div>
                    ) : (
                      <p className="font-paragraph text-foreground/50 italic">No non-verbal analysis available</p>
                    )}
                  </div>
                </div>

                {/* Feedback & Recommendations */}
                {session.feedbackSummary && (
                  <div className="bg-gradient-to-br from-primary/5 to-secondary/5 border border-primary/30 rounded-lg p-8 mb-12">
                    <div className="flex items-center gap-4 mb-6">
                      <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
                        <Lightbulb className="w-6 h-6 text-primary" />
                      </div>
                      <h3 className="font-heading text-2xl font-bold text-foreground">Feedback & Recommendations</h3>
                    </div>

                    <div className="space-y-4">
                      <p className="font-paragraph text-foreground/80 leading-relaxed">
                        {session.feedbackSummary}
                      </p>
                    </div>
                  </div>
                )}

                {/* Action Items */}
                <div className="bg-gradient-to-br from-background to-gradient-start/10 border border-primary/30 rounded-lg p-8">
                  <h3 className="font-heading text-2xl font-bold text-foreground mb-6">Next Steps</h3>
                  
                  <div className="space-y-4">
                    <div className="flex items-start gap-4">
                      <div className="w-8 h-8 bg-primary/20 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                        <CheckCircle className="w-5 h-5 text-primary" />
                      </div>
                      <div>
                        <h4 className="font-heading text-lg font-bold text-foreground mb-2">Practice Regularly</h4>
                        <p className="font-paragraph text-foreground/70">
                          Schedule regular practice sessions to build consistency and track improvement over time
                        </p>
                      </div>
                    </div>

                    <div className="flex items-start gap-4">
                      <div className="w-8 h-8 bg-primary/20 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                        <CheckCircle className="w-5 h-5 text-primary" />
                      </div>
                      <div>
                        <h4 className="font-heading text-lg font-bold text-foreground mb-2">Review Resources</h4>
                        <p className="font-paragraph text-foreground/70">
                          Check out our learning resources for targeted tips on improving specific skills
                        </p>
                      </div>
                    </div>

                    <div className="flex items-start gap-4">
                      <div className="w-8 h-8 bg-primary/20 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                        <CheckCircle className="w-5 h-5 text-primary" />
                      </div>
                      <div>
                        <h4 className="font-heading text-lg font-bold text-foreground mb-2">Track Progress</h4>
                        <p className="font-paragraph text-foreground/70">
                          Visit your progress dashboard to see trends and celebrate improvements
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-4 mt-8 pt-8 border-t border-primary/20">
                    <Link to="/practice/new">
                      <Button className="bg-primary text-primary-foreground hover:bg-primary/90 rounded">
                        Start New Session
                      </Button>
                    </Link>
                    <Link to="/resources">
                      <Button variant="outline" className="border-primary/30 text-primary hover:bg-primary/10 rounded">
                        View Resources
                      </Button>
                    </Link>
                    <Link to="/progress">
                      <Button variant="outline" className="border-primary/30 text-primary hover:bg-primary/10 rounded">
                        <TrendingUp className="w-4 h-4 mr-2" />
                        View Progress
                      </Button>
                    </Link>
                  </div>
                </div>
              </motion.div>
            )}
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
}
