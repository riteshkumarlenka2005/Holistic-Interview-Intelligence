import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, Award, Calendar, BarChart, Target, Zap } from 'lucide-react';
import { BaseCrudService } from '@/integrations';
import { PracticeSessions } from '@/entities';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import { format } from 'date-fns';

export default function ProgressPage() {
  const [sessions, setSessions] = useState<PracticeSessions[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadProgressData = async () => {
      try {
        setIsLoading(true);
        const result = await BaseCrudService.getAll<PracticeSessions>(
          'practicesessions',
          {},
          { limit: 50 }
        );

        // Sort by date descending
        const sorted = result.items.sort((a, b) => {
          const dateA = a.sessionDateTime ? new Date(a.sessionDateTime).getTime() : 0;
          const dateB = b.sessionDateTime ? new Date(b.sessionDateTime).getTime() : 0;
          return dateB - dateA;
        });

        setSessions(sorted);
      } catch (error) {
        console.error('Failed to load progress data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadProgressData();
  }, []);

  const calculateStats = () => {
    if (sessions.length === 0) return null;

    const scores = sessions
      .map(s => s.overallReadinessScore || 0)
      .filter(s => s > 0);

    if (scores.length === 0) return null;

    const avgScore = Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
    const highestScore = Math.max(...scores);
    const lowestScore = Math.min(...scores);
    const improvement = scores.length >= 2 ? scores[0] - scores[scores.length - 1] : 0;

    return { avgScore, highestScore, lowestScore, improvement, totalSessions: sessions.length };
  };

  const stats = calculateStats();

  const getScoreColor = (score?: number) => {
    if (!score) return 'text-foreground/50';
    if (score >= 80) return 'text-primary';
    if (score >= 60) return 'text-data-accent';
    return 'text-secondary';
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Header />

      <div className="w-full py-16 px-8 lg:px-16">
        <div className="max-w-[100rem] mx-auto">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="mb-12"
          >
            <h1
              className="font-heading text-5xl lg:text-6xl font-black text-foreground mb-4"
            >
              Your <span className="text-primary">Progress</span>
            </h1>
            <p className="font-paragraph text-lg text-foreground font-semibold">
              Track your improvement and celebrate your achievements
            </p>
          </motion.div>

          {/* Stats Overview */}
          {stats && (
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.1 }}
              >
                <div className="bg-gradient-to-br from-primary/10 to-primary/5 border border-primary/30 rounded-lg p-6">
                  <div className="flex items-center justify-between mb-4">
                    <BarChart className="w-8 h-8 text-primary" />
                    <div className="font-heading text-3xl font-bold text-primary">{stats.avgScore}%</div>
                  </div>
                  <div className="font-paragraph text-sm text-foreground/70">Average Score</div>
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.2 }}
              >
                <div className="bg-gradient-to-br from-primary/10 to-primary/5 border border-primary/30 rounded-lg p-6">
                  <div className="flex items-center justify-between mb-4">
                    <Award className="w-8 h-8 text-primary" />
                    <div className="font-heading text-3xl font-bold text-primary">{stats.highestScore}%</div>
                  </div>
                  <div className="font-paragraph text-sm text-foreground/70">Highest Score</div>
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.3 }}
              >
                <div className="bg-gradient-to-br from-primary/10 to-primary/5 border border-primary/30 rounded-lg p-6">
                  <div className="flex items-center justify-between mb-4">
                    <TrendingUp className="w-8 h-8 text-primary" />
                    <div className="font-heading text-3xl font-bold text-primary">
                      {stats.improvement > 0 ? `+${stats.improvement}` : stats.improvement}%
                    </div>
                  </div>
                  <div className="font-paragraph text-sm text-foreground/70">Total Improvement</div>
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.4 }}
              >
                <div className="bg-gradient-to-br from-primary/10 to-primary/5 border border-primary/30 rounded-lg p-6">
                  <div className="flex items-center justify-between mb-4">
                    <Zap className="w-8 h-8 text-primary" />
                    <div className="font-heading text-3xl font-bold text-primary">{stats.totalSessions}</div>
                  </div>
                  <div className="font-paragraph text-sm text-foreground/70">Total Sessions</div>
                </div>
              </motion.div>
            </div>
          )}

          {/* Progress Timeline */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.5 }}
            className="bg-gradient-to-br from-background to-gradient-start/10 border border-primary/30 rounded-lg p-8 mb-12"
          >
            <h2 className="font-heading text-2xl font-bold text-foreground mb-8">Performance Timeline</h2>

            <div className="min-h-[400px]">
              {isLoading ? (
                <div className="text-center py-24">
                  <div className="font-paragraph text-foreground/50">Loading progress data...</div>
                </div>
              ) : sessions.length > 0 ? (
                <div className="space-y-6">
                  {sessions.map((session, index) => (
                    <motion.div
                      key={session._id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.5, delay: index * 0.05 }}
                      className="relative"
                    >
                      <div className="flex items-start gap-6">
                        {/* Timeline Line */}
                        <div className="flex flex-col items-center">
                          <div className={`w-4 h-4 rounded-full ${getScoreColor(session.overallReadinessScore)} bg-current`} />
                          {index < sessions.length - 1 && (
                            <div className="w-0.5 h-full min-h-[60px] bg-primary/20 mt-2" />
                          )}
                        </div>

                        {/* Content */}
                        <div className="flex-1 pb-8">
                          <div className="bg-background/50 border border-primary/20 rounded-lg p-6">
                            <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
                              <div>
                                <div className="font-paragraph text-sm font-semibold text-foreground mb-2">
                                  {session.sessionType || 'General'} Interview
                                </div>
                                <div className="flex items-center gap-2 font-paragraph text-xs text-foreground/60">
                                  <Calendar className="w-3 h-3" />
                                  {session.sessionDateTime
                                    ? format(new Date(session.sessionDateTime), 'MMMM dd, yyyy • h:mm a')
                                    : 'No date'}
                                </div>
                              </div>
                              <div className={`font-heading text-4xl font-bold ${getScoreColor(session.overallReadinessScore)}`}>
                                {session.overallReadinessScore || 0}%
                              </div>
                            </div>

                            <div className="h-2 bg-background rounded-full overflow-hidden">
                              <div
                                className="h-full bg-gradient-to-r from-primary to-secondary transition-all duration-500"
                                style={{ width: `${session.overallReadinessScore || 0}%` }}
                              />
                            </div>
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-24">
                  <Target className="w-24 h-24 text-primary/30 mx-auto mb-6" />
                  <h3 className="font-heading text-2xl font-bold text-foreground mb-4">No Progress Data Yet</h3>
                  <p className="font-paragraph text-foreground/70">
                    Complete practice sessions to start tracking your progress
                  </p>
                </div>
              )}
            </div>
          </motion.div>

          {/* Skill Breakdown */}
          {stats && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.6 }}
              className="bg-gradient-to-br from-primary/5 to-secondary/5 border border-primary/30 rounded-lg p-8"
            >
              <h2 className="font-heading text-2xl font-bold text-foreground mb-8">Skill Analysis</h2>

              <div className="grid md:grid-cols-2 gap-8">
                <div>
                  <h3 className="font-heading text-lg font-bold text-foreground mb-4">Verbal Communication</h3>
                  <div className="space-y-4">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-paragraph text-sm text-foreground/70">Speech Clarity</span>
                        <span className="font-paragraph text-sm font-semibold text-primary">85%</span>
                      </div>
                      <div className="h-2 bg-background rounded-full overflow-hidden">
                        <div className="h-full bg-gradient-to-r from-primary to-secondary" style={{ width: '85%' }} />
                      </div>
                    </div>

                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-paragraph text-sm text-foreground/70">Filler Words</span>
                        <span className="font-paragraph text-sm font-semibold text-primary">72%</span>
                      </div>
                      <div className="h-2 bg-background rounded-full overflow-hidden">
                        <div className="h-full bg-gradient-to-r from-primary to-secondary" style={{ width: '72%' }} />
                      </div>
                    </div>

                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-paragraph text-sm text-foreground/70">Tone Variation</span>
                        <span className="font-paragraph text-sm font-semibold text-primary">78%</span>
                      </div>
                      <div className="h-2 bg-background rounded-full overflow-hidden">
                        <div className="h-full bg-gradient-to-r from-primary to-secondary" style={{ width: '78%' }} />
                      </div>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="font-heading text-lg font-bold text-foreground mb-4">Non-Verbal Communication</h3>
                  <div className="space-y-4">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-paragraph text-sm text-foreground/70">Eye Contact</span>
                        <span className="font-paragraph text-sm font-semibold text-secondary">68%</span>
                      </div>
                      <div className="h-2 bg-background rounded-full overflow-hidden">
                        <div className="h-full bg-gradient-to-r from-secondary to-primary" style={{ width: '68%' }} />
                      </div>
                    </div>

                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-paragraph text-sm text-foreground/70">Posture</span>
                        <span className="font-paragraph text-sm font-semibold text-secondary">82%</span>
                      </div>
                      <div className="h-2 bg-background rounded-full overflow-hidden">
                        <div className="h-full bg-gradient-to-r from-secondary to-primary" style={{ width: '82%' }} />
                      </div>
                    </div>

                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-paragraph text-sm text-foreground/70">Engagement</span>
                        <span className="font-paragraph text-sm font-semibold text-secondary">75%</span>
                      </div>
                      <div className="h-2 bg-background rounded-full overflow-hidden">
                        <div className="h-full bg-gradient-to-r from-secondary to-primary" style={{ width: '75%' }} />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </div>
      </div>

      <Footer />
    </div>
  );
}
