/**
 * FeaturesPage - Industrial-Grade Production Level UI
 * 
 * Features:
 * - Massive hero with 3D-like effects
 * - Clickable feature cards with detailed modals
 * - Premium Framer Motion animations
 * - 3D card tilt effects
 * - Comprehensive content sections
 * - Fully functional and interactive
 */
import { useState, useRef } from 'react';
import { motion, AnimatePresence, useMotionValue, useSpring, useTransform } from 'framer-motion';
import {
  Brain, Video, Mic, Eye, TrendingUp, Target, Zap, Shield, Globe, Users,
  MessageSquare, Award, BarChart, BookOpen, Lightbulb, CheckCircle, X,
  Play, ArrowRight, Sparkles, Cpu, Database, Cloud, Lock, Settings,
  Activity, Layers, Code, Terminal, Wand2, LineChart, PieChart, Gauge,
  Fingerprint, FileText, Clock, Star, ChevronRight, Rocket, Heart
} from 'lucide-react';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import { Button } from '@/components/ui/button';
import { Link } from 'react-router-dom';

// ============================================
// COMPREHENSIVE FEATURES DATA
// ============================================

interface Feature {
  id: string;
  icon: any;
  title: string;
  shortDescription: string;
  fullDescription: string;
  color: string;
  gradient: string;
  capabilities: string[];
  technicalDetails: {
    title: string;
    description: string;
  }[];
  useCases: string[];
  metrics: {
    label: string;
    value: string;
  }[];
  image?: string;
}

const CORE_FEATURES: Feature[] = [
  {
    id: 'video-analysis',
    icon: Video,
    title: 'Real-Time Video Analysis',
    shortDescription: 'Advanced computer vision tracks facial expressions, eye contact, posture, and body language throughout your interview.',
    fullDescription: 'Our state-of-the-art computer vision system uses deep learning models trained on millions of video frames to analyze your non-verbal communication in real-time. The AI tracks 468 facial landmarks, monitors eye gaze direction, analyzes hand gestures, and evaluates overall body posture to provide comprehensive feedback on your visual presentation.',
    color: 'text-red-500',
    gradient: 'from-red-500 to-orange-500',
    capabilities: [
      'Facial landmark detection (468 points)',
      'Eye contact percentage tracking',
      'Posture alignment monitoring',
      'Gesture pattern analysis',
      'Head movement frequency',
      'Micro-expression detection',
      'Engagement level scoring',
      'Anxiety indicator detection'
    ],
    technicalDetails: [
      { title: 'Model Architecture', description: 'MediaPipe Face Mesh + Custom CNN for expression classification' },
      { title: 'Frame Rate', description: '30 FPS real-time processing with <50ms latency' },
      { title: 'Accuracy', description: '94.7% accuracy on facial expression recognition' },
      { title: 'Privacy', description: 'All processing done locally, no video stored on servers' }
    ],
    useCases: [
      'Practice maintaining eye contact during difficult questions',
      'Learn to control nervous habits like fidgeting',
      'Perfect your posture for confidence projection',
      'Master appropriate facial expressions for different scenarios'
    ],
    metrics: [
      { label: 'Facial Points', value: '468' },
      { label: 'Latency', value: '<50ms' },
      { label: 'Accuracy', value: '94.7%' }
    ]
  },
  {
    id: 'speech-analysis',
    icon: Mic,
    title: 'Verbal Communication Analysis',
    shortDescription: 'Speech-to-text transcription with comprehensive analysis of your speaking patterns, tone, and content structure.',
    fullDescription: 'Our advanced speech analysis engine combines automatic speech recognition with natural language processing to evaluate not just what you say, but how you say it. We analyze speaking rate, filler word usage, tone variation, pause patterns, and content structure to help you become a more effective communicator.',
    color: 'text-blue-500',
    gradient: 'from-blue-500 to-cyan-500',
    capabilities: [
      'Real-time speech-to-text transcription',
      'Filler word detection (um, uh, like, you know)',
      'Speaking rate optimization (WPM)',
      'Pause classification (thinking vs nervous)',
      'Tone and pitch variation analysis',
      'Volume stability monitoring',
      'Sentiment and emotional tone',
      'STAR-method structure detection'
    ],
    technicalDetails: [
      { title: 'ASR Engine', description: 'Whisper Large V3 with speaker diarization' },
      { title: 'Languages', description: '40+ languages supported with accent adaptation' },
      { title: 'WER', description: '3.2% Word Error Rate on interview speech' },
      { title: 'Analysis', description: 'NLP-based content structure and coherence scoring' }
    ],
    useCases: [
      'Reduce filler word usage by 80%',
      'Optimize speaking pace for clarity',
      'Learn to use strategic pauses effectively',
      'Structure answers using STAR method'
    ],
    metrics: [
      { label: 'Languages', value: '40+' },
      { label: 'WER', value: '3.2%' },
      { label: 'Analysis Speed', value: 'Real-time' }
    ]
  },
  {
    id: 'multimodal-fusion',
    icon: Brain,
    title: 'Multimodal AI Fusion',
    shortDescription: 'Combines audio, video, and text data to provide holistic insights that mirror how real interviewers perceive you.',
    fullDescription: 'Our proprietary multimodal fusion engine is the heart of InterviewPro. It combines signals from video analysis, speech processing, and content evaluation to create a unified understanding of your interview performance. This mirrors how human interviewers simultaneously process multiple signals to form their impression of you.',
    color: 'text-purple-500',
    gradient: 'from-purple-500 to-violet-500',
    capabilities: [
      'Temporal alignment of all modalities',
      'Cross-modal conflict resolution',
      'Behavior event correlation',
      'Holistic readiness scoring',
      'Weighted signal combination',
      'Context-aware interpretation',
      'Confidence-weighted outputs',
      'Unified scoring framework'
    ],
    technicalDetails: [
      { title: 'Architecture', description: 'Transformer-based multimodal encoder with attention' },
      { title: 'Fusion Method', description: 'Late fusion with learned attention weights' },
      { title: 'Modalities', description: 'Video (30fps) + Audio (16kHz) + Text embeddings' },
      { title: 'Output', description: 'Unified score with per-modality confidence intervals' }
    ],
    useCases: [
      'Understand how verbal and non-verbal cues align',
      'Identify when facial expressions contradict speech',
      'Get holistic feedback that matches interviewer perception',
      'Improve overall presence and authenticity'
    ],
    metrics: [
      { label: 'Modalities', value: '3' },
      { label: 'Correlation', value: '0.92' },
      { label: 'Accuracy', value: '96.1%' }
    ]
  },
  {
    id: 'explainable-feedback',
    icon: MessageSquare,
    title: 'Explainable AI Feedback',
    shortDescription: 'Transparent AI explanations show exactly why you received each score and what behaviors influenced the assessment.',
    fullDescription: "We believe AI should never be a black box. Our explainable AI system provides detailed, human-readable explanations for every score and recommendation. You'll understand exactly what behaviors influenced your assessment and receive specific, actionable suggestions for improvement.",
    color: 'text-green-500',
    gradient: 'from-green-500 to-emerald-500',
    capabilities: [
      'Feature attribution analysis',
      'Behavior-driven explanations',
      'Counterfactual suggestions',
      'Human-readable insights',
      'Timeline-based annotations',
      'Confidence interval reporting',
      'Improvement prioritization',
      'Before/after comparisons'
    ],
    technicalDetails: [
      { title: 'Method', description: 'SHAP values + LIME for local interpretability' },
      { title: 'Visualization', description: 'Timeline-based behavior annotations' },
      { title: 'NLG', description: 'GPT-4 based natural language generation for feedback' },
      { title: 'Validation', description: 'Human expert validation with 91% agreement rate' }
    ],
    useCases: [
      'Understand why you received a specific confidence score',
      'See exactly which behaviors need improvement',
      'Get actionable suggestions with examples',
      'Track how specific changes improve your scores'
    ],
    metrics: [
      { label: 'Agreement', value: '91%' },
      { label: 'Clarity Score', value: '4.8/5' },
      { label: 'Actionability', value: '95%' }
    ]
  },
  {
    id: 'personalized-coaching',
    icon: Target,
    title: 'Personalized Coaching',
    shortDescription: 'Adaptive feedback tailored to your skill level, interview type, and career goals for maximum relevance.',
    fullDescription: 'No two interview candidates are the same. Our personalization engine adapts to your unique profile, skill level, target role, and learning style. Whether you\'re preparing for a technical interview at a FAANG company or a behavioral interview for a management role, our AI tailors its coaching to your specific needs.',
    color: 'text-amber-500',
    gradient: 'from-amber-500 to-orange-500',
    capabilities: [
      'Skill-level adaptation',
      'Role-specific benchmarks',
      'Industry-tailored feedback',
      'Progressive difficulty scaling',
      'Cultural sensitivity adjustments',
      'Learning style optimization',
      'Personalized practice plans',
      'Goal-oriented recommendations'
    ],
    technicalDetails: [
      { title: 'Profiling', description: 'Multi-armed bandit for adaptive difficulty' },
      { title: 'Benchmarks', description: '500+ role-specific performance baselines' },
      { title: 'Adaptation', description: 'Continuous learning from user progress' },
      { title: 'Personalization', description: 'Collaborative filtering with similar profiles' }
    ],
    useCases: [
      'Get feedback calibrated to your experience level',
      'Practice with role-specific question banks',
      'Receive industry-appropriate coaching',
      'Follow a personalized improvement roadmap'
    ],
    metrics: [
      { label: 'Roles', value: '500+' },
      { label: 'Personalization', value: '98%' },
      { label: 'Satisfaction', value: '4.9/5' }
    ]
  },
  {
    id: 'progress-tracking',
    icon: TrendingUp,
    title: 'Progress Tracking',
    shortDescription: 'Comprehensive analytics showing your improvement over time with detailed skill-wise breakdowns and trends.',
    fullDescription: 'Track your interview skills growth with our comprehensive analytics dashboard. See how each skill has improved over time, identify trends, and celebrate milestones. Our progress tracking helps you stay motivated and focused on the areas that matter most for your career goals.',
    color: 'text-indigo-500',
    gradient: 'from-indigo-500 to-blue-500',
    capabilities: [
      'Historical performance trends',
      'Skill-wise breakdown analysis',
      'Improvement velocity tracking',
      'Strengths and weaknesses mapping',
      'Goal achievement monitoring',
      'Milestone celebrations',
      'Comparative benchmarking',
      'Predictive readiness scoring'
    ],
    technicalDetails: [
      { title: 'Tracking', description: 'Time-series analysis with trend detection' },
      { title: 'Visualization', description: 'Interactive charts with drill-down capability' },
      { title: 'Prediction', description: 'ML-based readiness probability estimation' },
      { title: 'Export', description: 'PDF reports and data export functionality' }
    ],
    useCases: [
      'See how your confidence score has improved',
      'Identify skills that need more practice',
      'Set and track improvement goals',
      'Know when you\'re interview-ready'
    ],
    metrics: [
      { label: 'Data Points', value: '100+' },
      { label: 'Metrics', value: '25' },
      { label: 'Accuracy', value: '89%' }
    ]
  }
];

// Additional features
const ADDITIONAL_FEATURES: Feature[] = [
  {
    id: 'emotion-detection',
    icon: Heart,
    title: 'Emotion Detection',
    shortDescription: 'Real-time emotion recognition to help you project the right emotional state during interviews.',
    fullDescription: 'Our emotion detection system uses facial expression analysis combined with voice sentiment to identify your emotional state in real-time. This helps you understand how you come across emotionally and learn to project confidence, enthusiasm, and professionalism.',
    color: 'text-pink-500',
    gradient: 'from-pink-500 to-rose-500',
    capabilities: [
      '7 primary emotion classification',
      'Valence and arousal scoring',
      'Confidence vs nervousness detection',
      'Emotional consistency tracking',
      'Stress level monitoring',
      'Enthusiasm detection',
      'Engagement scoring',
      'Emotional intelligence feedback'
    ],
    technicalDetails: [
      { title: 'Model', description: 'FER-2013 trained ResNet-50 with attention' },
      { title: 'Emotions', description: 'Happy, Sad, Angry, Fear, Surprise, Disgust, Neutral' },
      { title: 'Accuracy', description: '87.3% on in-the-wild faces' },
      { title: 'Real-time', description: '<30ms inference per frame' }
    ],
    useCases: [
      'Learn to project confidence through facial expressions',
      'Control nervous expressions during difficult questions',
      'Show appropriate enthusiasm when discussing interests',
      'Maintain professional demeanor under pressure'
    ],
    metrics: [
      { label: 'Emotions', value: '7' },
      { label: 'Accuracy', value: '87.3%' },
      { label: 'Speed', value: '<30ms' }
    ]
  },
  {
    id: 'question-bank',
    icon: BookOpen,
    title: 'Intelligent Question Bank',
    shortDescription: 'AI-curated questions tailored to your target role, industry, and experience level.',
    fullDescription: 'Access thousands of interview questions curated by industry experts and powered by AI. Our question bank adapts to your target role, experience level, and the companies you\'re targeting to ensure you practice the most relevant questions.',
    color: 'text-teal-500',
    gradient: 'from-teal-500 to-cyan-500',
    capabilities: [
      '10,000+ curated questions',
      'Role-specific question sets',
      'Company-specific questions',
      'Difficulty progression',
      'Behavioral question generation',
      'Technical question adaptation',
      'Follow-up question simulation',
      'Industry-specific scenarios'
    ],
    technicalDetails: [
      { title: 'Database', description: '10,000+ questions across 50+ industries' },
      { title: 'Generation', description: 'GPT-4 based contextual question generation' },
      { title: 'Curation', description: 'Expert-validated with relevance scoring' },
      { title: 'Updates', description: 'Weekly additions based on current trends' }
    ],
    useCases: [
      'Practice company-specific interview questions',
      'Prepare for technical and behavioral rounds',
      'Experience realistic follow-up questions',
      'Build confidence with comprehensive coverage'
    ],
    metrics: [
      { label: 'Questions', value: '10K+' },
      { label: 'Industries', value: '50+' },
      { label: 'Updates', value: 'Weekly' }
    ]
  },
  {
    id: 'ai-interviewer',
    icon: Cpu,
    title: 'AI Interviewer Simulation',
    shortDescription: 'Practice with realistic AI interviewers that adapt to your responses in real-time.',
    fullDescription: 'Experience realistic interview simulations with our AI interviewer. It asks relevant follow-up questions, challenges your answers, and creates a genuine interview atmosphere to prepare you for the real thing.',
    color: 'text-violet-500',
    gradient: 'from-violet-500 to-purple-500',
    capabilities: [
      'Natural conversation flow',
      'Context-aware follow-ups',
      'Difficulty adaptation',
      'Multiple interviewer personas',
      'Industry-specific styles',
      'Challenge question generation',
      'Time-based sessions',
      'Realistic interruptions'
    ],
    technicalDetails: [
      { title: 'Engine', description: 'GPT-4 with custom interview fine-tuning' },
      { title: 'Personas', description: '20+ interviewer personalities' },
      { title: 'Context', description: 'Full session context for relevant follow-ups' },
      { title: 'Realism', description: '4.7/5 user-rated realism score' }
    ],
    useCases: [
      'Practice with tough interviewers',
      'Handle unexpected follow-up questions',
      'Build comfort with different interview styles',
      'Prepare for high-pressure situations'
    ],
    metrics: [
      { label: 'Personas', value: '20+' },
      { label: 'Realism', value: '4.7/5' },
      { label: 'Sessions', value: 'Unlimited' }
    ]
  },
  {
    id: 'privacy-security',
    icon: Shield,
    title: 'Privacy & Security',
    shortDescription: 'Enterprise-grade security with end-to-end encryption and complete data privacy.',
    fullDescription: 'Your privacy is our priority. All video and audio data is processed locally when possible, encrypted end-to-end, and never shared with third parties. You have complete control over your data with easy deletion options.',
    color: 'text-slate-500',
    gradient: 'from-slate-500 to-gray-500',
    capabilities: [
      '256-bit AES encryption',
      'Local-first processing',
      'GDPR compliance',
      'SOC 2 Type II certified',
      'Zero data selling',
      'User data control',
      'Automatic deletion options',
      'Transparent data practices'
    ],
    technicalDetails: [
      { title: 'Encryption', description: 'AES-256-GCM for data at rest and in transit' },
      { title: 'Processing', description: 'Client-side ML inference when possible' },
      { title: 'Compliance', description: 'GDPR, CCPA, SOC 2 Type II' },
      { title: 'Auditing', description: 'Annual third-party security audits' }
    ],
    useCases: [
      'Practice with confidence knowing data is secure',
      'Control exactly what data is stored',
      'Delete practice sessions anytime',
      'Trust in transparent privacy practices'
    ],
    metrics: [
      { label: 'Encryption', value: '256-bit' },
      { label: 'Uptime', value: '99.99%' },
      { label: 'Compliance', value: 'Full' }
    ]
  }
];

// Benefits data
const BENEFITS = [
  { icon: Award, title: 'Boost Confidence', description: 'Practice in a safe environment and receive constructive feedback to build interview confidence.', color: 'from-amber-500 to-orange-500' },
  { icon: BarChart, title: 'Track Improvement', description: 'See measurable progress over time with detailed analytics and skill-wise breakdowns.', color: 'from-blue-500 to-indigo-500' },
  { icon: BookOpen, title: 'Learn Best Practices', description: 'Access curated resources and tips based on your specific areas for improvement.', color: 'from-green-500 to-emerald-500' },
  { icon: Lightbulb, title: 'Gain Self-Awareness', description: 'Discover unconscious habits and communication patterns you never knew you had.', color: 'from-yellow-500 to-amber-500' },
  { icon: Users, title: 'Inclusive Access', description: 'Free tier for students ensures everyone has access to quality career preparation.', color: 'from-purple-500 to-violet-500' },
  { icon: Shield, title: 'Privacy First', description: 'Your data is encrypted and secure. Practice sessions are private and never shared.', color: 'from-slate-500 to-gray-500' },
];

// Technical capabilities
const TECHNICAL_CAPABILITIES = [
  {
    category: 'Verbal Analysis',
    icon: Mic,
    color: 'from-blue-500 to-cyan-500',
    features: [
      'Speech-to-text transcription',
      'Filler word frequency (um, uh, like)',
      'Speaking rate (words per minute)',
      'Pause classification (thinking vs nervous)',
      'Tone and pitch variation',
      'Volume stability',
      'Sentiment and emotional tone',
      'STAR-method structure detection',
      'Confidence score derivation'
    ]
  },
  {
    category: 'Non-Verbal Analysis',
    icon: Eye,
    color: 'from-purple-500 to-violet-500',
    features: [
      'Facial landmark detection',
      'Eye contact percentage',
      'Gaze timeline visualization',
      'Head movement frequency',
      'Posture alignment detection',
      'Gesture analysis',
      'Engagement detection',
      'Anxiety detection cues',
      'Micro-expression spotting'
    ]
  },
  {
    category: 'AI Intelligence',
    icon: Brain,
    color: 'from-green-500 to-emerald-500',
    features: [
      'LLM-based reasoning',
      'Multimodal fusion',
      'Temporal alignment',
      'Behavior event correlation',
      'Explainable AI outputs',
      'Personalization engine',
      'Adaptive difficulty',
      'Cultural sensitivity',
      'Bias mitigation'
    ]
  }
];

// ============================================
// 3D TILT CARD COMPONENT
// ============================================

function TiltCard({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  const ref = useRef<HTMLDivElement>(null);

  const x = useMotionValue(0);
  const y = useMotionValue(0);

  const mouseXSpring = useSpring(x);
  const mouseYSpring = useSpring(y);

  const rotateX = useTransform(mouseYSpring, [-0.5, 0.5], ["17.5deg", "-17.5deg"]);
  const rotateY = useTransform(mouseXSpring, [-0.5, 0.5], ["-17.5deg", "17.5deg"]);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!ref.current) return;

    const rect = ref.current.getBoundingClientRect();
    const width = rect.width;
    const height = rect.height;
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;
    const xPct = mouseX / width - 0.5;
    const yPct = mouseY / height - 0.5;

    x.set(xPct);
    y.set(yPct);
  };

  const handleMouseLeave = () => {
    x.set(0);
    y.set(0);
  };

  return (
    <motion.div
      ref={ref}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={{
        rotateY,
        rotateX,
        transformStyle: "preserve-3d",
      }}
      className={`relative ${className}`}
    >
      <div style={{ transform: "translateZ(75px)", transformStyle: "preserve-3d" }}>
        {children}
      </div>
    </motion.div>
  );
}

// ============================================
// FEATURE DETAIL MODAL
// ============================================

function FeatureDetailModal({ feature, onClose }: { feature: Feature; onClose: () => void }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 overflow-y-auto"
      onClick={onClose}
    >
      <div className="min-h-full flex items-center justify-center p-4 py-12">
        <motion.div
          initial={{ opacity: 0, scale: 0.9, y: 50 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.9, y: 50 }}
          transition={{ type: 'spring', damping: 25, stiffness: 300 }}
          className="relative w-full max-w-5xl bg-card-bg rounded-3xl shadow-2xl overflow-hidden"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className={`relative h-48 bg-gradient-to-br ${feature.gradient} overflow-hidden`}>
            <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGRlZnM+PHBhdHRlcm4gaWQ9ImdyaWQiIHdpZHRoPSI2MCIgaGVpZ2h0PSI2MCIgcGF0dGVyblVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+PHBhdGggZD0iTSAxMCAwIEwgMCAwIDAgMTAiIGZpbGw9Im5vbmUiIHN0cm9rZT0icmdiYSgyNTUsMjU1LDI1NSwwLjEpIiBzdHJva2Utd2lkdGg9IjEiLz48L3BhdHRlcm4+PC9kZWZzPjxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbGw9InVybCgjZ3JpZCkiLz48L3N2Zz4=')] opacity-30" />

            <div className="absolute inset-0 flex items-center justify-center">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.2, type: 'spring' }}
                className="w-24 h-24 rounded-2xl bg-white/20 backdrop-blur-sm flex items-center justify-center"
              >
                <feature.icon className="w-12 h-12 text-white" />
              </motion.div>
            </div>

            <button
              onClick={onClose}
              className="absolute top-4 right-4 w-10 h-10 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center text-white hover:bg-white/30 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Content */}
          <div className="p-8 lg:p-12">
            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="font-heading text-3xl lg:text-4xl font-black text-foreground mb-4"
            >
              {feature.title}
            </motion.h2>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15 }}
              className="font-paragraph text-lg text-foreground-muted mb-8 leading-relaxed"
            >
              {feature.fullDescription}
            </motion.p>

            {/* Metrics */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="grid grid-cols-3 gap-4 mb-10"
            >
              {feature.metrics.map((metric, i) => (
                <div key={i} className={`bg-gradient-to-br ${feature.gradient} rounded-xl p-4 text-center text-white`}>
                  <div className="font-heading text-2xl font-bold">{metric.value}</div>
                  <div className="text-sm opacity-80">{metric.label}</div>
                </div>
              ))}
            </motion.div>

            <div className="grid lg:grid-cols-2 gap-8">
              {/* Capabilities */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.25 }}
              >
                <h3 className="font-heading text-xl font-bold text-foreground mb-4 flex items-center gap-2">
                  <Sparkles className={`w-5 h-5 ${feature.color}`} />
                  Capabilities
                </h3>
                <ul className="space-y-3">
                  {feature.capabilities.map((cap, i) => (
                    <motion.li
                      key={i}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.3 + i * 0.05 }}
                      className="flex items-start gap-3"
                    >
                      <CheckCircle className={`w-5 h-5 ${feature.color} flex-shrink-0 mt-0.5`} />
                      <span className="font-paragraph text-foreground-muted">{cap}</span>
                    </motion.li>
                  ))}
                </ul>
              </motion.div>

              {/* Technical Details */}
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.25 }}
              >
                <h3 className="font-heading text-xl font-bold text-foreground mb-4 flex items-center gap-2">
                  <Terminal className={`w-5 h-5 ${feature.color}`} />
                  Technical Details
                </h3>
                <div className="space-y-4">
                  {feature.technicalDetails.map((detail, i) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, x: 10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.3 + i * 0.05 }}
                      className="bg-secondary/50 rounded-lg p-4"
                    >
                      <div className="font-heading text-sm font-bold text-foreground mb-1">{detail.title}</div>
                      <div className="font-paragraph text-sm text-foreground-muted">{detail.description}</div>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            </div>

            {/* Use Cases */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="mt-8 pt-8 border-t border-border-color"
            >
              <h3 className="font-heading text-xl font-bold text-foreground mb-4 flex items-center gap-2">
                <Target className={`w-5 h-5 ${feature.color}`} />
                Use Cases
              </h3>
              <div className="grid md:grid-cols-2 gap-4">
                {feature.useCases.map((useCase, i) => (
                  <div key={i} className="flex items-start gap-3 bg-card-bg border border-border-color rounded-lg p-4">
                    <ChevronRight className={`w-5 h-5 ${feature.color} flex-shrink-0 mt-0.5`} />
                    <span className="font-paragraph text-sm text-foreground-muted">{useCase}</span>
                  </div>
                ))}
              </div>
            </motion.div>

            {/* CTA */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="mt-8 flex items-center justify-center gap-4"
            >
              <Link to="/register">
                <Button className={`h-12 px-8 bg-gradient-to-r ${feature.gradient} text-white rounded-xl font-heading font-bold shadow-lg hover:shadow-xl transition-all`}>
                  <Rocket className="w-5 h-5 mr-2" />
                  Try This Feature
                </Button>
              </Link>
              <Button variant="outline" onClick={onClose} className="h-12 px-8 border-border-color text-foreground rounded-xl font-heading font-bold">
                Close
              </Button>
            </motion.div>
          </div>
        </motion.div>
      </div>
    </motion.div>
  );
}

// ============================================
// FEATURE CARD COMPONENT
// ============================================

function FeatureCard({ feature, index, onClick }: { feature: Feature; index: number; onClick: () => void }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 50 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.6, delay: index * 0.1 }}
    >
      <TiltCard>
        <motion.div
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={onClick}
          className="relative bg-card-bg border border-border-color rounded-2xl p-8 h-full shadow-lg hover:shadow-2xl transition-all duration-300 cursor-pointer group overflow-hidden"
        >
          {/* Background gradient on hover */}
          <div className={`absolute inset-0 bg-gradient-to-br ${feature.gradient} opacity-0 group-hover:opacity-5 transition-opacity duration-500`} />

          {/* Glow effect */}
          <div className={`absolute -top-24 -right-24 w-48 h-48 bg-gradient-to-br ${feature.gradient} rounded-full blur-3xl opacity-0 group-hover:opacity-20 transition-opacity duration-500`} />

          <div className="relative z-10">
            {/* Icon */}
            <motion.div
              whileHover={{ rotate: 5, scale: 1.1 }}
              transition={{ type: 'spring', stiffness: 300 }}
              className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${feature.gradient} flex items-center justify-center mb-6 shadow-lg`}
            >
              <feature.icon className="w-8 h-8 text-white" />
            </motion.div>

            <h3 className="font-heading text-2xl font-bold text-foreground mb-4 group-hover:text-primary transition-colors">
              {feature.title}
            </h3>

            <p className="font-paragraph text-foreground-muted mb-6 leading-relaxed">
              {feature.shortDescription}
            </p>

            {/* Capabilities preview */}
            <ul className="space-y-2 mb-6">
              {feature.capabilities.slice(0, 4).map((capability, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <CheckCircle className={`w-4 h-4 ${feature.color} flex-shrink-0 mt-1`} />
                  <span className="font-paragraph text-sm text-foreground-muted">{capability}</span>
                </li>
              ))}
            </ul>

            {/* Learn more button */}
            <div className="flex items-center gap-2 text-primary font-semibold group-hover:gap-3 transition-all">
              <span>Learn More</span>
              <ArrowRight className="w-4 h-4" />
            </div>
          </div>
        </motion.div>
      </TiltCard>
    </motion.div>
  );
}

// ============================================
// MAIN COMPONENT
// ============================================

export default function FeaturesPage() {
  const [selectedFeature, setSelectedFeature] = useState<Feature | null>(null);
  const allFeatures = [...CORE_FEATURES, ...ADDITIONAL_FEATURES];

  return (
    <div className="min-h-screen bg-background text-foreground overflow-hidden">
      <Header />

      {/* ==========================================
          HERO SECTION - Massive with 3D effects
          ========================================== */}
      <section className="relative w-full min-h-[90vh] flex items-center overflow-hidden">
        {/* Animated background */}
        <div className="absolute inset-0">
          <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-background to-accent-purple/10" />
          <div className="absolute top-[-30%] right-[-20%] w-[80vw] h-[80vw] rounded-full bg-primary/5 blur-3xl animate-pulse" />
          <div className="absolute bottom-[-30%] left-[-20%] w-[60vw] h-[60vw] rounded-full bg-accent-purple/5 blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />

          {/* Floating elements */}
          <motion.div
            animate={{ y: [-20, 20, -20], rotate: [0, 10, 0] }}
            transition={{ duration: 8, repeat: Infinity, ease: 'easeInOut' }}
            className="absolute top-[20%] left-[10%] w-20 h-20 rounded-2xl bg-gradient-to-br from-primary to-accent-purple opacity-20"
          />
          <motion.div
            animate={{ y: [20, -20, 20], rotate: [0, -10, 0] }}
            transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut' }}
            className="absolute bottom-[30%] right-[15%] w-16 h-16 rounded-full bg-gradient-to-br from-accent-purple to-primary opacity-20"
          />
          <motion.div
            animate={{ y: [-15, 15, -15], x: [-10, 10, -10] }}
            transition={{ duration: 10, repeat: Infinity, ease: 'easeInOut' }}
            className="absolute top-[40%] right-[30%] w-12 h-12 rounded-xl bg-gradient-to-br from-amber-500 to-orange-500 opacity-15"
          />
        </div>

        <div className="relative z-10 w-full px-6 lg:px-12 py-32">
          <div className="max-w-[100rem] mx-auto text-center">
            <motion.div
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
            >
              {/* Eyebrow */}
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.2 }}
                className="inline-flex items-center gap-3 px-6 py-3 bg-primary/10 border border-primary/20 rounded-full mb-8"
              >
                <Zap className="w-5 h-5 text-primary" />
                <span className="font-paragraph text-primary font-bold tracking-wide">POWERFUL AI TECHNOLOGY</span>
              </motion.div>

              {/* Main heading */}
              <motion.h1
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3, duration: 0.8 }}
                className="font-heading text-4xl sm:text-6xl md:text-7xl lg:text-9xl font-black text-foreground mb-8 leading-none"
              >
                Advanced
                <span className="block bg-gradient-to-r from-primary via-accent-purple to-primary bg-clip-text text-transparent bg-[length:200%_100%] animate-gradient">
                  Features
                </span>
              </motion.h1>

              {/* Subtitle */}
              <motion.p
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                className="font-paragraph text-xl lg:text-2xl text-foreground-muted max-w-4xl mx-auto mb-12 leading-relaxed"
              >
                Comprehensive AI analysis of your interview performance with <span className="text-foreground font-semibold">real-time feedback</span> on
                communication, confidence, and professional presence. <span className="text-primary font-semibold">Click any feature</span> to explore in detail.
              </motion.p>

              {/* CTA */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.7 }}
                className="flex flex-col sm:flex-row items-center justify-center gap-4"
              >
                <Link to="/register">
                  <Button className="w-full sm:w-auto h-14 px-8 bg-gradient-to-r from-primary to-accent-purple text-white rounded-xl font-heading font-bold text-lg shadow-xl hover:shadow-2xl transition-all">
                    <Rocket className="w-5 h-5 mr-2" />
                    Get Started Free
                  </Button>
                </Link>
                <Link to="/practice">
                  <Button variant="outline" className="w-full sm:w-auto h-14 px-8 border-2 border-border-color text-foreground rounded-xl font-heading font-bold text-lg hover:border-primary/50 transition-all">
                    <Play className="w-5 h-5 mr-2" />
                    Try Demo
                  </Button>
                </Link>
              </motion.div>

              {/* Stats */}
              <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.9 }}
                className="grid grid-cols-2 sm:flex sm:items-center sm:justify-center gap-4 sm:gap-8 lg:gap-16 mt-16"
              >
                {[
                  { value: '10', label: 'AI Features' },
                  { value: '3', label: 'Modalities' },
                  { value: '96%', label: 'Accuracy' },
                  { value: '< 50ms', label: 'Latency' },
                ].map((stat, i) => (
                  <div key={i} className="text-center">
                    <div className="font-heading text-3xl lg:text-4xl font-black text-primary">{stat.value}</div>
                    <div className="font-paragraph text-sm text-foreground-muted">{stat.label}</div>
                  </div>
                ))}
              </motion.div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* ==========================================
          CORE FEATURES - Clickable Cards with 3D
          ========================================== */}
      <section className="w-full py-16 lg:py-32 px-6 lg:px-12">
        <div className="max-w-[100rem] mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-12 lg:mb-20"
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 rounded-full mb-6">
              <Sparkles className="w-4 h-4 text-primary" />
              <span className="text-sm font-paragraph text-primary font-semibold">Interactive Features</span>
            </div>
            <h2 className="font-heading text-3xl sm:text-5xl lg:text-7xl font-black text-foreground mb-6">
              Core <span className="text-primary">Capabilities</span>
            </h2>
            <p className="font-paragraph text-xl text-foreground-muted max-w-3xl mx-auto">
              Six pillars of comprehensive interview preparation. <span className="text-primary font-semibold">Click any card</span> to explore detailed information.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {CORE_FEATURES.map((feature, index) => (
              <FeatureCard
                key={feature.id}
                feature={feature}
                index={index}
                onClick={() => setSelectedFeature(feature)}
              />
            ))}
          </div>
        </div>
      </section>

      {/* ==========================================
          ADDITIONAL FEATURES
          ========================================== */}
      <section className="w-full py-16 lg:py-32 px-6 lg:px-12 bg-background-light">
        <div className="max-w-[100rem] mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-12 lg:mb-20"
          >
            <h2 className="font-heading text-3xl sm:text-5xl lg:text-7xl font-black text-foreground mb-6">
              More <span className="text-primary">Features</span>
            </h2>
            <p className="font-paragraph text-xl text-foreground-muted max-w-3xl mx-auto">
              Additional powerful capabilities to enhance your interview preparation
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {ADDITIONAL_FEATURES.map((feature, index) => (
              <FeatureCard
                key={feature.id}
                feature={feature}
                index={index}
                onClick={() => setSelectedFeature(feature)}
              />
            ))}
          </div>
        </div>
      </section>

      {/* ==========================================
          TECHNICAL DEEP DIVE
          ========================================== */}
      <section className="w-full py-16 lg:py-32 px-6 lg:px-12">
        <div className="max-w-[100rem] mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-12 lg:mb-20"
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 rounded-full mb-6">
              <Terminal className="w-4 h-4 text-primary" />
              <span className="text-sm font-paragraph text-primary font-semibold">Under The Hood</span>
            </div>
            <h2 className="font-heading text-3xl sm:text-5xl lg:text-7xl font-black text-foreground mb-6">
              Technical <span className="text-primary">Deep Dive</span>
            </h2>
            <p className="font-paragraph text-xl text-foreground-muted max-w-3xl mx-auto">
              Comprehensive analysis modules working together to evaluate your performance
            </p>
          </motion.div>

          <div className="grid lg:grid-cols-3 gap-8">
            {TECHNICAL_CAPABILITIES.map((module, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 50 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: index * 0.15 }}
                whileHover={{ y: -10 }}
                className="group"
              >
                <div className="bg-card-bg border border-border-color rounded-2xl p-8 h-full shadow-lg hover:shadow-2xl transition-all duration-300 relative overflow-hidden">
                  {/* Background gradient */}
                  <div className={`absolute inset-0 bg-gradient-to-br ${module.color} opacity-0 group-hover:opacity-5 transition-opacity duration-500`} />

                  <div className="relative z-10">
                    <div className="flex items-center gap-4 mb-6">
                      <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${module.color} flex items-center justify-center shadow-lg`}>
                        <module.icon className="w-7 h-7 text-white" />
                      </div>
                      <h3 className="font-heading text-2xl font-bold text-foreground">{module.category}</h3>
                    </div>

                    <ul className="space-y-3">
                      {module.features.map((feature, idx) => (
                        <motion.li
                          key={idx}
                          initial={{ opacity: 0, x: -10 }}
                          whileInView={{ opacity: 1, x: 0 }}
                          viewport={{ once: true }}
                          transition={{ delay: 0.1 + idx * 0.05 }}
                          className="flex items-start gap-3"
                        >
                          <div className={`w-2 h-2 rounded-full bg-gradient-to-br ${module.color} flex-shrink-0 mt-2`} />
                          <span className="font-paragraph text-sm text-foreground-muted">{feature}</span>
                        </motion.li>
                      ))}
                    </ul>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ==========================================
          BENEFITS SECTION
          ========================================== */}
      <section className="w-full py-16 lg:py-32 px-6 lg:px-12 bg-background-light">
        <div className="max-w-[100rem] mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-12 lg:mb-20"
          >
            <h2 className="font-heading text-3xl sm:text-5xl lg:text-7xl font-black text-foreground mb-6">
              Why <span className="text-primary">InterviewPro</span>
            </h2>
            <p className="font-paragraph text-xl text-foreground-muted max-w-3xl mx-auto">
              Real benefits that make a difference in your career journey
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {BENEFITS.map((benefit, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                whileHover={{ y: -10, scale: 1.02 }}
                className="group"
              >
                <div className="bg-card-bg border border-border-color rounded-2xl p-8 h-full transition-all duration-300 hover:shadow-2xl relative overflow-hidden">
                  <div className={`absolute inset-0 bg-gradient-to-br ${benefit.color} opacity-0 group-hover:opacity-5 transition-opacity duration-500`} />

                  <div className="relative z-10">
                    <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${benefit.color} flex items-center justify-center mb-6 shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                      <benefit.icon className="w-8 h-8 text-white" />
                    </div>
                    <h3 className="font-heading text-xl font-bold text-foreground mb-3">{benefit.title}</h3>
                    <p className="font-paragraph text-foreground-muted">{benefit.description}</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ==========================================
          CTA SECTION
          ========================================== */}
      <section className="w-full py-16 lg:py-32 px-6 lg:px-12 bg-gradient-to-br from-primary via-accent-purple to-primary relative overflow-hidden">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGRlZnM+PHBhdHRlcm4gaWQ9ImdyaWQiIHdpZHRoPSI2MCIgaGVpZ2h0PSI2MCIgcGF0dGVyblVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+PHBhdGggZD0iTSAxMCAwIEwgMCAwIDAgMTAiIGZpbGw9Im5vbmUiIHN0cm9rZT0icmdiYSgyNTUsMjU1LDI1NSwwLjEpIiBzdHJva2Utd2lkdGg9IjEiLz48L3BhdHRlcm4+PC9kZWZzPjxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbGw9InVybCgjZ3JpZCkiLz48L3N2Zz4=')] opacity-30" />

        <div className="max-w-[100rem] mx-auto relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center"
          >
            <h2 className="font-heading text-3xl sm:text-5xl lg:text-7xl font-black text-white mb-8">
              Experience All Features<br />For Free
            </h2>
            <p className="font-paragraph text-xl text-white/80 max-w-2xl mx-auto mb-12">
              Start practicing with our comprehensive AI-powered interview coaching platform today.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link to="/register">
                <Button className="w-full sm:w-auto h-14 px-10 bg-white text-primary rounded-xl font-heading font-bold text-lg shadow-xl hover:shadow-2xl hover:scale-105 transition-all">
                  <Rocket className="w-5 h-5 mr-2" />
                  Get Started Free
                </Button>
              </Link>
              <Link to="/about">
                <Button variant="outline" className="w-full sm:w-auto h-14 px-10 border-2 border-white/30 text-white rounded-xl font-heading font-bold text-lg hover:bg-white/10 transition-all">
                  Learn More
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Feature Detail Modal */}
      <AnimatePresence>
        {selectedFeature && (
          <FeatureDetailModal
            feature={selectedFeature}
            onClose={() => setSelectedFeature(null)}
          />
        )}
      </AnimatePresence>

      <Footer />
    </div>
  );
}
