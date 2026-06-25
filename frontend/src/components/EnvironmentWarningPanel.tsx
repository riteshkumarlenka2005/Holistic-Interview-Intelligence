/**
 * EnvironmentWarningPanel Component
 * 
 * Displays warnings when multiple people are detected in the frame.
 * Includes audio alert functionality to notify the user.
 */
import React, { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertTriangle, Users, Volume2, VolumeX, MapPin } from 'lucide-react';
import { BehavioralMetrics } from '@/hooks/useBehavioralAnalysis';

interface EnvironmentWarningPanelProps {
    metrics: BehavioralMetrics | null;
    isAnalyzing: boolean;
}

const EnvironmentWarningPanel: React.FC<EnvironmentWarningPanelProps> = ({ metrics, isAnalyzing }) => {
    const [audioEnabled, setAudioEnabled] = useState(true);
    const [hasPlayed, setHasPlayed] = useState(false);
    const audioContextRef = useRef<AudioContext | null>(null);
    const lastWarningTime = useRef<number>(0);

    // Play warning sound when multiple people detected
    useEffect(() => {
        if (!metrics?.multi_person_warning || !audioEnabled || !isAnalyzing) {
            setHasPlayed(false);
            return;
        }

        const now = Date.now();
        // Only play sound every 10 seconds to avoid constant beeping
        if (now - lastWarningTime.current < 10000) return;

        // Create and play warning sound
        try {
            if (!audioContextRef.current) {
                audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
            }

            const ctx = audioContextRef.current;
            if (ctx.state === 'suspended') {
                ctx.resume();
            }

            // Create a gentle warning tone (not jarring)
            const oscillator = ctx.createOscillator();
            const gainNode = ctx.createGain();

            oscillator.connect(gainNode);
            gainNode.connect(ctx.destination);

            oscillator.frequency.value = 440; // A4 note
            oscillator.type = 'sine';

            // Gentle fade in/out
            gainNode.gain.setValueAtTime(0, ctx.currentTime);
            gainNode.gain.linearRampToValueAtTime(0.3, ctx.currentTime + 0.1);
            gainNode.gain.linearRampToValueAtTime(0, ctx.currentTime + 0.5);

            oscillator.start(ctx.currentTime);
            oscillator.stop(ctx.currentTime + 0.5);

            // Second beep
            setTimeout(() => {
                if (audioContextRef.current) {
                    const osc2 = ctx.createOscillator();
                    const gain2 = ctx.createGain();
                    osc2.connect(gain2);
                    gain2.connect(ctx.destination);
                    osc2.frequency.value = 523.25; // C5 note
                    osc2.type = 'sine';
                    gain2.gain.setValueAtTime(0, ctx.currentTime);
                    gain2.gain.linearRampToValueAtTime(0.3, ctx.currentTime + 0.1);
                    gain2.gain.linearRampToValueAtTime(0, ctx.currentTime + 0.5);
                    osc2.start(ctx.currentTime);
                    osc2.stop(ctx.currentTime + 0.5);
                }
            }, 300);

            lastWarningTime.current = now;
            setHasPlayed(true);
        } catch (e) {
            console.error('Failed to play warning sound:', e);
        }
    }, [metrics?.multi_person_warning, audioEnabled, isAnalyzing]);

    const totalFaces = metrics?.total_faces_detected || 0;
    const envQuality = metrics?.environment_quality || 'good';

    const getEnvironmentColor = () => {
        switch (envQuality) {
            case 'crowded': return 'text-red-500';
            case 'busy': return 'text-orange-400';
            default: return 'text-green-400';
        }
    };

    const getEnvironmentLabel = () => {
        switch (envQuality) {
            case 'crowded': return 'Crowded Environment';
            case 'busy': return 'Busy Environment';
            default: return 'Good Environment';
        }
    };

    return (
        <div className="bg-gradient-to-br from-background to-gradient-start/10 border border-primary/30 rounded-xl p-4">
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-yellow-500/20 flex items-center justify-center">
                        <MapPin className="w-5 h-5 text-yellow-400" />
                    </div>
                    <div>
                        <h3 className="font-heading font-bold text-foreground">Environment</h3>
                        <p className="text-xs text-foreground/60">Background detection</p>
                    </div>
                </div>

                {/* Audio toggle */}
                <button
                    onClick={() => setAudioEnabled(!audioEnabled)}
                    className={`p-2 rounded-lg transition-colors ${audioEnabled ? 'bg-green-500/20 text-green-400' : 'bg-foreground/10 text-foreground/40'
                        }`}
                    title={audioEnabled ? 'Mute warnings' : 'Enable audio warnings'}
                >
                    {audioEnabled ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
                </button>
            </div>

            {/* Environment Quality Indicator */}
            <div className="mb-4 p-3 bg-black/20 rounded-lg border border-primary/10">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <Users className={`w-4 h-4 ${getEnvironmentColor()}`} />
                        <span className={`text-sm font-medium ${getEnvironmentColor()}`}>
                            {getEnvironmentLabel()}
                        </span>
                    </div>
                    <span className="text-xs text-foreground/50">
                        {totalFaces} {totalFaces === 1 ? 'face' : 'faces'} detected
                    </span>
                </div>
            </div>

            {/* Warning Message */}
            <AnimatePresence>
                {metrics?.multi_person_warning && isAnalyzing && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="p-3 bg-orange-500/20 border border-orange-500/30 rounded-lg"
                    >
                        <div className="flex items-start gap-2">
                            <AlertTriangle className="w-4 h-4 text-orange-400 mt-0.5 shrink-0 animate-pulse" />
                            <div>
                                <p className="text-sm font-semibold text-orange-400">
                                    Multiple People Detected
                                </p>
                                <p className="text-xs text-foreground/70 mt-1">
                                    Please sit in a <strong>clean, empty place</strong> for best results.
                                    Find a quiet location with minimal background distractions.
                                </p>
                            </div>
                        </div>
                    </motion.div>
                )}

                {!metrics?.multi_person_warning && isAnalyzing && metrics?.face_detected && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="p-3 bg-green-500/20 border border-green-500/30 rounded-lg"
                    >
                        <div className="flex items-center gap-2">
                            <MapPin className="w-4 h-4 text-green-400" />
                            <p className="text-sm font-medium text-green-400">
                                Perfect! Clean environment
                            </p>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {!isAnalyzing && (
                <div className="text-center text-sm text-foreground/50 py-2">
                    Start practicing to see environment analysis
                </div>
            )}
        </div>
    );
};

export default EnvironmentWarningPanel;
