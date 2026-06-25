import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { TrendingUp, Award, Target, Calendar, Video, ArrowRight, Zap, Eye, Mic } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { BaseCrudService } from '@/integrations';
import { PracticeSessions } from '@/entities';
import { useMember } from '@/integrations';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import { format } from 'date-fns';

export default function DashboardPage() {
  const { member } = useMember();
  const [sessions, setSessions] = useState<PracticeSessions[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [stats, setStats] = useState({
    averageScore: 0,
    totalSessions: 0,
    improvement: 0,
    strongestSkill: 'Communication',
    weakestSkill: 'Eye Contact'
  });

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setIsLoading(true);
        const result = await BaseCrudService.getAll<PracticeSessions>(
          'practicesessions',
          {},
          { limit: 5 }
        );

        setSessions(result.items);

        // Calculate stats
        if (result.items.length > 0) {
          const scores = result.items
            .map(s => s.overallReadinessScore || 0)
            .filter(s => s > 0);

          const avgScore = scores.length > 0
            ? Math.round(scores.reduce((a, b) => a + b, 0) / scores.length)
            : 0;

          const improvement = scores.length >= 2
            ? Math.round(scores[0] - scores[scores.length - 1])
            : 0;

          setStats({
            averageScore: avgScore,
            totalSessions: result.totalCount,
            improvement,
            strongestSkill: avgScore >= 70 ? 'Verbal Communication' : 'Engagement',
            weakestSkill: avgScore < 70 ? 'Eye Contact' : 'Filler Words'
          });
        }
      } catch (error) {
        console.error('Failed to load dashboard data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadDashboardData();
  }, []);

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
          {/* Welcome Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="mb-12"
          >
            <h1
              className="font-heading text-5xl lg:text-6xl font-black text-foreground mb-4"
            >
              Welcome Back, <span className="text-primary">{member?.profile?.nickname || 'User'}</span>
            </h1>
            <p className="font-paragraph text-lg text-foreground font-semibold">
              Here's your interview readiness overview
            </p>
          </motion.div>

          {/* Stats Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
            >
              <div className="bg-gradient-to-br from-primary/10 to-primary/5 border border-primary/30 rounded-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <Award className="w-8 h-8 text-primary" />
                  <div className="font-heading text-3xl font-bold text-primary">
                    {isLoading ? '--' : stats.averageScore}%
                  </div>
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
                  <Video className="w-8 h-8 text-primary" />
                  <div className="font-heading text-3xl font-bold text-primary">
                    {isLoading ? '--' : stats.totalSessions}
                  </div>
                </div>
                <div className="font-paragraph text-sm text-foreground/70">Total Sessions</div>
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
                    {isLoading ? '--' : stats.improvement > 0 ? `+${stats.improvement}` : stats.improvement}%
                  </div>
                </div>
                <div className="font-paragraph text-sm text-foreground/70">Improvement</div>
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
                  <div className="font-heading text-3xl font-bold text-primary">
                    {isLoading ? '--' : Math.min(stats.totalSessions * 2, 100)}
                  </div>
                </div>
                <div className="font-paragraph text-sm text-foreground/70">Practice Streak</div>
              </div>
            </motion.div>
          </div>

          {/* Main Content Grid */}
          <div className="grid lg:grid-cols-3 gap-8 mb-12">
            {/* Recent Sessions */}
            <div className="lg:col-span-2">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.5 }}
                className="bg-gradient-to-br from-background to-gradient-start/10 border border-primary/30 rounded-lg p-8"
              >
                <div className="flex items-center justify-between mb-6">
                  <h2 className="font-heading text-2xl font-bold text-foreground">Recent Sessions</h2>
                  <Link to="/practice">
                    <Button variant="outline" className="border-primary/30 text-primary hover:bg-primary/10 rounded text-sm">
                      View All
                    </Button>
                  </Link>
                </div>

                <div className="space-y-4">
                  {isLoading ? (
                    <div className="text-center py-12">
                      <div className="font-paragraph text-foreground/50">Loading sessions...</div>
                    </div>
                  ) : sessions.length > 0 ? (
                    sessions.map((session) => (
                      <Link key={session._id} to={`/practice/${session._id}`}>
                        <div className="flex items-center justify-between p-4 bg-background/50 border border-primary/20 rounded hover:border-primary/50 transition-all duration-300 group">
                          <div className="flex items-center gap-4">
                            <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
                              <Video className="w-6 h-6 text-primary" />
                            </div>
                            <div>
                              <div className="font-paragraph text-sm font-semibold text-foreground mb-1">
                                {session.sessionType || 'General'} Interview
                              </div>
                              <div className="flex items-center gap-2 font-paragraph text-xs text-foreground/60">
                                <Calendar className="w-3 h-3" />
                                {session.sessionDateTime
                                  ? format(new Date(session.sessionDateTime), 'MMM dd, yyyy')
                                  : 'No date'}
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center gap-4">
                            <div className={`font-heading text-2xl font-bold ${getScoreColor(session.overallReadinessScore)}`}>
                              {session.overallReadinessScore || 0}%
                            </div>
                            <ArrowRight className="w-5 h-5 text-primary group-hover:translate-x-1 transition-transform duration-300" />
                          </div>
                        </div>
                      </Link>
                    ))
                  ) : (
                    <div className="text-center py-12">
                      <Video className="w-16 h-16 text-primary/30 mx-auto mb-4" />
                      <p className="font-paragraph text-foreground/50 mb-4">No sessions yet</p>
                      <Link to="/practice/new">
                        <Button className="bg-primary text-primary-foreground hover:bg-primary/90 rounded">
                          Start First Session
                        </Button>
                      </Link>
                    </div>
                  )}
                </div>
              </motion.div>
            </div>

            {/* Strengths & Weaknesses */}
            <div className="space-y-8">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.6 }}
                className="bg-gradient-to-br from-primary/10 to-primary/5 border border-primary/30 rounded-lg p-6"
              >
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-10 h-10 bg-primary/20 rounded-lg flex items-center justify-center">
                    <Target className="w-5 h-5 text-primary" />
                  </div>
                  <h3 className="font-heading text-xl font-bold text-foreground">Strengths</h3>
                </div>

                <div className="space-y-4">
                  <div className="flex items-start gap-3">
                    <Mic className="w-5 h-5 text-primary flex-shrink-0 mt-1" />
                    <div>
                      <div className="font-paragraph text-sm font-semibold text-foreground mb-1">
                        {stats.strongestSkill}
                      </div>
                      <div className="font-paragraph text-xs text-foreground/60">
                        Consistently strong performance
                      </div>
                    </div>
                  </div>

                  <div className="flex items-start gap-3">
                    <Award className="w-5 h-5 text-primary flex-shrink-0 mt-1" />
                    <div>
                      <div className="font-paragraph text-sm font-semibold text-foreground mb-1">
                        Confidence
                      </div>
                      <div className="font-paragraph text-xs text-foreground/60">
                        Shows steady improvement
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.7 }}
                className="bg-gradient-to-br from-secondary/10 to-secondary/5 border border-secondary/30 rounded-lg p-6"
              >
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-10 h-10 bg-secondary/20 rounded-lg flex items-center justify-center">
                    <TrendingUp className="w-5 h-5 text-secondary" />
                  </div>
                  <h3 className="font-heading text-xl font-bold text-foreground">Areas to Improve</h3>
                </div>

                <div className="space-y-4">
                  <div className="flex items-start gap-3">
                    <Eye className="w-5 h-5 text-secondary flex-shrink-0 mt-1" />
                    <div>
                      <div className="font-paragraph text-sm font-semibold text-foreground mb-1">
                        {stats.weakestSkill}
                      </div>
                      <div className="font-paragraph text-xs text-foreground/60">
                        Focus area for next session
                      </div>
                    </div>
                  </div>

                  <Link to="/resources">
                    <Button variant="outline" className="w-full border-secondary/30 text-secondary hover:bg-secondary/10 rounded text-sm">
                      View Resources
                    </Button>
                  </Link>
                </div>
              </motion.div>
            </div>
          </div>

          {/* Quick Actions */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.8 }}
            className="bg-gradient-to-br from-primary/5 to-secondary/5 border border-primary/30 rounded-lg p-8"
          >
            <h2 className="font-heading text-2xl font-bold text-foreground mb-6">Quick Actions</h2>

            <div className="grid md:grid-cols-3 gap-4">
              <Link to="/practice/new">
                <Button className="w-full bg-primary text-primary-foreground hover:bg-primary/90 rounded py-6">
                  <Video className="w-5 h-5 mr-2" />
                  New Practice Session
                </Button>
              </Link>

              <Link to="/progress">
                <Button variant="outline" className="w-full border-primary/30 text-primary hover:bg-primary/10 rounded py-6">
                  <TrendingUp className="w-5 h-5 mr-2" />
                  View Progress
                </Button>
              </Link>

              <Link to="/resources">
                <Button variant="outline" className="w-full border-primary/30 text-primary hover:bg-primary/10 rounded py-6">
                  <Target className="w-5 h-5 mr-2" />
                  Learning Resources
                </Button>
              </Link>
            </div>
          </motion.div>
        </div>
      </div>

      <Footer />
    </div>
  );
}
