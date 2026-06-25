/**
 * GazeDirectionPanel Component
 * 
 * Sidebar panel showing real-time gaze direction, eye contact percentage,
 * and feedback messages to help users maintain proper eye contact.
 */
import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Eye, AlertTriangle, CheckCircle2, Target, ArrowUp, ArrowDown, ArrowLeft, ArrowRight } from 'lucide-react';
import { BehavioralMetrics } from '@/hooks/useBehavioralAnalysis';

interface GazeDirectionPanelProps {
    metrics: BehavioralMetrics | null;
    isAnalyzing: boolean;
}

const GazeDirectionPanel: React.FC<GazeDirectionPanelProps> = ({ metrics, isAnalyzing }) => {
    const getDirectionIcon = () => {
        if (!metrics) return <Target className="w-6 h-6 text-foreground/50" />;

        switch (metrics.gaze_direction) {
            case 'left':
                return <ArrowLeft className="w-6 h-6 text-orange-400" />;
            case 'right':
                return <ArrowRight className="w-6 h-6 text-orange-400" />;
            case 'up':
                return <ArrowUp className="w-6 h-6 text-orange-400" />;
            case 'down':
                return <ArrowDown className="w-6 h-6 text-orange-400" />;
            default:
                return <Target className="w-6 h-6 text-green-400" />;
        }
    };

    const getDirectionLabel = () => {
        if (!metrics || !metrics.face_detected) return 'No face detected';

        switch (metrics.gaze_direction) {
            case 'left': return 'Looking LEFT';
            case 'right': return 'Looking RIGHT';
            case 'up': return 'Looking UP';
            case 'down': return 'Looking DOWN';
            default: return 'Looking at CENTER ✓';
        }
    };

    // Use real eye contact percentage from backend gaze tracking
    const isLookingAtCamera = metrics?.looking_at_camera ?? false;
    const eyeContactPct = metrics?.eye_contact_percentage ?? 0;

    return (
        <div className="bg-gradient-to-br from-background to-gradient-start/10 border border-primary/30 rounded-xl p-4">
            <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-full bg-purple-500/20 flex items-center justify-center">
                    <Eye className="w-5 h-5 text-purple-400" />
                </div>
                <div>
                    <h3 className="font-heading font-bold text-foreground">Eye Contact</h3>
                    <p className="text-xs text-foreground/60">Gaze direction tracking</p>
                </div>
            </div>

            {/* Gaze Direction Compass */}
            <div className="mb-4 p-4 bg-black/20 rounded-lg border border-primary/10">
                <div className="flex items-center justify-center gap-4">
                    {/* Direction Indicator Circle */}
                    <div className="relative w-24 h-24">
                        {/* Background circle */}
                        <div className="absolute inset-0 rounded-full border-2 border-foreground/20" />

                        {/* Center target */}
                        <motion.div
                            className={`absolute inset-0 flex items-center justify-center rounded-full ${isLookingAtCamera
                                ? 'bg-green-500/20 border-2 border-green-500'
                                : 'bg-orange-500/20 border-2 border-orange-500'
                                }`}
                            animate={{ scale: isLookingAtCamera ? [1, 1.05, 1] : 1 }}
                            transition={{ duration: 1.5, repeat: isLookingAtCamera ? Infinity : 0 }}
                        >
                            {getDirectionIcon()}
                        </motion.div>

                        {/* Direction indicators */}
                        <div className="absolute -top-1 left-1/2 -translate-x-1/2 text-xs text-foreground/40">UP</div>
                        <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 text-xs text-foreground/40">DOWN</div>
                        <div className="absolute top-1/2 -left-4 -translate-y-1/2 text-xs text-foreground/40">L</div>
                        <div className="absolute top-1/2 -right-3 -translate-y-1/2 text-xs text-foreground/40">R</div>
                    </div>

                    {/* Direction Label */}
                    <div className="text-center">
                        <AnimatePresence mode="wait">
                            <motion.div
                                key={metrics?.gaze_direction || 'none'}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -10 }}
                                className={`font-heading font-bold text-lg ${isLookingAtCamera ? 'text-green-400' : 'text-orange-400'
                                    }`}
                            >
                                {getDirectionLabel()}
                            </motion.div>
                        </AnimatePresence>
                    </div>
                </div>
            </div>

            {/* Eye Contact Percentage */}
            <div className="mb-4">
                <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-foreground">Eye Contact</span>
                    <span className={`font-heading text-xl font-bold ${eyeContactPct >= 60 ? 'text-green-400' :
                        eyeContactPct >= 40 ? 'text-yellow-400' : 'text-red-400'
                        }`}>
                        {Math.round(eyeContactPct)}%
                    </span>
                </div>
                <div className="h-3 bg-foreground/10 rounded-full overflow-hidden">
                    <motion.div
                        className={`h-full rounded-full ${eyeContactPct >= 60 ? 'bg-gradient-to-r from-green-500 to-green-400' :
                            eyeContactPct >= 40 ? 'bg-gradient-to-r from-yellow-500 to-yellow-400' :
                                'bg-gradient-to-r from-red-500 to-red-400'
                            }`}
                        initial={{ width: 0 }}
                        animate={{ width: `${eyeContactPct}%` }}
                        transition={{ duration: 0.5, ease: 'easeOut' }}
                    />
                </div>
                <p className="text-xs text-foreground/50 mt-1">
                    {eyeContactPct >= 60
                        ? 'Great eye contact! Keep it up.'
                        : eyeContactPct >= 40
                            ? 'Good, but try to look at the camera more.'
                            : 'Focus on looking at the camera lens.'}
                </p>
            </div>

            {/* Feedback Message */}
            <AnimatePresence>
                {!isLookingAtCamera && metrics?.face_detected && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="p-3 bg-orange-500/20 border border-orange-500/30 rounded-lg"
                    >
                        <div className="flex items-start gap-2">
                            <AlertTriangle className="w-4 h-4 text-orange-400 mt-0.5 shrink-0" />
                            <div>
                                <p className="text-sm font-semibold text-orange-400">
                                    Look at the Camera
                                </p>
                                <p className="text-xs text-foreground/70 mt-1">
                                    You should not look {metrics.gaze_direction}. Always look at the center (camera lens) for best impression.
                                </p>
                            </div>
                        </div>
                    </motion.div>
                )}

                {isLookingAtCamera && metrics?.face_detected && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="p-3 bg-green-500/20 border border-green-500/30 rounded-lg"
                    >
                        <div className="flex items-center gap-2">
                            <CheckCircle2 className="w-4 h-4 text-green-400" />
                            <p className="text-sm font-medium text-green-400">
                                Perfect! Looking at camera
                            </p>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Status when not analyzing */}
            {!isAnalyzing && (
                <div className="text-center text-sm text-foreground/50 py-4">
                    Start practicing to see eye contact analysis
                </div>
            )}
        </div>
    );
};

export default GazeDirectionPanel;
