import { useState } from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { 
  TrendingUp, Award, Target, Calendar, Video, ArrowRight, Zap, 
  BrainCircuit, BarChart3, Activity, ArrowUpRight, ArrowDownRight, Minus
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useMember } from '@/integrations/auth';
import { useApiClient } from '@/lib/apiClient';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import { format } from 'date-fns';
import { 
  Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer,
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip
} from 'recharts';

export default function DashboardPage() {
  const { member } = useMember();
  const { fetchApi } = useApiClient();

  const { data: reports, isLoading: isReportsLoading } = useQuery({
    queryKey: ['reports'],
    queryFn: () => fetchApi('/reports')
  });

  const { data: insightsData, isLoading: isInsightsLoading } = useQuery({
    queryKey: ['insights'],
    queryFn: () => fetchApi('/reports/session/latest/insights')
  });

  const isLoading = isReportsLoading || isInsightsLoading;

  // Process data
  const latestReport = reports && reports.length > 0 ? reports[0] : null;
  const overallScore = latestReport ? latestReport.overall_score * 100 : 0;
  
  // Fake radar data if endpoint doesn't return full details in summary
  // In a real app we'd fetch the full detail for the latest report
  const radarData = [
    { subject: 'Technical', A: 85, fullMark: 100 },
    { subject: 'Communication', A: 78, fullMark: 100 },
    { subject: 'Confidence', A: 82, fullMark: 100 },
    { subject: 'Integrity', A: 95, fullMark: 100 },
    { subject: 'Problem Solving', A: 80, fullMark: 100 },
  ];

  // Fake trend data for demonstration (normally aggregated from reports)
  const trendData = [
    { name: 'Int 1', score: 65 },
    { name: 'Int 2', score: 72 },
    { name: 'Int 3', score: 78 },
    { name: 'Int 4', score: 85 },
  ];

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-primary';
    if (score >= 60) return 'text-data-accent';
    return 'text-secondary';
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Header />

      <div className="w-full py-16 px-8 lg:px-16">
        <div className="max-w-[100rem] mx-auto space-y-12">
          
          {/* 1. Welcome Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h1 className="font-heading text-4xl lg:text-5xl font-black text-foreground mb-2">
              Welcome Back, <span className="text-primary">{member?.firstName || member?.email?.split('@')[0] || 'User'}</span>
            </h1>
            <p className="font-paragraph text-lg text-foreground/70">
              Here's your interview readiness overview
            </p>
          </motion.div>

          {/* 2. AI Insights Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="bg-gradient-to-r from-primary/10 via-primary/5 to-background border border-primary/20 rounded-xl p-6 shadow-sm relative overflow-hidden"
          >
            <div className="absolute top-0 right-0 p-4 opacity-10">
              <BrainCircuit className="w-24 h-24" />
            </div>
            <div className="flex items-center gap-3 mb-4">
              <BrainCircuit className="w-6 h-6 text-primary" />
              <h2 className="font-heading text-xl font-bold">AI Insights</h2>
            </div>
            <div className="space-y-3 relative z-10">
              {isInsightsLoading ? (
                <div className="animate-pulse space-y-2">
                  <div className="h-4 bg-primary/10 rounded w-3/4"></div>
                  <div className="h-4 bg-primary/10 rounded w-1/2"></div>
                </div>
              ) : insightsData?.insights ? (
                insightsData.insights.map((insight: string, idx: number) => (
                  <div key={idx} className="flex items-start gap-2">
                    <div className="mt-1 w-1.5 h-1.5 rounded-full bg-primary flex-shrink-0" />
                    <p className="font-paragraph text-foreground/80">{insight}</p>
                  </div>
                ))
              ) : (
                <p className="text-foreground/60">Complete an interview to generate AI insights.</p>
              )}
            </div>
          </motion.div>

          {/* Grid Layout for remaining components */}
          <div className="grid lg:grid-cols-3 gap-8">
            
            {/* Left Column (Main Metrics) */}
            <div className="lg:col-span-2 space-y-8">
              
              {/* 3. Readiness Score & Executive Summary */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.2 }}
                className="grid md:grid-cols-3 gap-6"
              >
                <div className="md:col-span-1 bg-background border border-border rounded-xl p-6 flex flex-col items-center justify-center text-center shadow-sm">
                  <h3 className="font-heading text-sm text-foreground/60 uppercase tracking-wider mb-2">Readiness Score</h3>
                  <div className={`font-heading text-6xl font-black ${getScoreColor(overallScore)} mb-2`}>
                    {overallScore.toFixed(0)}<span className="text-2xl">%</span>
                  </div>
                  <p className="font-paragraph text-sm text-foreground/70">
                    {overallScore >= 80 ? 'Interview Ready' : overallScore >= 60 ? 'Getting There' : 'Needs Practice'}
                  </p>
                </div>
                
                <div className="md:col-span-2 bg-background border border-border rounded-xl p-6 shadow-sm flex flex-col justify-center">
                  <h3 className="font-heading text-lg font-bold mb-3 flex items-center gap-2">
                    <Activity className="w-5 h-5 text-primary" /> Executive Summary
                  </h3>
                  <p className="font-paragraph text-foreground/80 leading-relaxed">
                    {latestReport ? 
                      "The candidate demonstrated solid technical foundations. Communication is clear, but confidence fluctuates during complex problem-solving. Integrity is exceptionally high." 
                      : "Take your first practice interview to generate an executive summary of your performance."
                    }
                  </p>
                </div>
              </motion.div>

              {/* 4 & 5. Radar & Performance Trend */}
              <div className="grid md:grid-cols-2 gap-6">
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.3 }}
                  className="bg-background border border-border rounded-xl p-6 shadow-sm"
                >
                  <h3 className="font-heading text-lg font-bold mb-4 flex items-center gap-2">
                    <Target className="w-5 h-5 text-primary" /> Skill Radar
                  </h3>
                  <div className="h-[250px] w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
                        <PolarGrid stroke="#e5e7eb" />
                        <PolarAngleAxis dataKey="subject" tick={{ fill: '#6b7280', fontSize: 12 }} />
                        <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                        <Radar name="Score" dataKey="A" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.4} />
                      </RadarChart>
                    </ResponsiveContainer>
                  </div>
                </motion.div>

                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.4 }}
                  className="bg-background border border-border rounded-xl p-6 shadow-sm"
                >
                  <h3 className="font-heading text-lg font-bold mb-4 flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-primary" /> Performance Trend
                  </h3>
                  <div className="h-[250px] w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={trendData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f3f4f6" />
                        <XAxis dataKey="name" tick={{ fill: '#6b7280', fontSize: 12 }} axisLine={false} tickLine={false} />
                        <YAxis domain={[0, 100]} tick={{ fill: '#6b7280', fontSize: 12 }} axisLine={false} tickLine={false} />
                        <RechartsTooltip 
                          contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                        />
                        <Line type="monotone" dataKey="score" stroke="#3b82f6" strokeWidth={3} dot={{ r: 4, fill: '#3b82f6', strokeWidth: 2, stroke: '#fff' }} activeDot={{ r: 6 }} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </motion.div>
              </div>

              {/* 6 & 7. Latest Interview & Question Breakdown */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.5 }}
                className="bg-background border border-border rounded-xl p-6 shadow-sm"
              >
                <div className="flex items-center justify-between mb-6">
                  <h3 className="font-heading text-lg font-bold flex items-center gap-2">
                    <Video className="w-5 h-5 text-primary" /> Latest Interview Details
                  </h3>
                  {latestReport && (
                    <Link to={`/reports/${latestReport.interview_id}/playback`}>
                      <Button variant="outline" size="sm" className="text-primary border-primary/20 hover:bg-primary/5">
                        Watch Playback <ArrowRight className="w-4 h-4 ml-2" />
                      </Button>
                    </Link>
                  )}
                </div>
                
                {latestReport ? (
                  <div className="space-y-4">
                    <div className="flex justify-between items-center p-3 bg-slate-50 rounded-lg">
                      <div>
                        <p className="font-semibold text-sm">Q1: Explain React Virtual DOM</p>
                        <p className="text-xs text-slate-500">Duration: 2:15</p>
                      </div>
                      <div className="flex items-center gap-4">
                        <div className="text-right">
                          <p className="text-xs text-slate-500">Tech Score</p>
                          <p className="font-bold text-green-600">92%</p>
                        </div>
                        <div className="text-right">
                          <p className="text-xs text-slate-500">Comm Score</p>
                          <p className="font-bold text-blue-600">85%</p>
                        </div>
                      </div>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-slate-50 rounded-lg">
                      <div>
                        <p className="font-semibold text-sm">Q2: How do you handle state management?</p>
                        <p className="text-xs text-slate-500">Duration: 3:40</p>
                      </div>
                      <div className="flex items-center gap-4">
                        <div className="text-right">
                          <p className="text-xs text-slate-500">Tech Score</p>
                          <p className="font-bold text-orange-500">75%</p>
                        </div>
                        <div className="text-right">
                          <p className="text-xs text-slate-500">Comm Score</p>
                          <p className="font-bold text-blue-600">88%</p>
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <p className="text-sm text-slate-500 text-center py-4">No recent interviews found.</p>
                )}
              </motion.div>
            </div>

            {/* Right Column (Sidebar) */}
            <div className="space-y-8">
              
              {/* 8. Learning Roadmap */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.6 }}
                className="bg-background border border-border rounded-xl p-6 shadow-sm"
              >
                <h3 className="font-heading text-lg font-bold mb-4 flex items-center gap-2">
                  <Target className="w-5 h-5 text-secondary" /> Learning Roadmap
                </h3>
                <div className="space-y-4 relative before:absolute before:inset-0 before:ml-2.5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-300 before:to-transparent">
                  <div className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                    <div className="flex items-center justify-center w-6 h-6 rounded-full border border-white bg-slate-300 group-[.is-active]:bg-primary text-slate-500 group-[.is-active]:text-emerald-50 shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10">
                      <div className="w-2 h-2 bg-white rounded-full"></div>
                    </div>
                    <div className="w-[calc(100%-2.5rem)] md:w-[calc(50%-1.5rem)] p-3 rounded-lg border border-border bg-background shadow-sm">
                      <p className="text-sm font-bold text-slate-900">Reduce Filler Words</p>
                      <p className="text-xs text-slate-500">High Priority</p>
                    </div>
                  </div>
                  
                  <div className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group">
                    <div className="flex items-center justify-center w-6 h-6 rounded-full border border-white bg-slate-200 text-slate-500 shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10">
                      <div className="w-2 h-2 bg-white rounded-full"></div>
                    </div>
                    <div className="w-[calc(100%-2.5rem)] md:w-[calc(50%-1.5rem)] p-3 rounded-lg border border-border bg-background shadow-sm">
                      <p className="text-sm font-bold text-slate-900">useCallback Deep Dive</p>
                      <p className="text-xs text-slate-500">Medium Priority</p>
                    </div>
                  </div>
                </div>
                <Button variant="outline" className="w-full mt-6 text-sm">View Full Roadmap</Button>
              </motion.div>

              {/* 9. Interview History */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.7 }}
                className="bg-background border border-border rounded-xl p-6 shadow-sm"
              >
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-heading text-lg font-bold flex items-center gap-2">
                    <Calendar className="w-5 h-5 text-slate-500" /> History
                  </h3>
                  <Link to="/reports/compare" className="text-xs font-semibold text-primary hover:underline">
                    Compare
                  </Link>
                </div>
                
                <div className="space-y-3">
                  {reports?.slice(0, 5).map((report: any) => (
                    <div key={report.id} className="flex justify-between items-center p-2 hover:bg-slate-50 rounded-md transition-colors border border-transparent hover:border-slate-100">
                      <div>
                        <p className="text-sm font-semibold truncate w-32">{report.title}</p>
                        <p className="text-xs text-slate-500">{format(new Date(report.created_at), 'MMM dd, yyyy')}</p>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className={`text-sm font-bold ${getScoreColor(report.overall_score * 100)}`}>
                          {(report.overall_score * 100).toFixed(0)}%
                        </span>
                        <Link to={`/reports/${report.interview_id}/playback`}>
                          <ArrowRight className="w-4 h-4 text-slate-400 hover:text-primary transition-colors" />
                        </Link>
                      </div>
                    </div>
                  ))}
                  
                  {(!reports || reports.length === 0) && (
                    <p className="text-sm text-slate-500 text-center py-4">No history available</p>
                  )}
                </div>
                
                <Link to="/practice/new">
                  <Button className="w-full mt-4 bg-primary text-primary-foreground">
                    <Video className="w-4 h-4 mr-2" /> Start Practice
                  </Button>
                </Link>
              </motion.div>

            </div>
          </div>

        </div>
      </div>

      <Footer />
    </div>
  );
}
