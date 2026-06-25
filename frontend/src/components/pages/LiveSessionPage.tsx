/**
 * LiveSessionPage Component
 * 
 * Premium live interview practice session page with:
 * - Real-time webcam video feed
 * - Behavioral analysis sidebar (confidence, nervousness, emotions)
 * - Session controls and interview question prompts
 * - AI-powered question generation using Gemini
 */
import { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import {
    Video,
    VideoOff,
    Mic,
    MicOff,
    Play,
    Square,
    Save,
    ArrowLeft,
    AlertCircle,
    Wifi,
    WifiOff,
    Eye,
    Brain,
    Activity,
    Sparkles,
    RefreshCw,
    Clock,
    MessageSquare,
    Loader2,
    Volume2,
    FileText,
    AlertTriangle,
    Languages,
    CheckCircle2,
    ShieldCheck
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import FaceTrackingOverlay from '@/components/FaceTrackingOverlay';
import GazeDirectionPanel from '@/components/GazeDirectionPanel';
import EnvironmentWarningPanel from '@/components/EnvironmentWarningPanel';
import SpeechRatePanel from '@/components/SpeechRatePanel';
import { useBehavioralAnalysis, BehavioralMetrics } from '@/hooks/useBehavioralAnalysis';
import { BaseCrudService } from '@/integrations';
import { PracticeSessions } from '@/entities';
import { generateSingleQuestion } from '@/services/geminiService';
import useSpeechAnalysis from '@/hooks/useSpeechAnalysis';

// Emotion labels with colors
const EMOTION_COLORS: Record<string, string> = {
    happy: 'bg-green-500',
    neutral: 'bg-blue-500',
    surprise: 'bg-yellow-500',
    fear: 'bg-orange-500',
    sad: 'bg-indigo-500',
    angry: 'bg-red-500',
    disgust: 'bg-purple-500'
};

export default function LiveSessionPage() {
    const navigate = useNavigate();
    const videoRef = useRef<HTMLVideoElement>(null);
    const streamRef = useRef<MediaStream | null>(null);

    // Session state
    const [isSessionActive, setIsSessionActive] = useState(false);
    const [isPracticing, setIsPracticing] = useState(false);
    const [cameraEnabled, setCameraEnabled] = useState(false);
    const [micEnabled, setMicEnabled] = useState(true);
    const [sessionDuration, setSessionDuration] = useState(0);
    const [cameraError, setCameraError] = useState<string | null>(null);
    const [sessionType, setSessionType] = useState<string>('Behavioral');
    const sessionStartTimeRef = useRef<Date | null>(null);
    const [hasConsented, setHasConsented] = useState(false);

    // Video dimensions for face tracking overlay
    const [videoDimensions, setVideoDimensions] = useState({ width: 1280, height: 720 });

    // Question generation state - unlimited questions
    const [currentQuestion, setCurrentQuestion] = useState<string>('');
    const [questionHistory, setQuestionHistory] = useState<string[]>([]);
    const [questionNumber, setQuestionNumber] = useState(0);
    const [isLoadingQuestion, setIsLoadingQuestion] = useState(true);
    const [questionError, setQuestionError] = useState<string | null>(null);

    // Behavioral analysis hook
    const {
        metrics,
        isConnected,
        isAnalyzing,
        error: analysisError,
        startAnalysis,
        stopAnalysis,
        resetSession
    } = useBehavioralAnalysis({
        fps: 4 // 4 FPS for smooth analysis without overwhelming the backend
    });

    // Speech analysis hook
    const {
        metrics: speechMetrics,
        transcriptionHistory,
        isConnected: speechConnected,
        isAnalyzing: speechAnalyzing,
        error: speechError,
        startAnalysis: startSpeechAnalysis,
        stopAnalysis: stopSpeechAnalysis,
        resetSession: resetSpeechSession
    } = useSpeechAnalysis({
        chunkIntervalMs: 3000 // Send audio every 3 seconds
    });

    // Session timer
    useEffect(() => {
        let interval: number | null = null;
        if (isPracticing) {
            interval = window.setInterval(() => {
                setSessionDuration(d => d + 1);
            }, 1000);
        }
        return () => {
            if (interval) clearInterval(interval);
        };
    }, [isPracticing]);

    // Fetch a single new question from AI
    const fetchNewQuestion = useCallback(async (resetHistory: boolean = false) => {
        setIsLoadingQuestion(true);
        setQuestionError(null);
        try {
            const history = resetHistory ? [] : questionHistory;
            const result = await generateSingleQuestion(sessionType, history);
            setCurrentQuestion(result.question);
            setQuestionHistory(prev => resetHistory ? [result.question] : [...prev, result.question]);
            setQuestionNumber(prev => resetHistory ? 1 : prev + 1);
            console.log('[LiveSessionPage] New question generated, source:', result.source);
        } catch (error) {
            console.error('[LiveSessionPage] Error fetching question:', error);
            setQuestionError('Failed to generate question. Please retry.');
        } finally {
            setIsLoadingQuestion(false);
        }
    }, [sessionType, questionHistory]);

    // Fetch first question on mount and when session type changes
    useEffect(() => {
        fetchNewQuestion(true); // Reset history when session type changes
    }, [sessionType]);

    // Format duration as MM:SS
    const formatDuration = (seconds: number): string => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    };

    // Initialize camera
    const initCamera = useCallback(async () => {
        try {
            setCameraError(null);
            const stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 1280 },
                    height: { ideal: 720 },
                    facingMode: 'user'
                },
                audio: true
            });

            if (videoRef.current) {
                videoRef.current.srcObject = stream;
                streamRef.current = stream;
                setCameraEnabled(true);
            }
        } catch (err) {
            console.error('Camera error:', err);
            setCameraError('Unable to access camera. Please check permissions.');
        }
    }, []);

    // Stop camera
    const stopCamera = useCallback(() => {
        if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop());
            streamRef.current = null;
        }
        if (videoRef.current) {
            videoRef.current.srcObject = null;
        }
        setCameraEnabled(false);
    }, []);

    // Start practice session
    const startSession = useCallback(async () => {
        await initCamera();
        setIsSessionActive(true);
        setSessionDuration(0);
        sessionStartTimeRef.current = new Date();
        resetSession();
        resetSpeechSession();
    }, [initCamera, resetSession, resetSpeechSession]);

    // Start practicing (recording with analysis)
    const startPractice = useCallback(() => {
        if (videoRef.current && cameraEnabled) {
            startAnalysis(videoRef.current);
            startSpeechAnalysis();
            setIsPracticing(true);
        }
    }, [cameraEnabled, startAnalysis, startSpeechAnalysis]);

    // Stop practicing
    const stopPractice = useCallback(() => {
        stopAnalysis();
        stopSpeechAnalysis();
        setIsPracticing(false);
    }, [stopAnalysis, stopSpeechAnalysis]);

    // End session completely and save to localStorage
    const endSession = useCallback(async () => {
        stopPractice();
        stopCamera();

        // Calculate overall readiness score from metrics
        const overallScore = metrics
            ? Math.round((metrics.confidence_score * 100 + (1 - metrics.nervousness_score) * 100) / 2)
            : 0;

        // Save session to localStorage
        try {
            await BaseCrudService.create<PracticeSessions>('practicesessions', {
                sessionDateTime: sessionStartTimeRef.current || new Date(),
                sessionType: sessionType,
                overallReadinessScore: overallScore,
                verbalAnalysisSummary: `Session duration: ${Math.floor(sessionDuration / 60)}m ${sessionDuration % 60}s`,
                nonVerbalAnalysisSummary: metrics
                    ? `Confidence: ${Math.round(metrics.confidence_score * 100)}%, Nervousness: ${Math.round(metrics.nervousness_score * 100)}%`
                    : 'No behavioral analysis data',
                feedbackSummary: metrics?.behavioral_tag || 'Session completed',
            });
            console.log('[LiveSessionPage] Session saved successfully');
        } catch (error) {
            console.error('[LiveSessionPage] Failed to save session:', error);
        }

        setIsSessionActive(false);
        navigate('/practice');
    }, [stopPractice, stopCamera, navigate, sessionType, sessionDuration, metrics]);

    // Toggle microphone
    const toggleMic = useCallback(() => {
        if (streamRef.current) {
            const audioTracks = streamRef.current.getAudioTracks();
            audioTracks.forEach(track => {
                track.enabled = !track.enabled;
            });
            setMicEnabled(prev => !prev);
        }
    }, []);

    // Next question - generates a fresh AI question
    const nextQuestion = useCallback(() => {
        fetchNewQuestion(false);
    }, [fetchNewQuestion]);

    // Cleanup on unmount
    // Cleanup on unmount
    useEffect(() => {
        return () => {
            stopCamera();
            stopAnalysis();
            stopSpeechAnalysis();
        };
    }, [stopCamera, stopAnalysis, stopSpeechAnalysis]);

    // Get behavioral tag color
    const getBehavioralTagColor = (tag: string): string => {
        switch (tag) {
            case 'CONFIDENT': return 'bg-green-500 text-white';
            case 'NERVOUS': return 'bg-orange-500 text-white';
            case 'NO_FACE': return 'bg-gray-500 text-white';
            default: return 'bg-blue-500 text-white';
        }
    };

    // Get score color class
    const getScoreColor = (score: number, isNervousness: boolean = false): string => {
        if (isNervousness) {
            if (score < 0.3) return 'from-green-500 to-green-400';
            if (score < 0.6) return 'from-yellow-500 to-yellow-400';
            return 'from-red-500 to-red-400';
        }
        if (score > 0.6) return 'from-green-500 to-green-400';
        if (score > 0.4) return 'from-yellow-500 to-yellow-400';
        return 'from-red-500 to-red-400';
    };

    return (
        <div className="min-h-screen bg-background text-foreground">
            <Header />

            <main className="relative w-full max-w-[120rem] mx-auto py-8 px-4 lg:px-8">
                {/* Back button */}
                <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="mb-6"
                >
                    <Button
                        variant="ghost"
                        onClick={() => navigate('/practice')}
                        className="text-foreground/70 hover:text-foreground"
                    >
                        <ArrowLeft className="w-4 h-4 mr-2" />
                        Back to Sessions
                    </Button>
                </motion.div>

                {!hasConsented ? (
                    <motion.div 
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="max-w-2xl mx-auto bg-gradient-to-br from-background to-gradient-start/10 border border-primary/30 rounded-xl p-8 text-center"
                    >
                        <div className="w-16 h-16 bg-primary/20 rounded-full flex items-center justify-center mx-auto mb-6">
                            <ShieldCheck className="w-8 h-8 text-primary" />
                        </div>
                        <h2 className="text-2xl font-bold font-heading mb-4 text-foreground">Privacy & Consent</h2>
                        <p className="text-foreground/80 mb-6 leading-relaxed">
                            To provide you with personalized, AI-driven coaching, this interview platform records and analyzes your session. 
                            By continuing, you agree to the processing of the following data:
                        </p>
                        
                        <div className="grid grid-cols-2 gap-4 text-left mb-8 max-w-md mx-auto">
                            <div className="flex items-center gap-3 p-3 bg-foreground/5 rounded-lg border border-foreground/10">
                                <Mic className="w-5 h-5 text-blue-400" />
                                <span>Audio & Speech</span>
                            </div>
                            <div className="flex items-center gap-3 p-3 bg-foreground/5 rounded-lg border border-foreground/10">
                                <Video className="w-5 h-5 text-emerald-400" />
                                <span>Video & Face</span>
                            </div>
                            <div className="flex items-center gap-3 p-3 bg-foreground/5 rounded-lg border border-foreground/10">
                                <Eye className="w-5 h-5 text-purple-400" />
                                <span>Eye Contact</span>
                            </div>
                            <div className="flex items-center gap-3 p-3 bg-foreground/5 rounded-lg border border-foreground/10">
                                <Brain className="w-5 h-5 text-orange-400" />
                                <span>Interview Responses</span>
                            </div>
                        </div>
                        
                        <p className="text-sm text-foreground/60 mb-8 italic">
                            Your recordings are processed securely to generate your interview feedback. You can delete your recordings and reports at any time from your Profile settings.
                        </p>
                        
                        <div className="flex gap-4 justify-center">
                            <Button 
                                variant="outline" 
                                onClick={() => navigate('/practice')}
                                className="px-8"
                            >
                                Cancel
                            </Button>
                            <Button 
                                onClick={() => setHasConsented(true)}
                                className="px-8 bg-primary hover:bg-primary/90 text-primary-foreground font-semibold"
                            >
                                I Consent, Continue
                            </Button>
                        </div>
                    </motion.div>
                ) : (
                    <div className="grid lg:grid-cols-3 gap-6">
                    {/* Video area - 2 columns */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: 0.1 }}
                        className="lg:col-span-2"
                    >
                        {/* Question prompt card - Compact design ABOVE camera */}
                        <motion.div
                            initial={{ opacity: 0, y: -10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.1 }}
                            className="mb-4 bg-gradient-to-r from-primary/10 to-secondary/10 border border-primary/30 rounded-xl p-3"
                        >
                            {isLoadingQuestion ? (
                                <div className="flex items-center justify-center gap-2 py-2">
                                    <Loader2 className="w-5 h-5 text-primary animate-spin" />
                                    <span className="text-foreground/70 text-sm">Generating AI question...</span>
                                </div>
                            ) : questionError ? (
                                <div className="flex items-center justify-center gap-2 py-2">
                                    <AlertCircle className="w-4 h-4 text-yellow-500" />
                                    <span className="text-foreground/70 text-sm">{questionError}</span>
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        onClick={() => fetchNewQuestion(false)}
                                        className="ml-2 border-primary text-primary hover:bg-primary/10 h-7 text-xs"
                                    >
                                        <RefreshCw className="w-3 h-3 mr-1" />
                                        Retry
                                    </Button>
                                </div>
                            ) : (
                                <div className="flex items-center justify-between gap-3">
                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center gap-2 mb-1">
                                            <MessageSquare className="w-4 h-4 text-primary shrink-0" />
                                            <span className="text-xs font-medium text-foreground/70">
                                                Q#{questionNumber}
                                            </span>
                                            <span className="px-1.5 py-0.5 bg-primary/20 text-primary text-xs rounded">
                                                {sessionType}
                                            </span>
                                            <span className="px-1.5 py-0.5 bg-green-500/20 text-green-500 text-xs rounded">
                                                ∞
                                            </span>
                                        </div>
                                        <p className="font-heading text-base lg:text-lg font-semibold text-foreground line-clamp-2" title={currentQuestion}>
                                            "{currentQuestion || 'Click Next to generate a question'}"
                                        </p>
                                    </div>
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        onClick={nextQuestion}
                                        className="border-primary text-primary hover:bg-primary/10 shrink-0 h-9"
                                        disabled={isLoadingQuestion}
                                    >
                                        {isLoadingQuestion ? (
                                            <Loader2 className="w-4 h-4 mr-1 animate-spin" />
                                        ) : (
                                            <Sparkles className="w-4 h-4 mr-1" />
                                        )}
                                        Next
                                    </Button>
                                </div>
                            )}
                        </motion.div>

                        {/* Video container */}
                        <div className="bg-gradient-to-br from-background to-gradient-start/10 border border-primary/30 rounded-2xl overflow-hidden">
                            {/* Video element */}
                            <div className="relative aspect-video bg-black/50">
                                <video
                                    ref={videoRef}
                                    autoPlay
                                    muted
                                    playsInline
                                    className="w-full h-full object-cover mirror"
                                    style={{ transform: 'scaleX(-1)' }}
                                    onLoadedMetadata={() => {
                                        if (videoRef.current) {
                                            setVideoDimensions({
                                                width: videoRef.current.videoWidth || 1280,
                                                height: videoRef.current.videoHeight || 720
                                            });
                                        }
                                    }}
                                />

                                {/* Face Tracking Overlay */}
                                {cameraEnabled && isAnalyzing && (
                                    <FaceTrackingOverlay
                                        metrics={metrics}
                                        videoWidth={videoDimensions.width}
                                        videoHeight={videoDimensions.height}
                                    />
                                )}

                                {/* Overlay when camera not active */}
                                {!cameraEnabled && (
                                    <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/80">
                                        <Video className="w-16 h-16 text-primary/50 mb-4" />
                                        <p className="text-foreground/70 font-paragraph mb-4">
                                            {cameraError || 'Select session type and start camera'}
                                        </p>

                                        {/* Session Type Selector */}
                                        <div className="flex items-center gap-2 mb-6">
                                            <span className="text-foreground/60 text-sm mr-2">Session Type:</span>
                                            {['Behavioral', 'Technical', 'HR'].map((type) => (
                                                <button
                                                    key={type}
                                                    onClick={() => setSessionType(type)}
                                                    className={`px-4 py-2 rounded text-sm font-medium transition-all duration-300 ${sessionType === type
                                                        ? 'bg-primary text-primary-foreground'
                                                        : 'bg-primary/20 text-foreground/70 hover:bg-primary/30'
                                                        }`}
                                                >
                                                    {type}
                                                </button>
                                            ))}
                                        </div>

                                        <Button
                                            onClick={startSession}
                                            className="bg-primary text-primary-foreground hover:bg-primary/90"
                                        >
                                            <Video className="w-4 h-4 mr-2" />
                                            Start Camera
                                        </Button>
                                    </div>
                                )}

                                {/* Face detection indicator */}
                                {isAnalyzing && metrics && (
                                    <div className="absolute top-4 left-4 flex items-center gap-2">
                                        <div className={`px-3 py-1.5 rounded-full text-xs font-semibold ${getBehavioralTagColor(metrics.behavioral_tag)}`}>
                                            {metrics.behavioral_tag}
                                        </div>
                                        {!metrics.face_detected && (
                                            <div className="px-3 py-1.5 bg-red-500/20 text-red-400 rounded-full text-xs font-semibold flex items-center gap-1">
                                                <AlertCircle className="w-3 h-3" />
                                                Face not detected
                                            </div>
                                        )}
                                    </div>
                                )}

                                {/* Session timer */}
                                {isSessionActive && (
                                    <div className="absolute top-4 right-4 flex items-center gap-2 px-3 py-1.5 bg-black/60 backdrop-blur-sm rounded-full text-white text-sm">
                                        <Clock className="w-4 h-4 text-primary" />
                                        {formatDuration(sessionDuration)}
                                        {isPracticing && (
                                            <span className="flex items-center gap-1 ml-2">
                                                <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                                                Recording
                                            </span>
                                        )}
                                    </div>
                                )}

                                {/* Connection status */}
                                <div className="absolute bottom-4 left-4 flex items-center gap-2">
                                    <div className={`px-3 py-1.5 rounded-full text-xs font-medium flex items-center gap-1 ${isConnected ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'}`}>
                                        {isConnected ? <Wifi className="w-3 h-3" /> : <WifiOff className="w-3 h-3" />}
                                        {isConnected ? 'Connected' : 'Disconnected'}
                                    </div>
                                </div>
                            </div>

                            {/* Controls */}
                            <div className="p-4 bg-black/20 border-t border-primary/20">
                                <div className="flex items-center justify-center gap-4">
                                    {/* Camera toggle */}
                                    <Button
                                        variant="outline"
                                        size="icon"
                                        onClick={cameraEnabled ? stopCamera : initCamera}
                                        className={`rounded-full w-12 h-12 ${cameraEnabled ? 'border-primary text-primary' : 'border-destructive text-destructive'}`}
                                    >
                                        {cameraEnabled ? <Video className="w-5 h-5" /> : <VideoOff className="w-5 h-5" />}
                                    </Button>

                                    {/* Mic toggle */}
                                    <Button
                                        variant="outline"
                                        size="icon"
                                        onClick={toggleMic}
                                        className={`rounded-full w-12 h-12 ${micEnabled ? 'border-primary text-primary' : 'border-destructive text-destructive'}`}
                                    >
                                        {micEnabled ? <Mic className="w-5 h-5" /> : <MicOff className="w-5 h-5" />}
                                    </Button>

                                    {/* Start/Stop Practice */}
                                    {cameraEnabled && (
                                        <Button
                                            onClick={isPracticing ? stopPractice : startPractice}
                                            className={`rounded-full px-8 py-6 text-lg font-semibold ${isPracticing
                                                ? 'bg-destructive hover:bg-destructive/90'
                                                : 'bg-primary hover:bg-primary/90'
                                                }`}
                                        >
                                            {isPracticing ? (
                                                <>
                                                    <Square className="w-5 h-5 mr-2" />
                                                    Stop Practice
                                                </>
                                            ) : (
                                                <>
                                                    <Play className="w-5 h-5 mr-2" />
                                                    Start Practice
                                                </>
                                            )}
                                        </Button>
                                    )}

                                    {/* Save/End button */}
                                    {isSessionActive && (
                                        <Button
                                            variant="outline"
                                            onClick={endSession}
                                            className="rounded-full border-2 border-secondary text-secondary hover:bg-secondary/10"
                                        >
                                            <Save className="w-4 h-4 mr-2" />
                                            End Session
                                        </Button>
                                    )}
                                </div>
                            </div>
                        </div>
                    </motion.div>

                    {/* Behavioral Analysis Sidebar */}
                    <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.2 }}
                        className="space-y-4"
                    >
                        {/* Analysis Header */}
                        <div className="bg-gradient-to-br from-background to-gradient-start/10 border border-primary/30 rounded-xl p-4">
                            <div className="flex items-center gap-3 mb-4">
                                <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center">
                                    <Brain className="w-5 h-5 text-primary" />
                                </div>
                                <div>
                                    <h3 className="font-heading font-bold text-foreground">Behavioral Analysis</h3>
                                    <p className="text-xs text-foreground/60">Real-time AI feedback</p>
                                </div>
                            </div>

                            {/* Error display */}
                            {analysisError && (
                                <div className="mb-4 p-3 bg-destructive/20 border border-destructive/30 rounded-lg text-sm text-destructive flex items-center gap-2">
                                    <AlertCircle className="w-4 h-4" />
                                    {analysisError}
                                </div>
                            )}

                            {/* Status indicator */}
                            <div className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm ${isAnalyzing
                                ? 'bg-green-500/20 text-green-400'
                                : 'bg-foreground/10 text-foreground/60'
                                }`}>
                                <Activity className={`w-4 h-4 ${isAnalyzing ? 'animate-pulse' : ''}`} />
                                {isAnalyzing ? 'Analyzing...' : 'Waiting to start'}
                            </div>
                        </div>

                        {/* Gaze Direction Panel */}
                        <GazeDirectionPanel
                            metrics={metrics}
                            isAnalyzing={isAnalyzing}
                        />

                        {/* Environment Warning Panel */}
                        <EnvironmentWarningPanel
                            metrics={metrics}
                            isAnalyzing={isAnalyzing}
                        />

                        {/* Speech Rate Panel */}
                        <SpeechRatePanel
                            metrics={speechMetrics}
                            isAnalyzing={speechAnalyzing}
                        />

                        {/* Speech Analysis Panel */}
                        <div className="bg-gradient-to-br from-background to-gradient-start/10 border border-primary/30 rounded-xl p-4">
                            <div className="flex items-center gap-3 mb-4">
                                <div className="w-10 h-10 rounded-full bg-blue-500/20 flex items-center justify-center">
                                    <Volume2 className="w-5 h-5 text-blue-400" />
                                </div>
                                <div>
                                    <h3 className="font-heading font-bold text-foreground">Speech Analysis</h3>
                                    <p className="text-xs text-foreground/60">Transcription & Emotions</p>
                                </div>
                            </div>

                            {/* Connection Status */}
                            <div className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm mb-4 ${speechConnected
                                ? 'bg-green-500/10 text-green-400'
                                : 'bg-yellow-500/10 text-yellow-500'
                                }`}>
                                {speechConnected ? <Wifi className="w-4 h-4" /> : <WifiOff className="w-4 h-4" />}
                                {speechConnected ? 'Speech Service Connected' : 'Connecting to Speech Service...'}
                            </div>

                            {/* Speech Error */}
                            {speechError && (
                                <div className="mb-4 p-2 bg-destructive/20 text-destructive text-xs rounded border border-destructive/30 flex items-center gap-2">
                                    <AlertTriangle className="w-3 h-3" />
                                    {speechError}
                                </div>
                            )}

                            {/* Live Transcription */}
                            <div className="mb-4">
                                <div className="flex items-center justify-between mb-2">
                                    <span className="text-sm font-medium text-foreground flex items-center gap-2">
                                        <FileText className="w-3 h-3 text-primary" />
                                        Live Transcript
                                    </span>
                                    {speechAnalyzing && <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />}
                                </div>
                                <div className="h-32 p-3 bg-black/20 rounded-lg border border-primary/10 overflow-y-auto text-sm text-foreground/80 font-mono leading-relaxed">
                                    {transcriptionHistory.length > 0 ? (
                                        transcriptionHistory.map((text, i) => (
                                            <p key={i} className="mb-2 last:mb-0 last:text-primary">{text}</p>
                                        ))
                                    ) : (
                                        <span className="text-foreground/40 italic">Start speaking to see transcription...</span>
                                    )}
                                </div>
                            </div>

                            {/* Speech Emotions */}
                            <div className="mb-4">
                                <span className="text-sm font-medium text-foreground flex items-center gap-2 mb-2">
                                    <Languages className="w-3 h-3 text-purple-400" />
                                    Vocal Emotion
                                </span>
                                {speechMetrics?.emotions && speechMetrics.emotions.length > 0 ? (
                                    <div className="space-y-1.5">
                                        {speechMetrics.emotions.slice(0, 3).map((e: any) => (
                                            <div key={e.label} className="flex items-center gap-2 text-xs">
                                                <span className="w-16 capitalize text-foreground/70">{e.label}</span>
                                                <div className="flex-1 h-1.5 bg-foreground/10 rounded-full overflow-hidden">
                                                    <div
                                                        className="h-full bg-purple-500 rounded-full transition-all duration-500"
                                                        style={{ width: `${e.score * 100}%` }}
                                                    />
                                                </div>
                                                <span className="w-8 text-right text-foreground/60">{Math.round(e.score * 100)}%</span>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <div className="text-xs text-foreground/40 italic">No emotion data yet</div>
                                )}
                            </div>

                            {/* Filler Words */}
                            <div className="flex items-center justify-between text-xs p-2 bg-foreground/5 rounded-lg border border-foreground/10">
                                <span className="text-foreground/70">Filler Words</span>
                                <span className={`font-mono font-bold ${(speechMetrics?.filler_count || 0) > 5 ? 'text-orange-400' : 'text-green-400'
                                    }`}>
                                    {speechMetrics?.filler_count || 0}
                                </span>
                            </div>
                        </div>

                        {/* Confidence Score */}
                        <div className="bg-gradient-to-br from-background to-gradient-start/10 border border-primary/30 rounded-xl p-4">
                            <div className="flex items-center justify-between mb-3">
                                <div className="flex items-center gap-2">
                                    <Sparkles className="w-4 h-4 text-green-400" />
                                    <span className="font-medium text-foreground">Confidence</span>
                                </div>
                                <span className="font-heading text-2xl font-bold text-foreground">
                                    {metrics ? `${Math.round(metrics.confidence_score * 100)}%` : '--'}
                                </span>
                            </div>
                            <div className="h-3 bg-foreground/10 rounded-full overflow-hidden">
                                <motion.div
                                    className={`h-full rounded-full bg-gradient-to-r ${getScoreColor(metrics?.confidence_score || 0)}`}
                                    initial={{ width: 0 }}
                                    animate={{ width: `${(metrics?.confidence_score || 0) * 100}%` }}
                                    transition={{ duration: 0.5, ease: 'easeOut' }}
                                />
                            </div>
                            <p className="text-xs text-foreground/50 mt-2">
                                {metrics?.confidence_score && metrics.confidence_score > 0.6
                                    ? 'Great job! You appear confident.'
                                    : metrics?.confidence_score && metrics.confidence_score > 0.4
                                        ? 'Good presence, keep it steady.'
                                        : 'Try to relax and project more confidence.'}
                            </p>
                        </div>

                        {/* Nervousness Score */}
                        <div className="bg-gradient-to-br from-background to-gradient-start/10 border border-primary/30 rounded-xl p-4">
                            <div className="flex items-center justify-between mb-3">
                                <div className="flex items-center gap-2">
                                    <Activity className="w-4 h-4 text-orange-400" />
                                    <span className="font-medium text-foreground">Nervousness</span>
                                </div>
                                <span className="font-heading text-2xl font-bold text-foreground">
                                    {metrics ? `${Math.round(metrics.nervousness_score * 100)}%` : '--'}
                                </span>
                            </div>
                            <div className="h-3 bg-foreground/10 rounded-full overflow-hidden">
                                <motion.div
                                    className={`h-full rounded-full bg-gradient-to-r ${getScoreColor(metrics?.nervousness_score || 0, true)}`}
                                    initial={{ width: 0 }}
                                    animate={{ width: `${(metrics?.nervousness_score || 0) * 100}%` }}
                                    transition={{ duration: 0.5, ease: 'easeOut' }}
                                />
                            </div>
                            <p className="text-xs text-foreground/50 mt-2">
                                {metrics?.nervousness_score && metrics.nervousness_score < 0.3
                                    ? 'Calm and collected - excellent!'
                                    : metrics?.nervousness_score && metrics.nervousness_score < 0.5
                                        ? 'Mild nervousness detected.'
                                        : 'Take a deep breath and relax.'}
                            </p>
                        </div>

                        {/* Emotion Breakdown */}
                        <div className="bg-gradient-to-br from-background to-gradient-start/10 border border-primary/30 rounded-xl p-4">
                            <div className="flex items-center gap-2 mb-4">
                                <Eye className="w-4 h-4 text-primary" />
                                <span className="font-medium text-foreground">Emotion Breakdown</span>
                            </div>

                            <div className="space-y-2">
                                {metrics?.emotions && Object.entries(metrics.emotions)
                                    .sort(([, a], [, b]) => (b as number) - (a as number))
                                    .slice(0, 5)
                                    .map(([emotion, score]) => (
                                        <div key={emotion} className="flex items-center gap-2">
                                            <span className="text-xs text-foreground/70 w-20 capitalize">{emotion}</span>
                                            <div className="flex-1 h-2 bg-foreground/10 rounded-full overflow-hidden">
                                                <motion.div
                                                    className={`h-full rounded-full ${EMOTION_COLORS[emotion] || 'bg-gray-500'}`}
                                                    initial={{ width: 0 }}
                                                    animate={{ width: `${(score as number) * 100}%` }}
                                                    transition={{ duration: 0.3 }}
                                                />
                                            </div>
                                            <span className="text-xs text-foreground/50 w-10 text-right">
                                                {Math.round((score as number) * 100)}%
                                            </span>
                                        </div>
                                    ))}

                                {!metrics?.emotions || Object.keys(metrics.emotions).length === 0 ? (
                                    <p className="text-sm text-foreground/50 text-center py-4">
                                        Start practicing to see emotion analysis
                                    </p>
                                ) : null}
                            </div>
                        </div>

                        {/* Tips */}
                        <div className="bg-gradient-to-br from-primary/5 to-secondary/5 border border-primary/20 rounded-xl p-4">
                            <h4 className="font-medium text-foreground mb-2">💡 Tips</h4>
                            <ul className="text-xs text-foreground/70 space-y-1">
                                <li>• Maintain eye contact with the camera</li>
                                <li>• Speak clearly at a moderate pace</li>
                                <li>• Keep a neutral or positive expression</li>
                                <li>• Avoid fidgeting or looking away</li>
                            </ul>
                        </div>
                    </motion.div>
                </div>
                )}
            </main >

            <Footer />
        </div >
    );
}
