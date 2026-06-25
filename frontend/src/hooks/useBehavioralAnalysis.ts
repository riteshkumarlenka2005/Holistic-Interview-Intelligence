/**
 * useBehavioralAnalysis Hook
 * 
 * React hook for real-time behavioral analysis via WebSocket.
 * Captures video frames and streams them to the backend for emotion detection.
 */
import { useState, useRef, useCallback, useEffect } from 'react';

export interface BehavioralMetrics {
    confidence_score: number;
    nervousness_score: number;
    behavioral_tag: string;
    emotions: Record<string, number>;
    face_detected: boolean;
    face_box: [number, number, number, number] | null;
    timestamp: number;
    // Gaze tracking fields
    gaze_direction: 'left' | 'right' | 'up' | 'down' | 'center';
    gaze_x: number;  // -1 to 1
    gaze_y: number;  // -1 to 1
    looking_at_camera: boolean;
    eye_contact_percentage: number;
    left_iris_position: [number, number] | null;  // normalized 0-1
    right_iris_position: [number, number] | null;  // normalized 0-1
    // Eye bounding boxes for green eye detection rectangles
    left_eye_box: [number, number, number, number] | null;  // (x, y, w, h) normalized 0-1
    right_eye_box: [number, number, number, number] | null;  // (x, y, w, h) normalized 0-1
    // Multi-person detection
    total_faces_detected: number;
    multi_person_warning: boolean;
    environment_quality: 'good' | 'busy' | 'crowded';
}

export interface UseBehavioralAnalysisOptions {
    sessionId?: string;
    fps?: number; // Frames per second to analyze
    wsUrl?: string;
}

export interface UseBehavioralAnalysisReturn {
    metrics: BehavioralMetrics | null;
    isConnected: boolean;
    isAnalyzing: boolean;
    error: string | null;
    startAnalysis: (videoElement: HTMLVideoElement) => void;
    stopAnalysis: () => void;
    resetSession: () => void;
}

const DEFAULT_WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

export function useBehavioralAnalysis(
    options: UseBehavioralAnalysisOptions = {}
): UseBehavioralAnalysisReturn {
    const {
        sessionId = `session_${Date.now()}`,
        fps = 5, // 5 FPS is good balance between responsiveness and performance
        wsUrl = DEFAULT_WS_URL
    } = options;

    const [metrics, setMetrics] = useState<BehavioralMetrics | null>(null);
    const [isConnected, setIsConnected] = useState(false);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const wsRef = useRef<WebSocket | null>(null);
    const videoRef = useRef<HTMLVideoElement | null>(null);
    const canvasRef = useRef<HTMLCanvasElement | null>(null);
    const intervalRef = useRef<number | null>(null);

    // Create hidden canvas for frame capture
    useEffect(() => {
        canvasRef.current = document.createElement('canvas');
        return () => {
            canvasRef.current = null;
        };
    }, []);

    // Capture frame from video as base64
    const captureFrame = useCallback((): string | null => {
        const video = videoRef.current;
        const canvas = canvasRef.current;

        if (!video || !canvas || video.readyState < 2) {
            return null;
        }

        // Set canvas size to match video
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        // Draw video frame to canvas
        const ctx = canvas.getContext('2d');
        if (!ctx) return null;

        ctx.drawImage(video, 0, 0);

        // Convert to base64 JPEG (good compression)
        return canvas.toDataURL('image/jpeg', 0.7);
    }, []);

    // Send frame to WebSocket
    const sendFrame = useCallback(() => {
        const ws = wsRef.current;
        if (!ws || ws.readyState !== WebSocket.OPEN) return;

        const frameData = captureFrame();
        if (!frameData) return;

        ws.send(JSON.stringify({
            type: 'frame',
            data: frameData,
            timestamp: Date.now()
        }));
    }, [captureFrame]);

    // Connect to WebSocket
    const connect = useCallback(() => {
        if (wsRef.current?.readyState === WebSocket.OPEN) return;

        setError(null);
        const wsEndpoint = `${wsUrl}/v1/behavioral/ws/behavioral-analysis/${sessionId}`;

        try {
            const ws = new WebSocket(wsEndpoint);

            ws.onopen = () => {
                console.log('Behavioral analysis WebSocket connected');
                setIsConnected(true);
                setError(null);
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);

                    if (data.type === 'analysis') {
                        setMetrics({
                            confidence_score: data.confidence_score,
                            nervousness_score: data.nervousness_score,
                            behavioral_tag: data.behavioral_tag,
                            emotions: data.emotions || {},
                            face_detected: data.face_detected,
                            face_box: data.face_box,
                            timestamp: data.timestamp,
                            gaze_direction: data.gaze_direction || 'center',
                            gaze_x: data.gaze_x || 0,
                            gaze_y: data.gaze_y || 0,
                            looking_at_camera: data.looking_at_camera ?? true,
                            eye_contact_percentage: data.eye_contact_percentage || 0,
                            left_iris_position: data.left_iris_position || null,
                            right_iris_position: data.right_iris_position || null,
                            left_eye_box: data.left_eye_box || null,
                            right_eye_box: data.right_eye_box || null,
                            total_faces_detected: data.total_faces_detected || 1,
                            multi_person_warning: data.multi_person_warning || false,
                            environment_quality: data.environment_quality || 'good'
                        });
                    } else if (data.type === 'error') {
                        setError(data.message);
                    }
                } catch (e) {
                    console.error('Error parsing WebSocket message:', e);
                }
            };

            ws.onerror = (event) => {
                console.error('WebSocket error:', event);
                setError('Connection error');
            };

            ws.onclose = () => {
                console.log('WebSocket closed');
                setIsConnected(false);
                setIsAnalyzing(false);
            };

            wsRef.current = ws;
        } catch (e) {
            setError(`Failed to connect: ${e}`);
        }
    }, [wsUrl, sessionId]);

    // Start analysis
    const startAnalysis = useCallback((videoElement: HTMLVideoElement) => {
        videoRef.current = videoElement;

        // Connect to WebSocket if not connected
        connect();

        // Wait for connection then start sending frames
        const checkConnectionAndStart = () => {
            if (wsRef.current?.readyState === WebSocket.OPEN) {
                setIsAnalyzing(true);
                // Start frame capture interval
                const intervalMs = 1000 / fps;
                intervalRef.current = window.setInterval(sendFrame, intervalMs);
            } else if (wsRef.current?.readyState === WebSocket.CONNECTING) {
                setTimeout(checkConnectionAndStart, 100);
            }
        };

        setTimeout(checkConnectionAndStart, 100);
    }, [connect, fps, sendFrame]);

    // Stop analysis
    const stopAnalysis = useCallback(() => {
        if (intervalRef.current) {
            clearInterval(intervalRef.current);
            intervalRef.current = null;
        }
        setIsAnalyzing(false);
    }, []);

    // Reset session (clears emotion history on backend)
    const resetSession = useCallback(() => {
        const ws = wsRef.current;
        if (ws?.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'reset' }));
        }
        setMetrics(null);
    }, []);

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            if (intervalRef.current) {
                clearInterval(intervalRef.current);
            }
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, []);

    return {
        metrics,
        isConnected,
        isAnalyzing,
        error,
        startAnalysis,
        stopAnalysis,
        resetSession
    };
}

export default useBehavioralAnalysis;
