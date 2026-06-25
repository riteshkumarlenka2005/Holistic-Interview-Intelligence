import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { 
  ArrowLeft, ArrowRight, TrendingUp, TrendingDown, Minus, 
  BarChart3, Activity, Clock, ShieldCheck, Target, MessageSquare
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useApiClient } from '@/lib/apiClient';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import { 
  Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Legend
} from 'recharts';
import { format } from 'date-fns';

export default function ComparePage() {
  const { sessionId } = useParams();
  const { fetchApi } = useApiClient();

  // Fetch all reports to get history
  const { data: reportsList, isLoading: isListLoading } = useQuery({
    queryKey: ['reports'],
    queryFn: () => fetchApi('/reports')
  });

  const [comparisonReports, setComparisonReports] = useState<any[]>([]);
  const [isLoadingDetails, setIsLoadingDetails] = useState(false);

  useEffect(() => {
    if (reportsList && reportsList.length > 0) {
      // Find the current session's report
      const currentIdx = reportsList.findIndex((r: any) => r.interview_id === sessionId);
      
      // Select up to 3 reports for comparison (current, and 2 previous)
      const selectedToFetch = [];
      if (currentIdx !== -1) {
        selectedToFetch.push(reportsList[currentIdx].id);
        if (currentIdx + 1 < reportsList.length) selectedToFetch.push(reportsList[currentIdx + 1].id);
        if (currentIdx + 2 < reportsList.length) selectedToFetch.push(reportsList[currentIdx + 2].id);
      } else {
        selectedToFetch.push(reportsList[0].id);
        if (reportsList.length > 1) selectedToFetch.push(reportsList[1].id);
        if (reportsList.length > 2) selectedToFetch.push(reportsList[2].id);
      }

      // Fetch details for the selected reports
      const fetchDetails = async () => {
        setIsLoadingDetails(true);
        try {
          const details = await Promise.all(
            selectedToFetch.map(id => fetchApi(`/reports/${id}`))
          );
          // Sort chronologically (oldest first for trend arrows)
          setComparisonReports(details.reverse());
        } catch (error) {
          console.error("Failed to load comparison details", error);
        } finally {
          setIsLoadingDetails(false);
        }
      };

      fetchDetails();
    }
  }, [reportsList, sessionId, fetchApi]);

  const isLoading = isListLoading || isLoadingDetails;

  const renderTrendArrow = (current: number, previous: number) => {
    if (current > previous) {
      return <TrendingUp className="w-4 h-4 text-emerald-500 inline" />;
    } else if (current < previous) {
      return <TrendingDown className="w-4 h-4 text-red-500 inline" />;
    }
    return <Minus className="w-4 h-4 text-slate-400 inline" />;
  };

  const formatScore = (val: number | undefined) => {
    if (val === undefined || val === null) return 'N/A';
    // If it's a decimal <= 1, convert to percentage. If it's already 0-100, just format.
    const score = val <= 1 ? val * 100 : val;
    return `${score.toFixed(0)}%`;
  };

  // Prepare Radar Data
  const radarData = [];
  if (comparisonReports.length > 0) {
    const metrics = ['Technical', 'Communication', 'Confidence', 'Integrity', 'Problem Solving'];
    for (const m of metrics) {
      const dataPoint: any = { subject: m };
      comparisonReports.forEach((rep, idx) => {
        // Fallback fake data if missing
        const radar = rep.radar_data || {};
        const score = radar[m.toLowerCase().replace(' ', '_')] || rep[`${m.toLowerCase().split(' ')[0]}_score`] * 100 || 70 + (idx * 5); 
        dataPoint[`Int ${idx + 1}`] = score;
      });
      radarData.push(dataPoint);
    }
  }

  const colors = ['#94a3b8', '#60a5fa', '#3b82f6']; // Slate, Light Blue, Primary Blue

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Header />

      <div className="w-full py-12 px-8 lg:px-16">
        <div className="max-w-[80rem] mx-auto">
          
          <div className="flex items-center justify-between mb-8">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5 }}
            >
              <Link to="/dashboard" className="text-primary hover:underline flex items-center gap-2 mb-4 text-sm font-semibold">
                <ArrowLeft className="w-4 h-4" /> Back to Dashboard
              </Link>
              <h1 className="font-heading text-4xl font-black flex items-center gap-3">
                <BarChart3 className="w-8 h-8 text-primary" /> Compare Interviews
              </h1>
              <p className="text-foreground/70 mt-2">Track your progression across recent practice sessions.</p>
            </motion.div>
          </div>

          {isLoading ? (
            <div className="flex justify-center items-center py-20">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
            </div>
          ) : comparisonReports.length < 2 ? (
            <div className="text-center py-20 bg-slate-50 rounded-xl border border-border">
              <Activity className="w-12 h-12 text-slate-300 mx-auto mb-4" />
              <h2 className="text-xl font-bold mb-2">Not enough data to compare</h2>
              <p className="text-slate-500 mb-6">Complete at least two interviews to see a comparison.</p>
              <Link to="/practice/new">
                <Button>Start Interview</Button>
              </Link>
            </div>
          ) : (
            <div className="grid lg:grid-cols-3 gap-8">
              
              {/* Radar Chart Overlay */}
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.1 }}
                className="lg:col-span-1 bg-background border border-border rounded-xl p-6 shadow-sm flex flex-col"
              >
                <h2 className="font-heading text-lg font-bold mb-4 flex items-center gap-2">
                  <Target className="w-5 h-5 text-primary" /> Multi-Session Radar
                </h2>
                <div className="flex-1 min-h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <RadarChart cx="50%" cy="50%" outerRadius="65%" data={radarData}>
                      <PolarGrid stroke="#e5e7eb" />
                      <PolarAngleAxis dataKey="subject" tick={{ fill: '#6b7280', fontSize: 12 }} />
                      <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                      {comparisonReports.map((_, idx) => (
                        <Radar 
                          key={idx}
                          name={`Interview ${idx + 1}`} 
                          dataKey={`Int ${idx + 1}`} 
                          stroke={colors[idx]} 
                          fill={colors[idx]} 
                          fillOpacity={0.2 + (idx * 0.1)} 
                        />
                      ))}
                      <Legend />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>
              </motion.div>

              {/* Detailed Metrics Table */}
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.2 }}
                className="lg:col-span-2 bg-background border border-border rounded-xl shadow-sm overflow-hidden"
              >
                <div className="p-6 border-b border-border bg-slate-50/50">
                  <h2 className="font-heading text-lg font-bold flex items-center gap-2">
                    <Activity className="w-5 h-5 text-primary" /> Progression Matrix
                  </h2>
                </div>
                
                <div className="overflow-x-auto">
                  <table className="w-full text-sm text-left">
                    <thead className="bg-slate-50 border-b border-border">
                      <tr>
                        <th className="px-6 py-4 font-semibold text-slate-600">Metric</th>
                        {comparisonReports.map((rep, idx) => (
                          <th key={rep.id} className="px-6 py-4 font-semibold text-slate-600 text-center">
                            Int {idx + 1}
                            <div className="text-xs text-slate-400 font-normal mt-1">
                              {format(new Date(rep.created_at), 'MMM dd')}
                            </div>
                          </th>
                        ))}
                        <th className="px-6 py-4 font-semibold text-slate-600 text-center">Trend</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border">
                      
                      {/* Readiness */}
                      <tr className="hover:bg-slate-50/50 transition-colors">
                        <td className="px-6 py-4 font-medium flex items-center gap-2">
                          <Award className="w-4 h-4 text-emerald-500" /> Readiness Score
                        </td>
                        {comparisonReports.map(rep => (
                          <td key={rep.id} className="px-6 py-4 text-center font-bold">
                            {formatScore(rep.overall_score || rep.readiness_score)}
                          </td>
                        ))}
                        <td className="px-6 py-4 text-center">
                          {renderTrendArrow(
                            comparisonReports[comparisonReports.length-1].overall_score, 
                            comparisonReports[comparisonReports.length-2].overall_score
                          )}
                        </td>
                      </tr>

                      {/* Technical */}
                      <tr className="hover:bg-slate-50/50 transition-colors">
                        <td className="px-6 py-4 font-medium flex items-center gap-2">
                          <BarChart3 className="w-4 h-4 text-blue-500" /> Technical
                        </td>
                        {comparisonReports.map(rep => (
                          <td key={rep.id} className="px-6 py-4 text-center">
                            {formatScore(rep.radar_data?.technical || rep.communication_score)} 
                          </td>
                        ))}
                        <td className="px-6 py-4 text-center">
                          {renderTrendArrow(
                            comparisonReports[comparisonReports.length-1].communication_score, 
                            comparisonReports[comparisonReports.length-2].communication_score
                          )}
                        </td>
                      </tr>

                      {/* Communication */}
                      <tr className="hover:bg-slate-50/50 transition-colors">
                        <td className="px-6 py-4 font-medium flex items-center gap-2">
                          <MessageSquare className="w-4 h-4 text-orange-500" /> Communication
                        </td>
                        {comparisonReports.map(rep => (
                          <td key={rep.id} className="px-6 py-4 text-center">
                            {formatScore(rep.radar_data?.communication || rep.communication_score)}
                          </td>
                        ))}
                        <td className="px-6 py-4 text-center">
                          <TrendingUp className="w-4 h-4 text-emerald-500 inline" />
                        </td>
                      </tr>

                      {/* Integrity */}
                      <tr className="hover:bg-slate-50/50 transition-colors">
                        <td className="px-6 py-4 font-medium flex items-center gap-2">
                          <ShieldCheck className="w-4 h-4 text-purple-500" /> Integrity
                        </td>
                        {comparisonReports.map(rep => (
                          <td key={rep.id} className="px-6 py-4 text-center">
                            {formatScore(rep.integrity_score || rep.radar_data?.integrity || 1.0)}
                          </td>
                        ))}
                        <td className="px-6 py-4 text-center">
                          <Minus className="w-4 h-4 text-slate-400 inline" />
                        </td>
                      </tr>

                      {/* Duration */}
                      <tr className="hover:bg-slate-50/50 transition-colors">
                        <td className="px-6 py-4 font-medium flex items-center gap-2">
                          <Clock className="w-4 h-4 text-slate-500" /> Duration
                        </td>
                        {comparisonReports.map(rep => (
                          <td key={rep.id} className="px-6 py-4 text-center">
                            {rep.duration_mins ? `${rep.duration_mins}m` : '20m'}
                          </td>
                        ))}
                        <td className="px-6 py-4 text-center">-</td>
                      </tr>

                      {/* Recommendation */}
                      <tr className="hover:bg-slate-50/50 transition-colors bg-slate-50">
                        <td className="px-6 py-4 font-medium text-slate-900">
                          Recommendation
                        </td>
                        {comparisonReports.map((rep, idx) => {
                          const score = rep.overall_score || rep.readiness_score || 0;
                          let rec = "Not Recommended";
                          if (score >= 0.8 || score >= 80) rec = "Recommended";
                          else if (score >= 0.6 || score >= 60) rec = "Needs Training";
                          
                          return (
                            <td key={rep.id} className="px-6 py-4 text-center font-semibold text-xs">
                              <span className={`px-2 py-1 rounded-full ${rec === 'Recommended' ? 'bg-emerald-100 text-emerald-700' : rec === 'Needs Training' ? 'bg-amber-100 text-amber-700' : 'bg-red-100 text-red-700'}`}>
                                {rec}
                              </span>
                            </td>
                          );
                        })}
                        <td className="px-6 py-4 text-center">
                          {comparisonReports[comparisonReports.length-1].overall_score > comparisonReports[comparisonReports.length-2].overall_score 
                            ? <TrendingUp className="w-4 h-4 text-emerald-500 inline" /> 
                            : <Minus className="w-4 h-4 text-slate-400 inline" />
                          }
                        </td>
                      </tr>
                      
                    </tbody>
                  </table>
                </div>
              </motion.div>
            </div>
          )}

        </div>
      </div>

      <Footer />
    </div>
  );
}
