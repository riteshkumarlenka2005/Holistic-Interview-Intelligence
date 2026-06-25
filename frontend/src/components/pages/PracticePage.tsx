import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Video, Calendar, Clock, TrendingUp, Plus, Filter } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { BaseCrudService } from '@/integrations';
import { PracticeSessions } from '@/entities';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import { format } from 'date-fns';

export default function PracticePage() {
  const [sessions, setSessions] = useState<PracticeSessions[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filterType, setFilterType] = useState<string>('all');
  const [hasNext, setHasNext] = useState(false);
  const [skip, setSkip] = useState(0);
  const pageSize = 12;

  const loadSessions = async (skipValue: number = 0, currentFilter: string = filterType) => {
    try {
      setIsLoading(true);

      // Build query options based on filter
      const queryOptions: Record<string, string> = {};
      if (currentFilter !== 'all') {
        queryOptions.sessionType = currentFilter;
      }



      const result = await BaseCrudService.getAll<PracticeSessions>(
        'practicesessions',
        queryOptions,
        { limit: pageSize, skip: skipValue }
      );



      if (skipValue === 0) {
        setSessions(result.items);
      } else {
        setSessions(prev => [...prev, ...result.items]);
      }

      setHasNext(result.hasNext);
      setSkip(result.nextSkip || 0);
    } catch (error) {
      console.error('Failed to load sessions:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {

    // Reset pagination and reload when filter changes
    setSkip(0);
    loadSessions(0, filterType);
  }, [filterType]);

  // Sessions are already filtered from the service
  const filteredSessions = sessions;

  const sessionTypes = ['all', 'Behavioral', 'Technical', 'HR'];

  const getScoreColor = (score?: number) => {
    if (!score) return 'text-foreground/50';
    if (score >= 80) return 'text-primary';
    if (score >= 60) return 'text-data-accent';
    return 'text-secondary';
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Header />

      {/* Hero Section */}
      <section className="relative w-full max-w-[120rem] mx-auto py-24 px-8 lg:px-16">
        <div className="max-w-[100rem] mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center mb-16"
          >
            <h1
              className="font-heading text-6xl lg:text-8xl font-black text-foreground mb-6"
            >
              Practice <span className="text-primary">Sessions</span>
            </h1>
            <p className="font-paragraph text-lg text-foreground font-semibold max-w-3xl mx-auto mb-8">
              Review your recorded interview practice sessions and track your improvement over time
            </p>

            <Link to="/practice/new">
              <Button className="bg-primary text-primary-foreground hover:bg-primary/90 px-8 py-6 text-lg font-semibold rounded transition-all duration-300 hover:scale-105">
                <Plus className="w-5 h-5 mr-2" />
                Start New Session
              </Button>
            </Link>
          </motion.div>

          {/* Filters */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="flex items-center gap-4 mb-12 flex-wrap"
          >
            <div className="flex items-center gap-2">
              <Filter className="w-5 h-5 text-primary" />
              <span className="font-paragraph text-sm text-foreground/70">Filter by type:</span>
            </div>
            {sessionTypes.map((type) => (
              <button
                key={type}
                onClick={() => setFilterType(type)}
                className={`px-4 py-2 rounded font-paragraph text-sm transition-all duration-300 ${filterType === type
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-primary/10 text-foreground/70 hover:bg-primary/20'
                  }`}
              >
                {type.charAt(0).toUpperCase() + type.slice(1)}
              </button>
            ))}
          </motion.div>

          {/* Sessions Grid */}
          <div className="min-h-[600px]">
            {isLoading && sessions.length === 0 ? null : filteredSessions.length > 0 ? (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.6 }}
                className="grid md:grid-cols-2 lg:grid-cols-3 gap-8"
              >
                {filteredSessions.map((session, index) => (
                  <motion.div
                    key={session._id}
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: index * 0.05 }}
                  >
                    <Link to={`/practice/${session._id}`}>
                      <div className="group bg-gradient-to-br from-background to-gradient-start/10 border border-primary/30 rounded-lg overflow-hidden h-full transition-all duration-300 hover:border-primary hover:shadow-lg hover:shadow-primary/20">
                        <div className="aspect-video bg-gradient-to-br from-primary/20 to-secondary/20 relative overflow-hidden">
                          <div className="absolute inset-0 flex items-center justify-center">
                            <Video className="w-16 h-16 text-primary/50" />
                          </div>
                          <div className="absolute top-4 right-4 px-3 py-1 bg-background/80 backdrop-blur-sm rounded text-xs font-paragraph text-primary border border-primary/30">
                            {session.sessionType || 'General'}
                          </div>
                        </div>

                        <div className="p-6">
                          <div className="flex items-center gap-2 mb-4 text-sm font-paragraph text-foreground/60">
                            <Calendar className="w-4 h-4" />
                            <span>
                              {session.sessionDateTime
                                ? format(new Date(session.sessionDateTime), 'MMM dd, yyyy')
                                : 'No date'}
                            </span>
                          </div>

                          <div className="mb-4">
                            <div className="flex items-center justify-between mb-2">
                              <span className="font-paragraph text-sm text-foreground/70">Readiness Score</span>
                              <span className={`font-heading text-2xl font-bold ${getScoreColor(session.overallReadinessScore)}`}>
                                {session.overallReadinessScore || 0}%
                              </span>
                            </div>
                            <div className="h-2 bg-background rounded-full overflow-hidden">
                              <div
                                className="h-full bg-gradient-to-r from-primary to-secondary transition-all duration-500"
                                style={{ width: `${session.overallReadinessScore || 0}%` }}
                              />
                            </div>
                          </div>

                          <div className="flex items-center justify-between pt-4 border-t border-primary/20">
                            <span className="font-paragraph text-sm text-foreground/70">View Details</span>
                            <TrendingUp className="w-5 h-5 text-primary group-hover:translate-x-1 transition-transform duration-300" />
                          </div>
                        </div>
                      </div>
                    </Link>
                  </motion.div>
                ))}
              </motion.div>
            ) : (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.6 }}
                className="text-center py-24"
              >
                <Video className="w-24 h-24 text-primary/30 mx-auto mb-6" />
                <h3 className="font-heading text-2xl font-bold text-foreground mb-4">
                  {filterType === 'all' ? 'No Sessions Yet' : `No ${filterType} Sessions`}
                </h3>
                <p className="font-paragraph text-foreground/70 mb-8">
                  {filterType === 'all'
                    ? 'Start your first practice session to begin improving your interview skills'
                    : 'Try a different filter or start a new session'}
                </p>
                <Link to="/practice/new">
                  <Button className="bg-primary text-primary-foreground hover:bg-primary/90 px-8 py-6 text-lg font-semibold rounded">
                    <Plus className="w-5 h-5 mr-2" />
                    Start New Session
                  </Button>
                </Link>
              </motion.div>
            )}
          </div>

          {/* Load More */}
          {hasNext && filteredSessions.length > 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6 }}
              className="text-center mt-12"
            >
              <Button
                onClick={() => loadSessions(skip)}
                disabled={isLoading}
                variant="outline"
                className="border-2 border-primary text-primary hover:bg-primary/10 px-8 py-6 text-lg font-semibold rounded"
              >
                {isLoading ? 'Loading...' : 'Load More Sessions'}
              </Button>
            </motion.div>
          )}
        </div>
      </section>

      <Footer />
    </div>
  );
}
