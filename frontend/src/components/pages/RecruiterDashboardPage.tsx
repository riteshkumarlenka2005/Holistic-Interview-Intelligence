import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { 
  Users, Search, Filter, ChevronDown, CheckCircle2, 
  AlertCircle, XCircle, ArrowRight, BarChart3, Clock, ExternalLink
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useMember } from '@/integrations/auth';
import { useApiClient } from '@/lib/apiClient';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import { format } from 'date-fns';

export default function RecruiterDashboardPage() {
  const { member } = useMember();
  const { fetchApi } = useApiClient();
  const [searchTerm, setSearchTerm] = useState('');

  // Fetch recruiter dashboard data
  const { data: dashboardData, isLoading } = useQuery({
    queryKey: ['recruiter-dashboard'],
    queryFn: () => fetchApi('/recruiter/dashboard')
  });

  const getRecommendationBadge = (rec: string) => {
    if (rec.includes('Recommended with') || rec.includes('Needs Training')) {
      return <span className="flex items-center gap-1 px-2.5 py-1 rounded-full bg-amber-100 text-amber-700 text-xs font-semibold"><AlertCircle className="w-3 h-3" /> {rec}</span>;
    } else if (rec.includes('Not Recommended')) {
      return <span className="flex items-center gap-1 px-2.5 py-1 rounded-full bg-red-100 text-red-700 text-xs font-semibold"><XCircle className="w-3 h-3" /> {rec}</span>;
    }
    return <span className="flex items-center gap-1 px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-700 text-xs font-semibold"><CheckCircle2 className="w-3 h-3" /> {rec}</span>;
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-emerald-600';
    if (score >= 60) return 'text-amber-600';
    return 'text-red-600';
  };

  const filteredCandidates = dashboardData?.filter((c: any) => 
    c.name.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  return (
    <div className="min-h-screen bg-slate-50 text-foreground">
      <Header />

      <div className="w-full py-12 px-8 lg:px-16">
        <div className="max-w-[100rem] mx-auto space-y-8">
          
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5 }}
            >
              <h1 className="font-heading text-4xl font-black text-slate-900 mb-2">
                Hiring Dashboard
              </h1>
              <p className="text-slate-500">Welcome back, {member?.firstName || member?.email?.split('@')[0]}. Here are your candidate evaluations.</p>
            </motion.div>
            
            <motion.div 
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5 }}
              className="flex items-center gap-3"
            >
              <div className="relative">
                <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                <input 
                  type="text" 
                  placeholder="Search candidates..." 
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-9 pr-4 py-2 border border-border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 w-64"
                />
              </div>
              <Button variant="outline" className="gap-2 bg-white">
                <Filter className="w-4 h-4" /> Filter <ChevronDown className="w-4 h-4" />
              </Button>
            </motion.div>
          </div>

          <div className="grid lg:grid-cols-4 gap-6">
            
            {/* Quick Stats Sidebar */}
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="lg:col-span-1 space-y-6"
            >
              <div className="bg-white border border-border rounded-xl p-6 shadow-sm">
                <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-4">Pipeline Overview</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="flex items-center gap-2 text-slate-600"><Users className="w-4 h-4 text-primary" /> Total Evaluated</span>
                    <span className="font-bold text-slate-900">{dashboardData?.length || 0}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="flex items-center gap-2 text-slate-600"><CheckCircle2 className="w-4 h-4 text-emerald-500" /> Recommended</span>
                    <span className="font-bold text-slate-900">{dashboardData?.filter((c: any) => c.readiness_score >= 80).length || 0}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="flex items-center gap-2 text-slate-600"><AlertCircle className="w-4 h-4 text-amber-500" /> Needs Review</span>
                    <span className="font-bold text-slate-900">{dashboardData?.filter((c: any) => c.readiness_score >= 60 && c.readiness_score < 80).length || 0}</span>
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-br from-primary to-primary/80 border border-primary/20 rounded-xl p-6 text-white shadow-sm">
                <h3 className="font-heading text-lg font-bold mb-2">Top Candidate</h3>
                {dashboardData && dashboardData.length > 0 ? (
                  <>
                    <p className="text-3xl font-black mb-1">{[...dashboardData].sort((a,b) => b.readiness_score - a.readiness_score)[0].name}</p>
                    <p className="text-primary-foreground/80 mb-4">Readiness: {[...dashboardData].sort((a,b) => b.readiness_score - a.readiness_score)[0].readiness_score}%</p>
                    <Link to={`/reports/${[...dashboardData].sort((a,b) => b.readiness_score - a.readiness_score)[0].latest_session_id}/playback`}>
                      <Button className="w-full bg-white text-primary hover:bg-white/90">Review Interview</Button>
                    </Link>
                  </>
                ) : (
                  <p className="text-primary-foreground/80">No candidates evaluated yet.</p>
                )}
              </div>
            </motion.div>

            {/* Candidate Table */}
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="lg:col-span-3 bg-white border border-border rounded-xl shadow-sm overflow-hidden flex flex-col"
            >
              <div className="p-6 border-b border-border flex justify-between items-center bg-slate-50/50">
                <h2 className="font-heading text-lg font-bold text-slate-900">Recent Evaluations</h2>
              </div>
              
              <div className="flex-1 overflow-auto">
                <table className="w-full text-sm text-left whitespace-nowrap">
                  <thead className="bg-slate-50 sticky top-0 z-10 border-b border-border shadow-sm">
                    <tr>
                      <th className="px-6 py-4 font-semibold text-slate-600">Candidate</th>
                      <th className="px-6 py-4 font-semibold text-slate-600">Readiness</th>
                      <th className="px-6 py-4 font-semibold text-slate-600 text-center">Technical</th>
                      <th className="px-6 py-4 font-semibold text-slate-600 text-center">Communication</th>
                      <th className="px-6 py-4 font-semibold text-slate-600 text-center">Integrity</th>
                      <th className="px-6 py-4 font-semibold text-slate-600 text-center">Recommendation</th>
                      <th className="px-6 py-4 font-semibold text-slate-600 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {isLoading ? (
                      <tr>
                        <td colSpan={7} className="px-6 py-12 text-center text-slate-500">
                          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
                          Loading candidate data...
                        </td>
                      </tr>
                    ) : filteredCandidates.length > 0 ? (
                      filteredCandidates.map((c: any) => (
                        <tr key={c.candidate_id} className="hover:bg-slate-50 transition-colors group">
                          <td className="px-6 py-4">
                            <div className="font-semibold text-slate-900">{c.name}</div>
                            <div className="text-xs text-slate-500 flex items-center gap-1 mt-1">
                              <Clock className="w-3 h-3" /> {format(new Date(c.interview_date), 'MMM dd, yyyy')}
                            </div>
                          </td>
                          <td className="px-6 py-4">
                            <div className="flex items-center gap-2">
                              <div className="w-full max-w-[100px] h-2 bg-slate-100 rounded-full overflow-hidden">
                                <div 
                                  className={`h-full rounded-full ${c.readiness_score >= 80 ? 'bg-emerald-500' : c.readiness_score >= 60 ? 'bg-amber-500' : 'bg-red-500'}`} 
                                  style={{ width: `${c.readiness_score}%` }}
                                />
                              </div>
                              <span className={`font-bold ${getScoreColor(c.readiness_score)}`}>{c.readiness_score}%</span>
                            </div>
                          </td>
                          <td className={`px-6 py-4 text-center font-semibold ${getScoreColor(c.technical_score)}`}>
                            {c.technical_score}%
                          </td>
                          <td className={`px-6 py-4 text-center font-semibold ${getScoreColor(c.communication_score)}`}>
                            {c.communication_score}%
                          </td>
                          <td className={`px-6 py-4 text-center font-semibold ${getScoreColor(c.integrity_score)}`}>
                            {c.integrity_score}%
                          </td>
                          <td className="px-6 py-4 text-center">
                            <div className="flex justify-center">
                              {getRecommendationBadge(c.recommendation)}
                            </div>
                          </td>
                          <td className="px-6 py-4 text-right">
                            <Link to={`/reports/${c.latest_session_id}/playback`}>
                              <Button variant="ghost" size="sm" className="opacity-0 group-hover:opacity-100 transition-opacity text-primary hover:text-primary hover:bg-primary/10">
                                View Report <ExternalLink className="w-4 h-4 ml-2" />
                              </Button>
                            </Link>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={7} className="px-6 py-12 text-center text-slate-500">
                          No candidates found matching your criteria.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </motion.div>
          </div>

        </div>
      </div>

      <Footer />
    </div>
  );
}
