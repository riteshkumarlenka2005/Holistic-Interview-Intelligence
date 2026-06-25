import { useState, useEffect, useRef, useMemo } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { 
  Play, Pause, FastForward, Rewind, SkipBack, ArrowLeft,
  Download, Share2, Video, MessageSquare, ShieldAlert,
  BrainCircuit, Activity, BarChart3, ChevronDown
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useApiClient } from '@/lib/apiClient';
import Header from '@/components/Header';
import Footer from '@/components/Footer';

export default function PlaybackPage() {
  const { sessionId } = useParams();
  const { fetchApi, API_URL } = useApiClient();

  // Fetch reports for session
  const { data: sessionReports, isLoading } = useQuery({
    queryKey: ['session-reports', sessionId],
    queryFn: () => fetchApi(`/reports/session/${sessionId}`)
  });

  // Export handlers
  const handleExport = (format: string) => {
    if (!reportId) return;
    const token = localStorage.getItem('access_token');
    const url = `${API_URL}/reports/${reportId}/export?format=${format}`;
    
    // Create a temporary link to trigger download with auth
    fetch(url, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    .then(res => res.blob())
    .then(blob => {
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = `interview_report_${sessionId}.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    });
  };

  const report = sessionReports && sessionReports.length > 0 ? sessionReports[0].data : null;
  const reportId = sessionReports && sessionReports.length > 0 ? sessionReports[0].id : null;
  
  const timeline = report?.timeline || [];
  
  // Calculate total duration from timeline
  const totalDurationMs = useMemo(() => {
    if (!timeline.length) return 1200000; // Default 20 mins
    // Support either time (seconds) or timestamp_ms
    const max = Math.max(...timeline.map((e: any) => e.timestamp_ms || (e.time * 1000) || 0));
    return max > 0 ? max : 1200000;
  }, [timeline]);

  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTimeMs, setCurrentTimeMs] = useState(0);
  const [playbackRate, setPlaybackRate] = useState(1);
  const [exportOpen, setExportOpen] = useState(false);

  // Scrubber sync logic
  useEffect(() => {
    let animationFrame: number;
    let lastTime = performance.now();

    const updatePlay = (time: number) => {
      if (!isPlaying) return;
      const dt = time - lastTime;
      lastTime = time;
      
      setCurrentTimeMs(prev => {
        const next = prev + (dt * playbackRate);
        if (next >= totalDurationMs) {
          setIsPlaying(false);
          return totalDurationMs;
        }
        return next;
      });
      
      animationFrame = requestAnimationFrame(updatePlay);
    };

    if (isPlaying) {
      lastTime = performance.now();
      animationFrame = requestAnimationFrame(updatePlay);
    }

    return () => {
      if (animationFrame) cancelAnimationFrame(animationFrame);
    };
  }, [isPlaying, playbackRate, totalDurationMs]);

  const formatTime = (ms: number) => {
    const totalSeconds = Math.floor(ms / 1000);
    const m = Math.floor(totalSeconds / 60);
    const s = totalSeconds % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  const handleScrub = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCurrentTimeMs(Number(e.target.value));
  };

  // Derive current state from scrubber
  const currentEvents = useMemo(() => {
    // Return all events up to current time
    return timeline.filter((e: any) => {
      const eventTimeMs = e.timestamp_ms || (e.time * 1000) || 0;
      return eventTimeMs <= currentTimeMs;
    });
  }, [timeline, currentTimeMs]);

  // Find active data elements
  const activeQuestion = currentEvents.filter((e: any) => e.type === 'question_delivered').pop();
  const activeCoaching = currentEvents.filter((e: any) => e.type === 'coaching_hint').pop();
  const activeIntegrity = currentEvents.filter((e: any) => 
    ['tab_switch', 'window_blur', 'multiple_faces'].includes(e.type)
  ).pop();
  
  // Create a synthetic transcript from strong answers/observations
  const recentTranscriptEvents = currentEvents.filter((e: any) => 
    e.type === 'strong_answer' || e.type === 'observation' || e.type === 'answer'
  ).slice(-3);

  // Interpolate scores based on events (synthetic logic for UX demo)
  const currentTechScore = report?.radar_data?.technical || report?.communication_score * 100 || 80;
  const currentCommScore = report?.radar_data?.communication || report?.communication_score * 100 || 75;
  const currentConfidence = report?.radar_data?.confidence || report?.presence_score * 100 || 70;

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col">
      <Header />

      <div className="flex-1 w-full py-8 px-4 lg:px-8 max-w-[120rem] mx-auto flex flex-col">
        
        {/* Top Bar */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
          <div className="flex items-center gap-4">
            <Link to="/dashboard" className="text-slate-400 hover:text-white transition-colors">
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <div>
              <h1 className="font-heading text-2xl font-bold">{report?.title || "Interview Session"} Playback</h1>
              <p className="text-sm text-slate-400">ID: {sessionId}</p>
            </div>
          </div>
          
          <div className="flex items-center gap-3 relative">
            <Button variant="outline" className="border-slate-700 bg-slate-800 text-slate-200 hover:bg-slate-700 hover:text-white">
              <Share2 className="w-4 h-4 mr-2" /> Share
            </Button>
            
            <div className="relative">
              <Button 
                variant="default" 
                className="bg-primary text-primary-foreground hover:bg-primary/90"
                onClick={() => setExportOpen(!exportOpen)}
              >
                <Download className="w-4 h-4 mr-2" /> Export <ChevronDown className="w-4 h-4 ml-2" />
              </Button>
              {exportOpen && (
                <div className="absolute right-0 top-full mt-2 w-48 bg-slate-800 border border-slate-700 rounded-md shadow-xl overflow-hidden z-50">
                  <button onClick={() => {handleExport('pdf'); setExportOpen(false)}} className="w-full text-left px-4 py-2 hover:bg-slate-700 text-sm">Download PDF</button>
                  <button onClick={() => {handleExport('json'); setExportOpen(false)}} className="w-full text-left px-4 py-2 hover:bg-slate-700 text-sm">Export JSON</button>
                  <button onClick={() => {handleExport('markdown'); setExportOpen(false)}} className="w-full text-left px-4 py-2 hover:bg-slate-700 text-sm">Export Markdown</button>
                  <button onClick={() => {handleExport('csv'); setExportOpen(false)}} className="w-full text-left px-4 py-2 hover:bg-slate-700 text-sm">Export CSV</button>
                </div>
              )}
            </div>
          </div>
        </div>

        {isLoading ? (
          <div className="flex-1 flex justify-center items-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
          </div>
        ) : (
          <div className="flex-1 grid lg:grid-cols-12 gap-6">
            
            {/* Main Playback Area (Left) */}
            <div className="lg:col-span-8 flex flex-col gap-6">
              
              {/* Video Mock/Placeholder */}
              <div className="bg-black border border-slate-800 rounded-xl aspect-video relative overflow-hidden shadow-2xl flex items-center justify-center group">
                <Video className="w-16 h-16 text-slate-700 opacity-30" />
                
                {/* Active Question Overlay */}
                {activeQuestion && (
                  <div className="absolute top-4 left-4 right-4 bg-black/60 backdrop-blur-md border border-white/10 rounded-lg p-4 transition-all">
                    <p className="text-xs text-primary font-bold uppercase tracking-wider mb-1">Current Question</p>
                    <p className="text-lg font-semibold">{activeQuestion.details || activeQuestion.description || "Question details unavailable"}</p>
                  </div>
                )}

                {/* Scrubber Controls */}
                <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/90 via-black/60 to-transparent pt-12 pb-4 px-6 opacity-0 group-hover:opacity-100 transition-opacity">
                  <div className="flex items-center gap-4 mb-2">
                    <button onClick={() => setIsPlaying(!isPlaying)} className="w-10 h-10 rounded-full bg-primary flex items-center justify-center text-white hover:bg-primary/90 transition-transform hover:scale-105">
                      {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5 ml-1" />}
                    </button>
                    
                    <div className="text-sm font-mono text-slate-300 w-16">{formatTime(currentTimeMs)}</div>
                    
                    <input 
                      type="range" 
                      min="0" 
                      max={totalDurationMs} 
                      value={currentTimeMs} 
                      onChange={handleScrub}
                      className="flex-1 h-1.5 appearance-none bg-slate-600 rounded-full outline-none [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:bg-primary [&::-webkit-slider-thumb]:rounded-full cursor-pointer hover:[&::-webkit-slider-thumb]:scale-125 transition-all"
                    />
                    
                    <div className="text-sm font-mono text-slate-300 w-16 text-right">{formatTime(totalDurationMs)}</div>
                    
                    <button onClick={() => setPlaybackRate(r => r === 1 ? 1.5 : r === 1.5 ? 2 : 1)} className="text-xs font-bold bg-white/10 hover:bg-white/20 px-2 py-1 rounded">
                      {playbackRate}x
                    </button>
                  </div>
                </div>
              </div>

              {/* Dynamic Transcript Area */}
              <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 flex-1 min-h-[200px] overflow-hidden relative">
                <h3 className="font-heading text-sm font-bold text-slate-400 mb-4 flex items-center gap-2 uppercase tracking-wider">
                  <MessageSquare className="w-4 h-4" /> Live Transcript
                </h3>
                
                <div className="space-y-4 max-h-[300px] overflow-y-auto pr-4 scrollbar-thin scrollbar-thumb-slate-700">
                  {recentTranscriptEvents.length > 0 ? (
                    recentTranscriptEvents.map((ev: any, i: number) => (
                      <motion.div 
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        key={`${ev.timestamp_ms}-${i}`} 
                        className={`p-3 rounded-lg border-l-2 ${ev.type === 'strong_answer' ? 'bg-emerald-500/10 border-emerald-500' : 'bg-blue-500/10 border-blue-500'}`}
                      >
                        <div className="flex justify-between items-start mb-1">
                          <span className="text-xs text-slate-400 font-mono">{formatTime(ev.timestamp_ms || ev.time*1000 || 0)}</span>
                          {ev.details?.includes('Score') && <span className="text-xs font-bold text-emerald-400">{ev.details}</span>}
                        </div>
                        <p className="text-slate-200 text-sm leading-relaxed">{ev.description || "Candidate provided an answer."}</p>
                      </motion.div>
                    ))
                  ) : (
                    <div className="text-slate-500 italic text-sm py-8 text-center">Transcript waiting for input...</div>
                  )}
                </div>
              </div>

            </div>

            {/* Sidebar Data (Right) */}
            <div className="lg:col-span-4 flex flex-col gap-6">
              
              {/* Telemetry / Live Scores */}
              <div className="bg-slate-800/80 border border-slate-700 rounded-xl p-6">
                <h3 className="font-heading text-sm font-bold text-slate-400 mb-6 flex items-center gap-2 uppercase tracking-wider">
                  <Activity className="w-4 h-4" /> Live Telemetry
                </h3>
                
                <div className="space-y-6">
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-slate-300">Technical Scope</span>
                      <span className="font-mono text-emerald-400">{currentTechScore.toFixed(0)}</span>
                    </div>
                    <div className="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden border border-slate-800">
                      <div className="bg-emerald-500 h-full rounded-full transition-all duration-300" style={{ width: `${currentTechScore}%` }}></div>
                    </div>
                  </div>
                  
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-slate-300">Communication</span>
                      <span className="font-mono text-blue-400">{currentCommScore.toFixed(0)}</span>
                    </div>
                    <div className="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden border border-slate-800">
                      <div className="bg-blue-500 h-full rounded-full transition-all duration-300" style={{ width: `${currentCommScore}%` }}></div>
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-slate-300">Confidence</span>
                      <span className="font-mono text-purple-400">{currentConfidence.toFixed(0)}</span>
                    </div>
                    <div className="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden border border-slate-800">
                      <div className="bg-purple-500 h-full rounded-full transition-all duration-300" style={{ width: `${currentConfidence}%` }}></div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Integrity Alerts */}
              <div className="bg-slate-800/80 border border-slate-700 rounded-xl p-6">
                <h3 className="font-heading text-sm font-bold text-slate-400 mb-4 flex items-center gap-2 uppercase tracking-wider">
                  <ShieldAlert className="w-4 h-4" /> Integrity Events
                </h3>
                
                <div className="min-h-[80px]">
                  {activeIntegrity ? (
                    <motion.div 
                      key={activeIntegrity.timestamp_ms}
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      className="bg-red-500/10 border border-red-500/30 rounded-lg p-3"
                    >
                      <div className="flex items-center gap-2 text-red-400 font-bold text-sm mb-1">
                        <ShieldAlert className="w-4 h-4" /> {activeIntegrity.description || "Alert"}
                      </div>
                      <p className="text-xs text-red-300/80">{activeIntegrity.details || "Detected integrity concern."}</p>
                    </motion.div>
                  ) : (
                    <div className="h-full flex items-center justify-center border border-dashed border-slate-700 rounded-lg">
                      <span className="text-emerald-500/70 text-xs font-semibold flex items-center gap-2">
                        <CheckCircle2 className="w-3 h-3" /> No recent alerts
                      </span>
                    </div>
                  )}
                </div>
              </div>

              {/* Coaching Hints */}
              <div className="bg-primary/10 border border-primary/20 rounded-xl p-6 flex-1">
                <h3 className="font-heading text-sm font-bold text-primary/80 mb-4 flex items-center gap-2 uppercase tracking-wider">
                  <BrainCircuit className="w-4 h-4" /> Coaching Engine
                </h3>
                
                <div className="min-h-[100px]">
                  {activeCoaching ? (
                    <motion.div 
                      key={activeCoaching.timestamp_ms}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="bg-primary/20 rounded-lg p-4"
                    >
                      <p className="text-primary-foreground text-sm font-medium leading-relaxed">
                        "{activeCoaching.description || activeCoaching.details}"
                      </p>
                    </motion.div>
                  ) : (
                    <div className="text-primary/50 italic text-sm text-center py-6">
                      AI is analyzing candidate responses...
                    </div>
                  )}
                </div>
              </div>

            </div>
          </div>
        )}
      </div>

    </div>
  );
}
