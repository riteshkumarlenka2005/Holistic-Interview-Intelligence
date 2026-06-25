/**
 * SpeechRatePanel Component
 * 
 * Displays real-time speech rate (words per minute), vocal clarity,
 * and provides feedback on speaking pace.
 */
import React from 'react';
import { motion } from 'framer-motion';
import { Mic, Gauge, Sparkles, AlertCircle, CheckCircle2, Zap } from 'lucide-react';
import { SpeechMetrics } from '@/hooks/useSpeechAnalysis';

interface SpeechRatePanelProps {
    metrics: SpeechMetrics | null;
    isAnalyzing: boolean;
}

const SpeechRatePanel: React.FC<SpeechRatePanelProps> = ({ metrics, isAnalyzing }) => {
    const wpm = metrics?.words_per_minute || 0;
    const speechRateStatus = metrics?.speech_rate_status || 'optimal';
    const vocalClarity = metrics?.vocal_clarity || 100;
    const clarityFeedback = metrics?.clarity_feedback || "Start speaking to analyze";

    // Optimal WPM range: 120-150
    const OPTIMAL_MIN = 100;
    const OPTIMAL_MAX = 160;
    const MAX_WPM = 200;

    const getSpeedColor = () => {
        switch (speechRateStatus) {
            case 'slow': return 'text-blue-400';
            case 'fast': return 'text-red-400';
            default: return 'text-green-400';
        }
    };

    const getSpeedLabel = () => {
        switch (speechRateStatus) {
            case 'slow': return 'Speaking Slowly';
            case 'fast': return 'Speaking Too Fast';
            default: return 'Optimal Speed';
        }
    };

    const getSpeedFeedback = () => {
        switch (speechRateStatus) {
            case 'slow':
                return 'Try to speak a bit faster. Aim for 120-150 words per minute.';
            case 'fast':
                return 'Slow down! Your speed should not exceed 150 WPM for clarity.';
            default:
                return 'Great pace! You\'re speaking at an interview-friendly speed.';
        }
    };

    const getClarityColor = () => {
        if (vocalClarity >= 70) return 'text-green-400';
        if (vocalClarity >= 50) return 'text-yellow-400';
        return 'text-red-400';
    };

    // Calculate WPM gauge position (0-100%)
    const gaugePosition = Math.min((wpm / MAX_WPM) * 100, 100);

    return (
        <div className="bg-gradient-to-br from-background to-gradient-start/10 border border-primary/30 rounded-xl p-4">
            <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-full bg-cyan-500/20 flex items-center justify-center">
                    <Gauge className="w-5 h-5 text-cyan-400" />
                </div>
                <div>
                    <h3 className="font-heading font-bold text-foreground">Speech Rate</h3>
                    <p className="text-xs text-foreground/60">Words per minute analysis</p>
                </div>
            </div>

            {/* WPM Display */}
            <div className="mb-4 p-4 bg-black/20 rounded-lg border border-primary/10">
                <div className="flex items-center justify-between mb-3">
                    <span className="text-sm text-foreground/70">Current Speed</span>
                    <div className="flex items-baseline gap-1">
                        <span className={`font-heading text-3xl font-bold ${getSpeedColor()}`}>
                            {wpm}
                        </span>
                        <span className="text-xs text-foreground/50">WPM</span>
                    </div>
                </div>

                {/* Speed Gauge */}
                <div className="relative h-3 bg-foreground/10 rounded-full overflow-hidden mb-2">
                    {/* Optimal zone indicator */}
                    <div
                        className="absolute h-full bg-green-500/30"
                        style={{
                            left: `${(OPTIMAL_MIN / MAX_WPM) * 100}%`,
                            width: `${((OPTIMAL_MAX - OPTIMAL_MIN) / MAX_WPM) * 100}%`
                        }}
                    />

                    {/* Current position indicator */}
                    <motion.div
                        className={`absolute top-0 w-1 h-full rounded-full ${speechRateStatus === 'optimal' ? 'bg-green-500' :
                                speechRateStatus === 'slow' ? 'bg-blue-500' : 'bg-red-500'
                            }`}
                        initial={{ left: 0 }}
                        animate={{ left: `${gaugePosition}%` }}
                        transition={{ duration: 0.5, ease: 'easeOut' }}
                    />
                </div>

                <div className="flex items-center justify-between text-xs text-foreground/40">
                    <span>Slow</span>
                    <span className="text-green-400">Optimal (100-160)</span>
                    <span>Fast</span>
                </div>
            </div>

            {/* Speed Status */}
            <div className={`flex items-center gap-2 mb-3 ${getSpeedColor()}`}>
                {speechRateStatus === 'optimal' ? (
                    <CheckCircle2 className="w-4 h-4" />
                ) : speechRateStatus === 'fast' ? (
                    <Zap className="w-4 h-4" />
                ) : (
                    <AlertCircle className="w-4 h-4" />
                )}
                <span className="text-sm font-medium">{getSpeedLabel()}</span>
            </div>

            <p className="text-xs text-foreground/60 mb-4">{getSpeedFeedback()}</p>

            {/* Vocal Clarity */}
            <div className="border-t border-primary/10 pt-4">
                <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-foreground flex items-center gap-2">
                        <Sparkles className="w-3 h-3 text-purple-400" />
                        Vocal Clarity
                    </span>
                    <span className={`font-heading text-lg font-bold ${getClarityColor()}`}>
                        {vocalClarity}%
                    </span>
                </div>

                <div className="h-2 bg-foreground/10 rounded-full overflow-hidden mb-2">
                    <motion.div
                        className={`h-full rounded-full ${vocalClarity >= 70 ? 'bg-gradient-to-r from-green-500 to-green-400' :
                                vocalClarity >= 50 ? 'bg-gradient-to-r from-yellow-500 to-yellow-400' :
                                    'bg-gradient-to-r from-red-500 to-red-400'
                            }`}
                        initial={{ width: 0 }}
                        animate={{ width: `${vocalClarity}%` }}
                        transition={{ duration: 0.5, ease: 'easeOut' }}
                    />
                </div>

                <p className="text-xs text-foreground/50">{clarityFeedback}</p>
            </div>

            {!isAnalyzing && (
                <div className="text-center text-sm text-foreground/50 pt-4 border-t border-primary/10 mt-4">
                    Start speaking to analyze your speech rate
                </div>
            )}
        </div>
    );
};

export default SpeechRatePanel;
