/**
 * useSpeechAnalysis Hook
 * 
 * React hook for real-time speech analysis via WebSocket.
 * Captures audio from microphone and streams to backend for analysis.
 * 
 * Returns: transcription, grammar issues, emotions, filler word detection.
 */
import { useState, useRef, useCallback, useEffect } from 'react';

export interface GrammarIssue {
    message: string;
    offset: number;
    length: number;
    replacements: string[];
}

export interface EmotionScore {
    label: string;
    score: number;
}

export interface SpeechMetrics {
    // Transcription
    transcription: string;
    word_count: number;

    // Grammar
    grammar_issues: GrammarIssue[];
    grammar_error_count: number;

    // Emotions
    emotions: EmotionScore[];
    dominant_emotion: string;
    dominant_emotion_score: number;

    // Fillers
    filler_count: number;
    filler_words: string[];

    // Speech rate (words per minute)
    words_per_minute: number;
    speech_rate_status: 'slow' | 'optimal' | 'fast';

    // Vocal clarity
    vocal_clarity: number;  // 0-100
    clarity_feedback: string;

    // Timestamp
    timestamp: number;
}

export interface SpeechSummary {
    total_words: number;
    total_fillers: number;
    filler_rate: number;
    total_grammar_errors: number;
    dominant_emotion: string;
    full_transcription: string;
}

export interface UseSpeechAnalysisOptions {
    sessionId?: string;
    wsUrl?: string;
    chunkIntervalMs?: number; // How often to send audio chunks
}

export interface UseSpeechAnalysisReturn {
    metrics: SpeechMetrics | null;
    transcriptionHistory: string[];
    isConnected: boolean;
    isAnalyzing: boolean;
    error: string | null;
    startAnalysis: () => void;
    stopAnalysis: () => void;
    resetSession: () => void;
    getSummary: () => void;
}

const DEFAULT_WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

export function useSpeechAnalysis(
    options: UseSpeechAnalysisOptions = {}
): UseSpeechAnalysisReturn {
    const {
        sessionId = `speech_${Date.now()}`,
        wsUrl = DEFAULT_WS_URL,
        chunkIntervalMs = 3000 // Send audio every 3 seconds
    } = options;

    const [metrics, setMetrics] = useState<SpeechMetrics | null>(null);
    const [transcriptionHistory, setTranscriptionHistory] = useState<string[]>([]);
    const [isConnected, setIsConnected] = useState(false);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const wsRef = useRef<WebSocket | null>(null);
    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const audioChunksRef = useRef<Blob[]>([]);
    const streamRef = useRef<MediaStream | null>(null);
    const intervalRef = useRef<number | null>(null);

    // Convert audio blob to base64
    const blobToBase64 = useCallback((blob: Blob): Promise<string> => {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onloadend = () => {
                const result = reader.result as string;
                resolve(result);
            };
            reader.onerror = reject;
            reader.readAsDataURL(blob);
        });
    }, []);

    // Send accumulated audio chunks to backend
    const sendAudioChunk = useCallback(async () => {
        const ws = wsRef.current;
        if (!ws || ws.readyState !== WebSocket.OPEN) return;
        if (audioChunksRef.current.length === 0) return;

        try {
            // Combine all chunks into one blob (includes headers from the start)
            const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
            // Do NOT clear the array, so we keep the webm headers!
            // audioChunksRef.current = []; 

            // Convert to base64
            const base64Audio = await blobToBase64(audioBlob);

            // Send to backend
            ws.send(JSON.stringify({
                type: 'audio',
                data: base64Audio,
                timestamp: Date.now()
            }));
        } catch (e) {
            console.error('[SpeechAnalysis] Error sending audio:', e);
        }
    }, [blobToBase64]);

    const reconnectCountRef = useRef(0);
    const reconnectTimeoutRef = useRef<number | null>(null);

    // Connect to WebSocket
    const connect = useCallback(() => {
        if (wsRef.current?.readyState === WebSocket.OPEN || wsRef.current?.readyState === WebSocket.CONNECTING) return;

        setError(null);
        const wsEndpoint = `${wsUrl}/v1/speech/ws/speech-analysis/${sessionId}`;

        try {
            const ws = new WebSocket(wsEndpoint);

            ws.onopen = () => {
                console.log('[SpeechAnalysis] WebSocket connected');
                setIsConnected(true);
                setError(null);
                reconnectCountRef.current = 0;
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);

                    if (data.type === 'analysis') {
                        // Calculate words per minute (assuming 3-second chunks)
                        const chunkDurationMinutes = 3 / 60;
                        const wpm = Math.round((data.word_count ?? 0) / chunkDurationMinutes);

                        // Determine speech rate status (optimal: 120-150 WPM)
                        let speechRateStatus: 'slow' | 'optimal' | 'fast' = 'optimal';
                        if (wpm < 100) speechRateStatus = 'slow';
                        else if (wpm > 160) speechRateStatus = 'fast';

                        // Calculate vocal clarity based on filler words and grammar
                        const fillerPenalty = Math.min((data.filler_count ?? 0) * 5, 30);
                        const grammarPenalty = Math.min((data.grammar_error_count ?? 0) * 10, 30);
                        const baseClarity = 100 - fillerPenalty - grammarPenalty;
                        const vocalClarity = Math.max(baseClarity, 20);

                        let clarityFeedback = "Great clarity!";
                        if (vocalClarity < 50) clarityFeedback = "Try to reduce filler words and speak more clearly";
                        else if (vocalClarity < 70) clarityFeedback = "Good, but watch for filler words";

                        const newMetrics: SpeechMetrics = {
                            transcription: data.transcription ?? '',
                            word_count: data.word_count ?? 0,
                            grammar_issues: data.grammar_issues ?? [],
                            grammar_error_count: data.grammar_error_count ?? 0,
                            emotions: data.emotions ?? [],
                            dominant_emotion: data.dominant_emotion ?? 'neutral',
                            dominant_emotion_score: data.dominant_emotion_score ?? 0,
                            filler_count: data.filler_count ?? 0,
                            filler_words: data.filler_words ?? [],
                            words_per_minute: wpm,
                            speech_rate_status: speechRateStatus,
                            vocal_clarity: vocalClarity,
                            clarity_feedback: clarityFeedback,
                            timestamp: data.timestamp ?? Date.now()
                        };

                        setMetrics(newMetrics);

                        // Add to transcription history if not empty
                        if (newMetrics.transcription.trim()) {
                            setTranscriptionHistory(prev => [...prev, newMetrics.transcription]);
                        }
                    } else if (data.type === 'error') {
                        setError(data.message);
                    } else if (data.type === 'summary') {
                        console.log('[SpeechAnalysis] Session summary:', data);
                    }
                } catch (e) {
                    console.error('[SpeechAnalysis] Error parsing message:', e);
                }
            };

            ws.onerror = (event) => {
                console.error('[SpeechAnalysis] WebSocket error:', event);
                setError('Connection error');
            };

            ws.onclose = () => {
                console.log('[SpeechAnalysis] WebSocket closed');
                setIsConnected(false);
                setIsAnalyzing(false);
                
                // Exponential backoff reconnection
                if (reconnectCountRef.current < 5) {
                    const timeout = Math.pow(2, reconnectCountRef.current) * 1000;
                    reconnectTimeoutRef.current = window.setTimeout(connect, timeout);
                    reconnectCountRef.current += 1;
                }
            };

            wsRef.current = ws;
        } catch (e) {
            setError(`Failed to connect: ${e}`);
        }
    }, [wsUrl, sessionId]);

    // Start microphone capture and analysis
    const startAnalysis = useCallback(async () => {
        try {
            // Request microphone access
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    sampleRate: 16000
                }
            });
            streamRef.current = stream;

            // Create MediaRecorder
            const mediaRecorder = new MediaRecorder(stream, {
                mimeType: 'audio/webm;codecs=opus'
            });

            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunksRef.current.push(event.data);
                }
            };

            mediaRecorderRef.current = mediaRecorder;

            // Connect to WebSocket
            connect();

            // Wait for WebSocket connection
            const waitForConnection = () => {
                if (wsRef.current?.readyState === WebSocket.OPEN) {
                    // Start recording
                    mediaRecorder.start(1000); // Collect data every 1 second

                    // Set up interval to send chunks
                    intervalRef.current = window.setInterval(sendAudioChunk, chunkIntervalMs);

                    setIsAnalyzing(true);
                } else if (wsRef.current?.readyState === WebSocket.CONNECTING) {
                    setTimeout(waitForConnection, 100);
                }
            };

            setTimeout(waitForConnection, 100);
        } catch (e) {
            console.error('[SpeechAnalysis] Failed to start:', e);
            setError(`Microphone access denied: ${e}`);
        }
    }, [connect, sendAudioChunk, chunkIntervalMs]);

    // Stop analysis
    const stopAnalysis = useCallback(() => {
        // Stop interval
        if (intervalRef.current) {
            clearInterval(intervalRef.current);
            intervalRef.current = null;
        }

        // Send any remaining audio
        sendAudioChunk();

        // Stop MediaRecorder
        if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
            mediaRecorderRef.current.stop();
        }

        // Stop microphone stream
        if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop());
            streamRef.current = null;
        }

        setIsAnalyzing(false);
    }, [sendAudioChunk]);

    // Reset session
    const resetSession = useCallback(() => {
        const ws = wsRef.current;
        if (ws?.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'reset' }));
        }
        setMetrics(null);
        setTranscriptionHistory([]);
        audioChunksRef.current = [];
    }, []);

    // Get session summary
    const getSummary = useCallback(() => {
        const ws = wsRef.current;
        if (ws?.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'get_summary' }));
        }
    }, []);

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            if (intervalRef.current) {
                clearInterval(intervalRef.current);
            }
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
            }
            if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
                mediaRecorderRef.current.stop();
            }
            if (streamRef.current) {
                streamRef.current.getTracks().forEach(track => track.stop());
            }
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, []);

    return {
        metrics,
        transcriptionHistory,
        isConnected,
        isAnalyzing,
        error,
        startAnalysis,
        stopAnalysis,
        resetSession,
        getSummary
    };
}

export default useSpeechAnalysis;
