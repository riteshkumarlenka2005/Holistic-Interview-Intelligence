// HPI 1.7-G
import React, { useRef, useState, useEffect } from 'react';
import { motion, useScroll, useTransform, useSpring, useInView, AnimatePresence } from 'framer-motion';
import { Link } from 'react-router-dom';
import {
  Brain,
  Video,
  TrendingUp,
  Award,
  Users,
  Globe,
  ArrowRight,
  CheckCircle,
  Zap,
  Target,
  MessageSquare,
  Play,
  Activity,
  Mic,
  Eye,
  BarChart3
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Image } from '@/components/ui/image';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import IntelligenceInterlude from '@/components/IntelligenceInterlude';
import TrustedCompanies from '@/components/TrustedCompanies';
import FAQSection from '@/components/FAQSection';
import TestimonialsMarquee from '@/components/TestimonialsMarquee';
import LivePracticePreview from '@/components/LivePracticePreview';

// --- CANONICAL DATA SOURCES (PRESERVED) ---

const features = [
  {
    icon: Video,
    title: 'AI-Powered Practice',
    description: 'Record practice interviews with real-time feedback on verbal and non-verbal communication'
  },
  {
    icon: Brain,
    title: 'Multimodal Analysis',
    description: 'Advanced AI evaluates speech patterns, facial expressions, body language, and engagement'
  },
  {
    icon: TrendingUp,
    title: 'Progress Tracking',
    description: 'Monitor your improvement over time with detailed analytics and skill-wise metrics'
  },
  {
    icon: Award,
    title: 'Personalized Feedback',
    description: 'Get actionable insights tailored to your skill level, role, and interview type'
  },
  {
    icon: MessageSquare,
    title: 'Explainable AI',
    description: 'Understand exactly why you received each score with transparent, behavior-driven explanations'
  },
  {
    icon: Users,
    title: 'Accessible to All',
    description: 'Democratizing career readiness tools for students from all backgrounds'
  }
];

const howItWorks = [
  {
    step: '01',
    title: 'Set Your Goals',
    description: 'Choose your interview type, skill level, and career objectives to personalize your experience',
    detail: 'Configure the AI to simulate HR screenings, technical deep-dives, or behavioral assessments tailored to your target role.'
  },
  {
    step: '02',
    title: 'Practice & Record',
    description: 'Answer interview questions while our AI analyzes your verbal and non-verbal communication in real-time',
    detail: 'Our secure environment captures micro-expressions, tone variations, and speech clarity without storing sensitive biometric data.'
  },
  {
    step: '03',
    title: 'Learn & Improve',
    description: 'Review detailed feedback, track progress, and access targeted resources to enhance your skills',
    detail: 'Receive a comprehensive breakdown of your performance with actionable drills to improve specific weaknesses.'
  }
];

const testimonials = [
  {
    name: 'Sarah Chen',
    role: 'Computer Science Graduate',
    content: 'This platform transformed my interview confidence. The AI feedback helped me identify and fix nervous habits I never knew I had.',
    score: 'Improved readiness score from 62% to 89%'
  },
  {
    name: 'Marcus Johnson',
    role: 'First-Generation College Student',
    content: 'As someone without access to career coaching, this platform leveled the playing field. The personalized feedback is invaluable.',
    score: 'Landed dream job after 3 weeks of practice'
  },
  {
    name: 'Priya Sharma',
    role: 'MBA Candidate',
    content: 'The multimodal analysis caught subtle communication issues I would have never noticed. Game-changer for behavioral interviews.',
    score: 'Increased eye contact by 45%'
  }
];

// --- UTILITY COMPONENTS ---

const SectionLabel = ({ number, text }: { number: string; text: string }) => (
  <div className="flex items-center gap-4 mb-8">
    <span className="font-paragraph text-primary text-sm tracking-widest border border-primary/30 px-2 py-1 rounded">
      {number}
    </span>
    <div className="h-px w-12 bg-primary/30" />
    <span className="font-paragraph text-foreground/60 text-sm uppercase tracking-widest">
      {text}
    </span>
  </div>
);

const GridBackground = () => (
  <div className="absolute inset-0 pointer-events-none z-0 overflow-hidden">
    <div
      className="absolute inset-0 opacity-[0.02]"
      style={{
        backgroundImage: `linear-gradient(to right, #6C5CE7 1px, transparent 1px), linear-gradient(to bottom, #6C5CE7 1px, transparent 1px)`,
        backgroundSize: '4rem 4rem'
      }}
    />
    <div className="absolute inset-0 bg-gradient-to-b from-background via-transparent to-background" />
  </div>
);

// --- SECTIONS ---

const HeroSection = () => {
  const { scrollY } = useScroll();
  const y1 = useTransform(scrollY, [0, 500], [0, 100]);
  const y2 = useTransform(scrollY, [0, 500], [0, -80]);
  const opacity = useTransform(scrollY, [0, 400], [1, 0]);
  const scale = useTransform(scrollY, [0, 300], [1, 0.95]);

  return (
    <section className="relative w-full min-h-screen flex items-center justify-center overflow-hidden">
      {/* Premium Background Image with Overlay - More visible */}
      <div className="absolute inset-0 z-0">
        <img
          src="https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=2000&q=80"
          alt="Modern office background"
          className="w-full h-full object-cover"
        />
        {/* Lighter overlay to make background more visible */}
        <div className="absolute inset-0 bg-gradient-to-br from-background/70 via-background/50 to-background/30" />
        <div className="absolute inset-0 bg-gradient-to-t from-background/80 via-transparent to-background/40" />
      </div>

      {/* Animated Mesh Gradient Background */}
      <div className="absolute inset-0 z-[1] overflow-hidden">
        <motion.div
          className="absolute top-[-30%] left-[-20%] w-[80vw] h-[80vw] rounded-full opacity-30"
          style={{
            background: 'radial-gradient(circle, rgba(108,92,231,0.4) 0%, transparent 70%)',
            filter: 'blur(80px)',
          }}
          animate={{
            x: [0, 50, 0],
            y: [0, 30, 0],
            scale: [1, 1.1, 1],
          }}
          transition={{ duration: 15, repeat: Infinity, ease: "easeInOut" }}
        />
        <motion.div
          className="absolute bottom-[-30%] right-[-20%] w-[70vw] h-[70vw] rounded-full opacity-25"
          style={{
            background: 'radial-gradient(circle, rgba(0,206,201,0.3) 0%, transparent 70%)',
            filter: 'blur(80px)',
          }}
          animate={{
            x: [0, -40, 0],
            y: [0, -40, 0],
            scale: [1, 1.15, 1],
          }}
          transition={{ duration: 18, repeat: Infinity, ease: "easeInOut" }}
        />
        <motion.div
          className="absolute top-[20%] right-[10%] w-[40vw] h-[40vw] rounded-full opacity-20"
          style={{
            background: 'radial-gradient(circle, rgba(253,121,168,0.3) 0%, transparent 70%)',
            filter: 'blur(60px)',
          }}
          animate={{
            x: [0, 30, 0],
            y: [0, -20, 0],
          }}
          transition={{ duration: 12, repeat: Infinity, ease: "easeInOut" }}
        />
      </div>

      {/* Floating Particles Effect */}
      <div className="absolute inset-0 z-[2] pointer-events-none overflow-hidden">
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 bg-primary/40 rounded-full"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              y: [-20, 20, -20],
              x: [-10, 10, -10],
              opacity: [0.2, 0.6, 0.2],
            }}
            transition={{
              duration: 4 + Math.random() * 4,
              repeat: Infinity,
              delay: Math.random() * 2,
              ease: "easeInOut",
            }}
          />
        ))}
      </div>

      {/* Grid Pattern Overlay */}
      <div className="absolute inset-0 z-[3] pointer-events-none opacity-[0.03]"
        style={{
          backgroundImage: `linear-gradient(rgba(108,92,231,0.5) 1px, transparent 1px), linear-gradient(90deg, rgba(108,92,231,0.5) 1px, transparent 1px)`,
          backgroundSize: '60px 60px',
        }}
      />

      {/* Main Content Container */}
      <div className="container relative z-10 px-6 lg:px-12 xl:px-20 w-full max-w-[140rem] mx-auto pt-24 lg:pt-32 pb-16">
        <div className="grid lg:grid-cols-12 gap-8 lg:gap-16 items-center">

          {/* Left Content - Enhanced Typography & CTAs */}
          <motion.div
            className="lg:col-span-6 space-y-8"
            initial={{ opacity: 0, x: -60 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 1, ease: [0.25, 0.46, 0.45, 0.94] }}
          >
            {/* Premium Badge */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="inline-flex items-center gap-3 px-5 py-2.5 bg-gradient-to-r from-primary/20 to-accent-purple/20 border border-primary/30 rounded-full backdrop-blur-xl shadow-lg shadow-primary/10"
            >
              <div className="relative">
                <div className="w-2.5 h-2.5 bg-primary rounded-full animate-pulse" />
                <div className="absolute inset-0 w-2.5 h-2.5 bg-primary rounded-full animate-ping" />
              </div>
              <span className="font-paragraph text-sm text-primary font-semibold tracking-wide">
                🚀 AI-Powered Interview Mastery
              </span>
            </motion.div>

            {/* Main Headline with Gradient */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.8 }}
            >
              <h1 className="font-heading text-4xl sm:text-5xl md:text-6xl lg:text-7xl xl:text-8xl font-black leading-[0.9] tracking-tight">
                <span className="text-foreground">ACE YOUR</span>
                <br />
                <span className="bg-gradient-to-r from-primary via-accent-purple to-primary bg-clip-text text-transparent bg-[length:200%_auto] animate-gradient">
                  INTERVIEW
                </span>
                <br />
                <span className="text-foreground/80">WITH AI</span>
              </h1>
            </motion.div>

            {/* Subheadline with Premium Styling */}
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="font-paragraph text-lg lg:text-xl text-foreground/80 max-w-xl leading-relaxed"
            >
              Transform your interview skills with{' '}
              <span className="text-primary font-semibold">real-time AI feedback</span>,{' '}
              personalized coaching, and comprehensive analytics. Join{' '}
              <span className="text-primary font-semibold">50,000+ professionals</span>{' '}
              who landed their dream jobs.
            </motion.p>

            {/* Premium CTA Buttons */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
              className="flex flex-col sm:flex-row gap-4 pt-4"
            >
              <Link to="/practice">
                <Button className="group relative w-full sm:w-auto h-14 px-8 bg-gradient-to-r from-primary to-accent-purple text-white font-heading font-bold text-base rounded-xl shadow-xl shadow-primary/25 hover:shadow-2xl hover:shadow-primary/40 hover:scale-[1.02] transition-all duration-300 overflow-hidden">
                  <span className="relative z-10 flex items-center gap-2">
                    Start Free Practice
                    <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                  </span>
                  <div className="absolute inset-0 bg-gradient-to-r from-accent-purple to-primary opacity-0 group-hover:opacity-100 transition-opacity" />
                </Button>
              </Link>
              <Link to="/demo">
                <Button variant="outline" className="group w-full sm:w-auto h-14 px-8 border-2 border-foreground/20 text-foreground hover:border-primary hover:text-primary font-heading font-bold text-base rounded-xl backdrop-blur-sm transition-all duration-300">
                  <Play className="w-5 h-5 mr-2 group-hover:scale-110 transition-transform" />
                  Try Demo Interview
                </Button>
              </Link>
            </motion.div>

            {/* Trust Indicators */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.7 }}
              className="flex flex-wrap items-center gap-6 pt-8"
            >
              {/* Star Rating */}
              <div className="flex items-center gap-2">
                <div className="flex">
                  {[...Array(5)].map((_, i) => (
                    <Award key={i} className="w-5 h-5 text-yellow-500 fill-yellow-500" />
                  ))}
                </div>
                <span className="font-paragraph text-sm text-foreground/70">4.9/5 Rating</span>
              </div>
              <div className="w-px h-8 bg-foreground/10" />
              {/* User Avatars Stack */}
              <div className="flex items-center gap-3">
                <div className="flex -space-x-3">
                  {[1, 2, 3, 4].map((i) => (
                    <div
                      key={i}
                      className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-accent-purple border-2 border-background flex items-center justify-center text-white text-xs font-bold"
                    >
                      {String.fromCharCode(64 + i)}
                    </div>
                  ))}
                  <div className="w-10 h-10 rounded-full bg-secondary border-2 border-background flex items-center justify-center text-foreground-muted text-xs font-bold">
                    +50K
                  </div>
                </div>
                <span className="font-paragraph text-sm text-foreground/70">Happy Users</span>
              </div>
            </motion.div>
          </motion.div>

          {/* Right Content - Video with Premium Frame */}
          <motion.div
            className="lg:col-span-6 relative"
            style={{ y: y2, scale }}
            initial={{ opacity: 0, x: 60 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 1, delay: 0.3, ease: [0.25, 0.46, 0.45, 0.94] }}
          >
            {/* Main Video Container with Premium Frame */}
            <div className="relative h-[450px] lg:h-[550px] w-full">
              {/* Decorative Ring */}
              <div className="absolute -inset-4 rounded-3xl bg-gradient-to-br from-primary/20 via-transparent to-accent-purple/20 blur-xl" />

              {/* Video Frame */}
              <div className="relative w-full h-full rounded-3xl overflow-hidden shadow-2xl shadow-black/20 border-2 border-white/10 bg-background">
                {/* Decorative Corner Accents */}
                <div className="absolute top-0 left-0 w-20 h-20 border-l-4 border-t-4 border-primary rounded-tl-3xl" />
                <div className="absolute top-0 right-0 w-20 h-20 border-r-4 border-t-4 border-accent-purple rounded-tr-3xl" />
                <div className="absolute bottom-0 left-0 w-20 h-20 border-l-4 border-b-4 border-accent-purple rounded-bl-3xl" />
                <div className="absolute bottom-0 right-0 w-20 h-20 border-r-4 border-b-4 border-primary rounded-br-3xl" />

                {/* YouTube Embedded Video - Mock Interview */}
                <iframe
                  src="https://www.youtube.com/embed/HG68Ymazo18?autoplay=1&mute=1&loop=1&playlist=HG68Ymazo18&controls=0&showinfo=0&rel=0&modestbranding=1"
                  title="Online Interview Practice"
                  className="w-full h-full absolute inset-0"
                  style={{ border: 'none' }}
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                />

                {/* Subtle overlay gradient */}
                <div className="absolute inset-0 bg-gradient-to-t from-background/40 via-transparent to-transparent pointer-events-none" />

                {/* Live recording indicator - Premium Style */}
                <div className="absolute top-5 left-5 flex items-center gap-2 px-4 py-2 bg-red-600 backdrop-blur-sm rounded-full z-10 shadow-lg shadow-red-600/30">
                  <div className="relative">
                    <div className="w-2.5 h-2.5 bg-white rounded-full animate-pulse" />
                    <div className="absolute inset-0 w-2.5 h-2.5 bg-white rounded-full animate-ping" />
                  </div>
                  <span className="text-xs font-bold text-white uppercase tracking-wider">LIVE SESSION</span>
                </div>

                {/* Interview label - Premium Style */}
                <div className="absolute bottom-5 right-5 flex items-center gap-2 px-4 py-2 bg-background/90 backdrop-blur-xl rounded-full border border-border-color z-10 shadow-lg">
                  <Video className="w-4 h-4 text-primary" />
                  <span className="text-sm font-paragraph font-semibold text-foreground">AI Mock Interview</span>
                </div>


              </div>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Bottom Scroll Indicator */}
      <motion.div
        className="absolute bottom-8 left-1/2 transform -translate-x-1/2 z-10"
        animate={{ y: [0, 10, 0] }}
        transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
      >
        <div className="flex flex-col items-center gap-2 text-foreground/50">
          <span className="text-xs font-paragraph uppercase tracking-widest">Scroll to Explore</span>
          <div className="w-6 h-10 rounded-full border-2 border-foreground/30 flex items-start justify-center p-2">
            <motion.div
              className="w-1.5 h-1.5 bg-primary rounded-full"
              animate={{ y: [0, 16, 0] }}
              transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
            />
          </div>
        </div>
      </motion.div>
    </section>
  );
};

const StickyProcessSection = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end end"]
  });

  const [activeStep, setActiveStep] = useState(0);

  useEffect(() => {
    const unsubscribe = scrollYProgress.on("change", (latest) => {
      if (latest < 0.3) setActiveStep(0);
      else if (latest < 0.7) setActiveStep(1);
      else setActiveStep(2);
    });
    return () => unsubscribe();
  }, [scrollYProgress]);

  return (
    <section ref={containerRef} className="relative h-[200vh] lg:h-[300vh] bg-background-light">
      <div className="sticky top-0 h-screen w-full overflow-hidden">
        <GridBackground />
        <div className="absolute inset-0 flex flex-col lg:flex-row h-full max-w-[120rem] mx-auto">

          {/* Left Side: Static Title & Context */}
          <div className="w-full lg:w-1/2 h-1/3 lg:h-full flex flex-col justify-center px-6 lg:px-12 z-10 bg-background-light/80 lg:bg-transparent backdrop-blur-sm lg:backdrop-blur-none border-b lg:border-b-0 lg:border-r border-border-color">
            <SectionLabel number="02" text="Workflow" />
            <h2
              className="font-heading text-4xl lg:text-6xl font-black mb-6"
            >
              HOW IT <span className="text-primary">WORKS</span>
            </h2>
            <p className="font-paragraph text-foreground font-semibold max-w-md mb-8">
              A seamless three-step process designed to transform your communication skills through data-driven intelligence.
            </p>

            {/* Progress Indicator */}
            <div className="flex items-center gap-4">
              <div className="font-heading text-6xl font-bold text-foreground/10 relative">
                0{activeStep + 1}
                <motion.span
                  className="absolute inset-0 text-primary overflow-hidden"
                  initial={{ height: "0%" }}
                  animate={{ height: "100%" }}
                  key={activeStep}
                  transition={{ duration: 0.5 }}
                >
                  0{activeStep + 1}
                </motion.span>
              </div>
              <div className="h-px flex-1 bg-border-color relative">
                <motion.div
                  className="absolute left-0 top-0 h-full bg-primary"
                  style={{ width: useTransform(scrollYProgress, [0, 1], ["0%", "100%"]) }}
                />
              </div>
            </div>
          </div>

          {/* Right Side: Dynamic Content */}
          <div className="w-full lg:w-1/2 h-2/3 lg:h-full relative flex items-center justify-center p-6 lg:p-12">
            <AnimatePresence mode="wait">
              <motion.div
                key={activeStep}
                initial={{ opacity: 0, x: 50, filter: "blur(10px)" }}
                animate={{ opacity: 1, x: 0, filter: "blur(0px)" }}
                exit={{ opacity: 0, x: -50, filter: "blur(10px)" }}
                transition={{ duration: 0.5, ease: "circOut" }}
                className="w-full max-w-lg"
              >
                <div className="bg-card-bg border border-border-color p-8 lg:p-12 rounded-2xl shadow-sm relative overflow-hidden group">
                  <div className="absolute top-0 right-0 w-32 h-32 bg-primary-lighter/20 rounded-full blur-3xl group-hover:bg-primary-lighter/30 transition-all duration-500" />

                  <div className="relative z-10">
                    <div className="w-12 h-12 bg-secondary rounded-lg flex items-center justify-center mb-6 text-primary">
                      {activeStep === 0 && <Target size={24} />}
                      {activeStep === 1 && <Video size={24} />}
                      {activeStep === 2 && <TrendingUp size={24} />}
                    </div>
                    <h3 className="font-heading text-3xl font-bold mb-4 text-foreground">
                      {howItWorks[activeStep].title}
                    </h3>
                    <p className="font-paragraph text-lg text-foreground-muted mb-6">
                      {howItWorks[activeStep].description}
                    </p>
                    <div className="p-4 bg-secondary rounded border-l-4 border-primary">
                      <p className="font-paragraph text-sm text-foreground-muted">
                        {howItWorks[activeStep].detail}
                      </p>
                    </div>
                  </div>
                </div>
              </motion.div>
            </AnimatePresence>
          </div>
        </div>
      </div>
    </section>
  );
};

const FeaturesGrid = () => {
  return (
    <section className="py-16 lg:py-32 px-6 lg:px-12 relative bg-background overflow-hidden">
      <div className="max-w-[120rem] mx-auto">
        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-end mb-10 lg:mb-20 gap-4 lg:gap-8">
          <div>
            <SectionLabel number="03" text="Capabilities" />
            <h2
              className="font-heading text-4xl lg:text-6xl font-black max-w-2xl"
            >
              POWERFUL <span className="text-primary">FEATURES</span>
            </h2>
          </div>
          <p className="font-paragraph text-foreground font-semibold max-w-md text-right lg:text-left">
            Comprehensive tools designed to help you master every aspect of interview preparation.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-50px" }}
              transition={{ delay: index * 0.1, duration: 0.5 }}
              className="group relative h-full"
            >
              <div className="absolute inset-0 bg-gradient-to-br from-primary-lighter/10 to-accent-light/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 blur-xl rounded-2xl" />
              <div className="relative h-full bg-card-bg border border-border-color p-8 hover:border-primary-lighter transition-colors duration-300 flex flex-col rounded-2xl shadow-sm hover:shadow-md">
                <div className="mb-6 w-12 h-12 bg-secondary rounded-lg flex items-center justify-center group-hover:bg-primary group-hover:text-white transition-all duration-300">
                  <feature.icon size={24} className="text-primary group-hover:text-white" />
                </div>
                <h3 className="font-heading text-xl font-bold mb-3 text-foreground group-hover:text-primary transition-colors">
                  {feature.title}
                </h3>
                <p className="font-paragraph text-sm text-foreground-muted leading-relaxed flex-grow">
                  {feature.description}
                </p>

                <div className="mt-6 pt-6 border-t border-border-color flex items-center justify-between opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                  <span className="font-paragraph text-xs text-primary font-semibold">LEARN MORE</span>
                  <ArrowRight size={14} className="text-primary" />
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

const ImpactSection = () => {
  const ref = useRef(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"]
  });
  const y = useTransform(scrollYProgress, [0, 1], ["-20%", "20%"]);

  return (
    <section ref={ref} className="relative w-full min-h-[80vh] py-16 lg:py-0 overflow-hidden flex items-center justify-center">
      <motion.div
        className="absolute inset-0 w-full h-[120%] -top-[10%]"
        style={{ y }}
      >
        <Image
          src="https://static.wixstatic.com/media/0f4bf0_0a07e3c629b6432796e1cc408b4a7119~mv2.png?originWidth=1280&originHeight=448"
          alt="Global Impact Background"
          className="w-full h-full object-cover opacity-20 grayscale"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-background via-background/80 to-background" />
      </motion.div>

      <div className="relative z-10 container px-6 text-center max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-secondary border border-border-color rounded-full mb-8 backdrop-blur-md">
            <Globe className="w-4 h-4 text-primary" />
            <span className="text-sm font-paragraph text-foreground">Accessible Education for All</span>
          </div>

          <h2
            className="font-heading text-3xl sm:text-5xl lg:text-7xl font-black mb-8 leading-tight text-foreground"
          >
            DEMOCRATIZING <br />
            <span className="text-primary">OPPORTUNITY</span>
          </h2>

          <p className="font-paragraph text-xl text-foreground font-semibold mb-12 leading-relaxed">
            We believe career readiness is a fundamental right. Our platform bridges the gap for students everywhere through accessible, AI-driven coaching.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-left">
            {[
              { title: "Inclusive Access", desc: "Free tier for students from underserved communities." },
              { title: "Culturally Aware", desc: "AI trained to respect diverse communication styles." },
              { title: "Lifelong Learning", desc: "Continuous skill development for every career stage." }
            ].map((item, i) => (
              <div key={i} className="bg-card-bg border border-border-color p-6 rounded-xl shadow-sm">
                <CheckCircle className="text-primary mb-4" size={24} />
                <h4 className="font-heading text-lg font-bold mb-2 text-foreground">{item.title}</h4>
                <p className="font-paragraph text-sm text-foreground-muted">{item.desc}</p>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
};

const TestimonialSection = () => {
  return (
    <section className="py-16 lg:py-32 px-6 lg:px-12 bg-background-light relative">
      <div className="max-w-[120rem] mx-auto">
        <SectionLabel number="04" text="Validation" />
        <h2
          className="font-heading text-4xl lg:text-6xl font-black mb-16"
        >
          STUDENT <span className="text-primary">SUCCESS</span>
        </h2>

        <div className="grid md:grid-cols-3 gap-8">
          {testimonials.map((t, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.2 }}
              className="bg-card-bg border border-border-color p-8 rounded-2xl relative shadow-sm hover:shadow-md transition-shadow"
            >
              <div className="absolute -top-4 -left-4 text-6xl font-heading text-primary/15">"</div>
              <p className="font-paragraph text-lg text-foreground mb-8 relative z-10 italic">
                {t.content}
              </p>

              <div className="flex items-end justify-between border-t border-border-color pt-6">
                <div>
                  <div className="font-heading font-bold text-foreground">{t.name}</div>
                  <div className="font-paragraph text-xs text-primary mt-1">{t.role}</div>
                </div>
              </div>

              <div className="mt-4 bg-secondary p-3 rounded border border-border-color">
                <div className="flex items-center gap-2 text-primary font-bold font-paragraph text-xs">
                  <TrendingUp size={14} />
                  {t.score}
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

const CTASection = () => {
  return (
    <section className="py-16 lg:py-32 px-6 lg:px-12 relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-b from-background to-primary-lighter/5" />
      <GridBackground />

      <div className="max-w-5xl mx-auto relative z-10 text-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="bg-card-bg border border-border-color p-6 sm:p-12 lg:p-24 rounded-3xl shadow-sm"
        >
          <h2
            className="font-heading text-3xl sm:text-5xl lg:text-7xl font-black mb-8 text-foreground"
          >
            READY TO <span className="text-primary">SUCCEED?</span>
          </h2>
          <p className="font-paragraph text-xl text-foreground font-semibold mb-12 max-w-2xl mx-auto">
            Join thousands of students who are mastering their interviews with AI-powered feedback. Start your free practice session today.
          </p>

          <div className="flex flex-col sm:flex-row justify-center gap-6">
            <Link to="/register">
              <Button className="w-full sm:w-auto h-14 px-10 bg-primary text-white hover:bg-accent-purple font-heading font-bold text-base rounded-lg shadow-sm hover:shadow-md transition-all">
                Start Free Trial
                <ArrowRight className="ml-2 w-4 h-4" />
              </Button>
            </Link>
            <Link to="/about">
              <Button variant="outline" className="w-full sm:w-auto h-14 px-10 border-border-color text-foreground hover:bg-secondary font-heading font-bold text-base rounded-lg">
                Learn More
              </Button>
            </Link>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

// Interview Questions Section
const interviewQuestions = [
  {
    question: "Tell me about yourself",
    tip: "Decide in advance which of your skills and career highlights best fit the role",
    answer: "Share those as a personal and interesting story, showing how you got started, where you are now, and how this role is the next logical chapter"
  },
  {
    question: "What interests you about this position?",
    tip: "Research the company and position beforehand to find specific things you like around mission, culture, customers, and the role",
    answer: "Get specific about the impact you want to have and how your skills fit well"
  },
  {
    question: "What are your strengths?",
    tip: "Decide ahead of time which of your strengths best match the requirements of the role",
    answer: "Highlight just 2 to 3 and back them up with memorable stories of times you shined"
  },
  {
    question: "Tell me about a time you failed. How did you deal with that situation?",
    tip: "Demonstrate that you are humble, resilient, and growth-oriented",
    answer: "Tell a story of a setback that you quickly recovered and learned from - and then moved forward"
  },
  {
    question: "Describe a time you motivated others. How did you accomplish it?",
    tip: "Even if you are not in leadership, they want to see leadership here - tailoring your approach to the situation and personalities involved",
    answer: "Highlight a time when you were positive, persistent, and persuasive"
  },
  {
    question: "Tell me a time you had to handle multiple projects at once. How did it go?",
    tip: "Focus on your time management and reliability",
    answer: "Share an example where you used a repeatable system - prioritized in a smart way, delegated, blocked time, gave frequent updates"
  },
  {
    question: "Describe a time you went through a major change at work. How did you adapt?",
    tip: "Employers are looking for people who are excited about change, not just tolerant of it",
    answer: "Tell a story about a big change that impacted you directly and that you adjusted to quickly; bonus if you got others on board"
  },
  {
    question: "Tell me about a time you set a goal for yourself. How did you ensure you achieved it?",
    tip: "Show you can Get Things Done. That you set clear goals and follow through",
    answer: "Pick an example where you succeeded in a replicable way - broke the goal into small steps, made progress each day, showed grit through challenges"
  },
  {
    question: "What are your weaknesses?",
    tip: "Don't use 'I care too much' or other clichés - this is about self-awareness",
    answer: "Describe 1 to 2 that aren't critical to the role, and note the ways you've been working on them"
  },
  {
    question: "Any questions for me?",
    tip: "The only question almost guaranteed to be asked - don't sleep on this",
    answer: "Ask questions that show you've researched the company or are focused on success (ex: What would success look like in the first 6 months of this role?)"
  }
];

const InterviewQuestionsSection = () => {
  return (
    <section className="py-12 lg:py-24 px-6 lg:px-12 relative">
      <GridBackground />
      <div className="max-w-[120rem] mx-auto relative z-10">
        {/* Header with Image */}
        <div className="grid lg:grid-cols-2 gap-12 items-center mb-16">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <SectionLabel number="05" text="Preparation Guide" />
            <h2
              className="font-heading text-4xl lg:text-6xl font-black text-foreground mb-6"
            >
              Common Interview <span className="text-primary">Questions</span>
            </h2>
            <p className="font-paragraph text-lg text-foreground font-semibold">
              Master these essential interview questions with expert tips and proven answer strategies. Being well-prepared with thoughtful responses will help you stand out from other candidates.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="relative flex justify-center"
          >
            {/* Interview Line Art Illustration */}
            <svg viewBox="0 0 500 300" className="w-full max-w-md" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              {/* Desk */}
              <line x1="50" y1="250" x2="450" y2="250" className="stroke-foreground/30" />

              {/* Interviewer (left) */}
              <g className="stroke-foreground">
                {/* Head */}
                <circle cx="130" cy="120" r="30" />
                {/* Glasses */}
                <circle cx="120" cy="115" r="8" />
                <circle cx="140" cy="115" r="8" />
                <line x1="128" y1="115" x2="132" y2="115" />
                {/* Hair */}
                <path d="M100 105 Q110 75 130 80 Q150 75 160 105" />
                {/* Body/Suit */}
                <path d="M100 150 L80 250" />
                <path d="M160 150 L180 250" />
                <path d="M100 150 Q130 170 160 150" />
                {/* Tie */}
                <path d="M130 150 L125 200 L130 210 L135 200 L130 150" />
                {/* Arms */}
                <path d="M100 180 Q80 200 90 230 L100 240" />
                <path d="M160 180 Q180 200 170 230 L160 240" />
              </g>

              {/* Candidate (right) */}
              <g className="stroke-foreground">
                {/* Head */}
                <circle cx="370" cy="120" r="28" />
                {/* Hair */}
                <path d="M342 110 Q350 80 370 85 Q395 80 400 120" />
                <path d="M398 110 Q405 140 395 160" />
                {/* Body */}
                <path d="M342 148 L320 250" />
                <path d="M398 148 L420 250" />
                <path d="M342 148 Q370 168 398 148" />
                {/* Arms - gesturing */}
                <path d="M342 180 Q310 170 290 150 L280 145" />
                <path d="M285 140 L280 145 L290 148" />
                <path d="M398 180 Q430 190 420 240" />
                {/* Paper in hand */}
                <rect x="405" y="220" width="30" height="40" rx="2" />
                <line x1="410" y1="230" x2="430" y2="230" />
                <line x1="410" y1="240" x2="425" y2="240" />
              </g>
            </svg>
          </motion.div>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {interviewQuestions.map((item, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.05 }}
              className="bg-card-bg border border-border-color rounded-xl p-6 hover:shadow-md transition-shadow"
            >
              <h3 className="font-heading text-lg font-bold text-foreground mb-4 flex items-start gap-3">
                <span className="bg-primary text-white text-xs px-2 py-1 rounded-full flex-shrink-0">
                  Q{index + 1}
                </span>
                {item.question}
              </h3>

              <div className="space-y-3">
                <div className="bg-primary/5 border-l-4 border-primary p-4 rounded-r-lg">
                  <div className="flex items-center gap-2 mb-1">
                    <Zap className="w-4 h-4 text-primary" />
                    <span className="font-heading text-xs font-bold text-primary uppercase">Tip</span>
                  </div>
                  <p className="font-paragraph text-sm text-foreground-muted">{item.tip}</p>
                </div>

                <div className="bg-secondary/50 p-4 rounded-lg">
                  <div className="flex items-center gap-2 mb-1">
                    <CheckCircle className="w-4 h-4 text-green-600" />
                    <span className="font-heading text-xs font-bold text-green-600 uppercase">Answer Strategy</span>
                  </div>
                  <p className="font-paragraph text-sm text-foreground">{item.answer}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

// Interview Tips Section (Do's and Don'ts)
const interviewDos = [
  {
    title: "Listen Actively",
    description: "Listen carefully to what the interviewer has to say. Pay attention to both verbal and non-verbal cues."
  },
  {
    title: "Research the Company",
    description: "Know the company's mission, values, recent news, and the role you're applying for inside out."
  },
  {
    title: "Take Notes",
    description: "Taking notes helps you concentrate and process the information better. It also shows you're engaged."
  },
  {
    title: "Be Prepared",
    description: "Read the job description beforehand and write down what you want to address during the interview."
  },
  {
    title: "Ask Questions",
    description: "Prepare thoughtful questions that occur to you and make sure to ask them at the appropriate time."
  },
  {
    title: "Follow Up",
    description: "Send a thank-you email within 24 hours, reiterating your interest and key points from the discussion."
  }
];

const interviewDonts = [
  {
    title: "Don't Talk Constantly",
    description: "Constant chatter can be distracting. Keep your answers concise and let the interviewer guide the conversation."
  },
  {
    title: "Don't Be Negative",
    description: "Never badmouth previous employers or colleagues. Keep the conversation positive and professional."
  },
  {
    title: "Don't Check Your Phone",
    description: "Turn your phone off or put it on silent. Looking at your phone is extremely rude during an interview."
  },
  {
    title: "Don't Be Late",
    description: "Being on time shows respect. Arrive 10-15 minutes early to allow for any unexpected delays."
  },
  {
    title: "Don't Interrupt",
    description: "While someone is talking, don't interrupt them. Wait until they have finished before you raise your own points."
  },
  {
    title: "Don't Lie",
    description: "Be honest about your experience and skills. Misrepresentations will likely come back to haunt you."
  }
];

const InterviewTipsSection = () => {
  return (
    <section className="py-24 px-6 lg:px-12 relative bg-gradient-to-b from-secondary/30 to-background">
      <div className="max-w-[120rem] mx-auto relative z-10">
        {/* Header with centered illustration */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <SectionLabel number="06" text="Interview Etiquette" />
          <h2
            className="font-heading text-4xl lg:text-6xl font-black text-foreground mb-6"
          >
            Do's & <span className="text-primary">Don'ts</span>
          </h2>
          <p className="font-paragraph text-lg text-foreground font-semibold max-w-3xl mx-auto mb-12">
            Follow these essential guidelines to make a great impression in your next interview
          </p>

          {/* Interview with microphone illustration */}
          <div className="flex justify-center mb-8">
            <svg viewBox="0 0 500 250" className="w-full max-w-lg" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              {/* Desk line */}
              <path d="M80 220 Q250 230 420 220" className="stroke-foreground/30" />

              {/* Interviewer (left) - holding microphone */}
              <g className="stroke-foreground">
                {/* Head */}
                <circle cx="150" cy="100" r="28" />
                {/* Hair */}
                <path d="M122 90 Q130 60 150 65 Q175 55 178 100" />
                {/* Body */}
                <path d="M122 128 L100 220" />
                <path d="M178 128 L200 220" />
                <path d="M122 128 Q150 150 178 128" />
                {/* Collar detail */}
                <path d="M140 128 L150 145 L160 128" />
                {/* Arm holding microphone */}
                <path d="M178 145 Q220 140 260 130" />
                {/* Microphone */}
                <ellipse cx="275" cy="125" rx="12" ry="18" />
                <rect x="271" y="143" width="8" height="25" rx="2" />
                {/* Other arm */}
                <path d="M122 145 Q90 180 110 210" />
              </g>

              {/* Interviewee (right) */}
              <g className="stroke-foreground">
                {/* Head */}
                <circle cx="370" cy="105" r="26" />
                {/* Hair */}
                <path d="M344 95 Q350 70 370 75 Q400 65 405 105" />
                <path d="M396 95 Q410 120 400 140" />
                {/* Body */}
                <path d="M344 131 L325 220" />
                <path d="M396 131 L415 220" />
                <path d="M344 131 Q370 150 396 131" />
                {/* Arms - relaxed/listening */}
                <path d="M344 150 Q310 180 320 210" />
                <path d="M396 150 Q430 180 420 210" />
              </g>
            </svg>
          </div>
        </motion.div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Do's Column */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="bg-green-50 dark:bg-green-950/20 border border-green-200 dark:border-green-800 rounded-2xl p-8"
          >
            <div className="flex items-center gap-3 mb-8">
              <div className="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center">
                <CheckCircle className="w-6 h-6 text-white" />
              </div>
              <h3 className="font-heading text-2xl font-bold text-green-700 dark:text-green-400">Do</h3>
            </div>

            <div className="space-y-4">
              {interviewDos.map((item, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 10 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.1 }}
                  className="bg-white dark:bg-card-bg border border-green-100 dark:border-green-900 rounded-xl p-4 flex gap-4"
                >
                  <div className="w-8 h-8 bg-green-100 dark:bg-green-900 rounded-lg flex items-center justify-center flex-shrink-0">
                    <CheckCircle className="w-4 h-4 text-green-600" />
                  </div>
                  <div>
                    <h4 className="font-heading font-bold text-foreground mb-1">{item.title}</h4>
                    <p className="font-paragraph text-sm text-foreground-muted">{item.description}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Don'ts Column */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-800 rounded-2xl p-8"
          >
            <div className="flex items-center gap-3 mb-8">
              <div className="w-12 h-12 bg-red-500 rounded-full flex items-center justify-center">
                <Target className="w-6 h-6 text-white" />
              </div>
              <h3 className="font-heading text-2xl font-bold text-red-700 dark:text-red-400">Don't</h3>
            </div>

            <div className="space-y-4">
              {interviewDonts.map((item, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 10 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.1 }}
                  className="bg-white dark:bg-card-bg border border-red-100 dark:border-red-900 rounded-xl p-4 flex gap-4"
                >
                  <div className="w-8 h-8 bg-red-100 dark:bg-red-900 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Target className="w-4 h-4 text-red-600" />
                  </div>
                  <div>
                    <h4 className="font-heading font-bold text-foreground mb-1">{item.title}</h4>
                    <p className="font-paragraph text-sm text-foreground-muted">{item.description}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
};

// How to Introduce Yourself Section
const introductionTips = [
  {
    number: "1",
    title: "Lead With Proof",
    color: "bg-yellow-500",
    points: [
      "Don't say 'I'm a marketer' or 'I run an agency.'",
      "Say what you've actually done.",
      "Example: 'I've helped businesses drive over $2B in ROI.'"
    ],
    takeaway: "Results beat official titles every time."
  },
  {
    number: "2",
    title: "Hit A Pain Point",
    color: "bg-orange-500",
    points: [
      "Open by naming the exact problem your audience struggles with.",
      "'Most companies can't get attention online.'",
      "Position yourself as the one who fixes it."
    ],
    takeaway: "You're selling clarity, not confusion."
  },
  {
    number: "3",
    title: "Use A 10-Word Story",
    color: "bg-pink-500",
    points: [
      "Boil your backstory into one punchy sentence.",
      "'I turned $0 into a multi-million-dollar agency in 5 years.'",
      "Short hits harder than long."
    ],
    takeaway: "If they want more, they'll ask."
  },
  {
    number: "4",
    title: "Body Language",
    color: "bg-purple-500",
    points: [
      "Stand tall, shoulders back, chin up.",
      "Speak slower than feels natural.",
      "Lock eyes, don't scan the room."
    ],
    takeaway: "Your presence says more than your words."
  },
  {
    number: "5",
    title: "End With A Question",
    color: "bg-blue-500",
    points: [
      "Flip the focus back to them immediately.",
      "'What's the biggest growth challenge you're facing right now?'",
      "It makes the conversation about them."
    ],
    takeaway: "And gives you the ammo to respond with value."
  },
  {
    number: "6",
    title: "Borrow Their Language",
    color: "bg-teal-500",
    points: [
      "Mirror the words they use for their industry.",
      "If they say 'clients,' don't say 'customers.'",
      "It shows you get their world."
    ],
    takeaway: "Instant trust, zero translation needed."
  },
  {
    number: "7",
    title: "Show What's Next",
    color: "bg-green-500",
    points: [
      "Don't just say what you do now...",
      "Hint at the bigger mission you're building.",
      "People buy into vision, not just services."
    ],
    takeaway: "It makes you unforgettable."
  },
  {
    number: "8",
    title: "Authority Without Flexing",
    color: "bg-indigo-500",
    points: [
      "Mention one credibility marker. Quickly.",
      "'Worked with Tony Robbins' team' is enough.",
      "Let curiosity do the rest."
    ],
    takeaway: "Silence sells better than bragging."
  }
];

const IntroductionTipsSection = () => {
  return (
    <section className="py-24 px-6 lg:px-12 relative">
      <GridBackground />
      <div className="max-w-[120rem] mx-auto relative z-10">
        {/* Header with side-by-side layout */}
        <div className="grid lg:grid-cols-2 gap-12 items-center mb-16">
          {/* Illustration - Person speaking/presenting */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="relative flex justify-center order-2 lg:order-1"
          >
            <svg viewBox="0 0 300 400" className="w-full max-w-xs" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              {/* Head */}
              <g className="stroke-foreground">
                <ellipse cx="150" cy="100" rx="50" ry="55" />
                {/* Hair */}
                <path d="M100 85 Q110 50 150 55 Q190 50 200 85" />
                <path d="M105 90 Q95 70 110 60" />
                {/* Eyes */}
                <ellipse cx="130" cy="95" rx="8" ry="10" />
                <ellipse cx="170" cy="95" rx="8" ry="10" />
                <circle cx="132" cy="95" r="3" fill="currentColor" />
                <circle cx="172" cy="95" r="3" fill="currentColor" />
                {/* Eyebrows */}
                <path d="M120 80 Q130 75 140 80" />
                <path d="M160 80 Q170 75 180 80" />
                {/* Nose */}
                <path d="M150 100 L148 115 Q150 120 155 118" />
                {/* Smiling mouth */}
                <path d="M135 130 Q150 145 165 130" />
                {/* Ear */}
                <path d="M200 95 Q210 95 210 110 Q210 125 200 120" />
                {/* Earring */}
                <circle cx="202" cy="125" r="3" />
              </g>

              {/* Body */}
              <g className="stroke-foreground">
                {/* Neck */}
                <path d="M135 155 L130 175" />
                <path d="M165 155 L170 175" />
                {/* Shoulders/top */}
                <path d="M80 200 Q100 175 130 175 L170 175 Q200 175 220 200" />
                {/* Body outline */}
                <path d="M80 200 L70 380" />
                <path d="M220 200 L230 380" />
                {/* Collar/neckline */}
                <path d="M130 175 Q150 195 170 175" />
                <circle cx="150" cy="185" r="5" />
              </g>

              {/* Arms */}
              <g className="stroke-foreground">
                {/* Left arm - holding microphone */}
                <path d="M80 200 Q50 240 70 280 L85 290" />
                {/* Microphone */}
                <rect x="70" y="290" width="35" height="25" rx="3" />
                <text x="78" y="307" className="fill-foreground text-[8px] font-bold" stroke="none">MIC</text>
                <rect x="85" y="315" width="5" height="30" />

                {/* Right arm - pointing up */}
                <path d="M220 200 Q250 210 260 180 L270 140" />
                {/* Pointing finger */}
                <path d="M270 140 L275 120" />
                <path d="M268 145 L260 138" />
                <path d="M272 148 L280 145" />
              </g>

              {/* Watch */}
              <ellipse cx="75" cy="275" rx="8" ry="6" className="stroke-foreground" />
            </svg>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="order-1 lg:order-2"
          >
            <SectionLabel number="07" text="First Impressions" />
            <h2
              className="font-heading text-4xl lg:text-6xl font-black text-foreground mb-6"
            >
              How To <span className="text-primary">Introduce Yourself</span>
            </h2>
            <p className="font-paragraph text-lg text-foreground font-semibold">
              Make your introductions unforgettable with these proven techniques. Your first impression sets the tone for the entire conversation - make it count with confidence, clarity, and authenticity.
            </p>
          </motion.div>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {introductionTips.map((tip, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.05 }}
              className="bg-card-bg border border-border-color rounded-xl overflow-hidden hover:shadow-lg transition-shadow"
            >
              <div className={`${tip.color} px-4 py-3 flex items-center gap-3`}>
                <span className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center text-white font-bold">
                  {tip.number}
                </span>
                <h3 className="font-heading font-bold text-white">{tip.title}</h3>
              </div>

              <div className="p-5">
                <ul className="space-y-2 mb-4">
                  {tip.points.map((point, i) => (
                    <li key={i} className="font-paragraph text-sm text-foreground-muted flex items-start gap-2">
                      <ArrowRight className="w-3 h-3 text-primary mt-1 flex-shrink-0" />
                      {point}
                    </li>
                  ))}
                </ul>

                <div className="pt-4 border-t border-border-color">
                  <p className="font-heading text-sm font-bold text-primary">{tip.takeaway}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default function HomePage() {
  return (
    <div className="min-h-screen bg-background text-foreground font-paragraph selection:bg-primary selection:text-white overflow-x-clip">
      <Header />

      <main>
        <HeroSection />
        <StickyProcessSection />
        <FeaturesGrid />
        <IntelligenceInterlude />
        <ImpactSection />
        <LivePracticePreview />
        <TestimonialSection />
        <InterviewQuestionsSection />
        <InterviewTipsSection />
        <IntroductionTipsSection />
        <CTASection />
        <TestimonialsMarquee />
        <FAQSection />
        <TrustedCompanies />
      </main>

      <Footer />
    </div>
  );
}