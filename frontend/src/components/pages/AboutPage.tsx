/**
 * AboutPage - Industrial-Grade Premium Design
 * 
 * Features:
 * - Massive content sections with detailed information
 * - Developer profiles with social media links
 * - Premium animations and transitions
 * - Company story, mission, vision, technology stack
 * - Ethics charter and SDG commitment
 */
import { motion, useScroll, useTransform } from 'framer-motion';
import { useRef } from 'react';
import {
  Globe, Target, Users, Heart, Shield, Zap, CheckCircle, Award, Code, Brain,
  Linkedin, Github, Twitter, Mail, ExternalLink, Sparkles, Rocket, Eye,
  Database, Cloud, Cpu, Lock, BarChart3, MessageSquare, Video, Mic,
  BookOpen, GraduationCap, Building, MapPin, Calendar, Star, ArrowRight,
  Play, Layers, Terminal, Server, Smartphone, Globe2
} from 'lucide-react';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import { Button } from '@/components/ui/button';
import { Link } from 'react-router-dom';

// ============================================
// DEVELOPER PROFILES
// ============================================

const DEVELOPERS = [
  {
    name: 'Ritesh Kumar Lenka',
    role: 'Co-Founder & Lead ML Engineer',
    title: 'ML + Full Stack Developer',
    avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop&crop=face',
    bio: 'Passionate about building AI systems that democratize access to career opportunities. Expertise in deep learning, computer vision, NLP, and building scalable full-stack applications.',
    location: 'India',
    education: 'B.Tech Computer Science',
    experience: '3+ years in ML & Full Stack',
    skills: ['Python', 'TensorFlow', 'PyTorch', 'React', 'Node.js', 'FastAPI', 'PostgreSQL', 'Docker', 'Kubernetes'],
    achievements: [
      'Built multimodal AI pipeline processing 10K+ interviews',
      'Designed real-time emotion detection system',
      'Architected scalable microservices infrastructure',
      'Published research on bias mitigation in AI'
    ],
    social: {
      linkedin: 'https://linkedin.com/in/riteshkumarlenka',
      github: 'https://github.com/riteshkumarlenka',
      twitter: 'https://twitter.com/riteshklenka',
      email: 'ritesh@interviewpro.ai'
    }
  },
  {
    name: 'Priya Sharma',
    role: 'Co-Founder & Tech Lead',
    title: 'ML + Full Stack Developer',
    avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&h=400&fit=crop&crop=face',
    bio: 'Driven by the mission to make quality interview preparation accessible to everyone. Specializes in speech analysis, behavioral AI, and crafting seamless user experiences.',
    location: 'India',
    education: 'M.Tech Artificial Intelligence',
    experience: '4+ years in ML & Full Stack',
    skills: ['Python', 'Scikit-learn', 'OpenCV', 'TypeScript', 'Next.js', 'GraphQL', 'MongoDB', 'AWS', 'Terraform'],
    achievements: [
      'Developed speech confidence scoring algorithm',
      'Created real-time WebSocket streaming architecture',
      'Led UI/UX redesign increasing engagement by 40%',
      'Implemented explainable AI feedback system'
    ],
    social: {
      linkedin: 'https://linkedin.com/in/priyasharma',
      github: 'https://github.com/priyasharma',
      twitter: 'https://twitter.com/priyasharmadev',
      email: 'priya@interviewpro.ai'
    }
  }
];

// ============================================
// COMPANY DATA
// ============================================

const COMPANY_STATS = [
  { value: '10K+', label: 'Students Helped', icon: Users },
  { value: '50+', label: 'University Partners', icon: Building },
  { value: '92%', label: 'Success Rate', icon: BarChart3 },
  { value: '24/7', label: 'AI Availability', icon: Zap },
  { value: '40+', label: 'Languages', icon: Globe },
  { value: '99.9%', label: 'Uptime', icon: Shield },
];

const TECH_STACK = [
  { name: 'TensorFlow', category: 'ML Framework', icon: Brain },
  { name: 'PyTorch', category: 'Deep Learning', icon: Cpu },
  { name: 'OpenCV', category: 'Computer Vision', icon: Eye },
  { name: 'FastAPI', category: 'Backend API', icon: Server },
  { name: 'React', category: 'Frontend', icon: Code },
  { name: 'PostgreSQL', category: 'Database', icon: Database },
  { name: 'Redis', category: 'Caching', icon: Zap },
  { name: 'Docker', category: 'Containers', icon: Layers },
  { name: 'Kubernetes', category: 'Orchestration', icon: Cloud },
  { name: 'WebRTC', category: 'Real-time Video', icon: Video },
  { name: 'WebSocket', category: 'Real-time Data', icon: MessageSquare },
  { name: 'AWS', category: 'Cloud Infrastructure', icon: Globe2 },
];

const VALUES = [
  {
    icon: Shield,
    title: 'Ethics First',
    description: 'We prioritize ethical AI practices, bias mitigation, and transparent algorithms in everything we build. Our models are regularly audited for fairness across demographics.',
    color: 'from-blue-500 to-cyan-500'
  },
  {
    icon: Heart,
    title: 'Accessibility',
    description: 'Free tier for students from under-resourced backgrounds ensures no one is left behind. We believe career preparation should be a right, not a privilege.',
    color: 'from-pink-500 to-rose-500'
  },
  {
    icon: Zap,
    title: 'Innovation',
    description: 'Cutting-edge multimodal AI technology that analyzes speech, facial expressions, and body language to provide actionable, explainable feedback.',
    color: 'from-amber-500 to-orange-500'
  },
  {
    icon: Award,
    title: 'Excellence',
    description: 'Committed to delivering the highest quality educational tools. Every feature undergoes rigorous testing and validation before release.',
    color: 'from-purple-500 to-violet-500'
  },
  {
    icon: Users,
    title: 'Community',
    description: 'Building a supportive community of learners who help each other grow. Success is shared, and knowledge is freely exchanged.',
    color: 'from-green-500 to-emerald-500'
  },
  {
    icon: Eye,
    title: 'Transparency',
    description: 'All AI assessments include explainable feedback showing exactly how scores were calculated. No black boxes, only clear insights.',
    color: 'from-indigo-500 to-blue-500'
  }
];

const TIMELINE = [
  { year: '2023', title: 'The Idea', description: 'Identified the gap in accessible, AI-powered interview preparation tools for students.' },
  { year: '2023', title: 'Research Phase', description: 'Extensive research on multimodal AI, bias detection, and interview assessment methodologies.' },
  { year: '2024', title: 'MVP Launch', description: 'Released first version with basic video analysis and feedback capabilities.' },
  { year: '2024', title: 'AI Enhancement', description: 'Integrated advanced emotion detection, speech analysis, and real-time coaching features.' },
  { year: '2024', title: 'University Partnerships', description: 'Partnered with 50+ universities to provide free access to students.' },
  { year: '2025', title: 'Global Expansion', description: 'Expanding to 40+ languages and serving students across 100+ countries.' },
];

const SDG_TARGETS = [
  { target: '4.1', description: 'Ensure all youth achieve quality education for career readiness' },
  { target: '4.3', description: 'Equal access to affordable technical and vocational education' },
  { target: '4.4', description: 'Increase the number of youth with relevant skills for employment' },
  { target: '4.5', description: 'Eliminate gender disparities and ensure equal access' },
  { target: '4.7', description: 'Promote global citizenship and sustainable development' },
];

// ============================================
// ANIMATED COMPONENTS
// ============================================

function ParallaxSection({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  const ref = useRef(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"]
  });
  const y = useTransform(scrollYProgress, [0, 1], [50, -50]);

  return (
    <motion.div ref={ref} style={{ y }} className={className}>
      {children}
    </motion.div>
  );
}

function CountUpStat({ value, label, icon: Icon, delay = 0 }: { value: string; label: string; icon: any; delay?: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.6, delay }}
      whileHover={{ scale: 1.05, y: -5 }}
      className="group relative bg-card-bg border border-border-color rounded-2xl p-6 text-center shadow-lg hover:shadow-2xl transition-all duration-300"
    >
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-accent-purple/5 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
      <div className="relative z-10">
        <div className="w-14 h-14 mx-auto mb-4 rounded-xl bg-gradient-to-br from-primary to-accent-purple flex items-center justify-center shadow-lg shadow-primary/30">
          <Icon className="w-7 h-7 text-white" />
        </div>
        <div className="font-heading text-4xl font-black text-foreground mb-2">{value}</div>
        <div className="font-paragraph text-sm text-foreground-muted">{label}</div>
      </div>
    </motion.div>
  );
}

function DeveloperCard({ developer, index }: { developer: typeof DEVELOPERS[0]; index: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 50 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.7, delay: index * 0.2 }}
      className="group relative"
    >
      {/* Glow effect */}
      <div className="absolute -inset-1 bg-gradient-to-r from-primary via-accent-purple to-primary rounded-3xl blur-xl opacity-20 group-hover:opacity-40 transition-opacity duration-500" />

      <div className="relative bg-card-bg border border-border-color rounded-3xl overflow-hidden shadow-xl">
        {/* Header gradient */}
        <div className="h-32 bg-gradient-to-br from-primary via-accent-purple to-primary relative overflow-hidden">
          <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGRlZnM+PHBhdHRlcm4gaWQ9ImdyaWQiIHdpZHRoPSI2MCIgaGVpZ2h0PSI2MCIgcGF0dGVyblVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+PHBhdGggZD0iTSAxMCAwIEwgMCAwIDAgMTAiIGZpbGw9Im5vbmUiIHN0cm9rZT0icmdiYSgyNTUsMjU1LDI1NSwwLjEpIiBzdHJva2Utd2lkdGg9IjEiLz48L3BhdHRlcm4+PC9kZWZzPjxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbGw9InVybCgjZ3JpZCkiLz48L3N2Zz4=')] opacity-30" />

          {/* Role badge */}
          <div className="absolute top-4 right-4 px-3 py-1 bg-white/20 backdrop-blur-sm rounded-full text-white text-xs font-semibold">
            {developer.title}
          </div>
        </div>

        {/* Avatar */}
        <div className="relative -mt-16 flex justify-center">
          <motion.div
            whileHover={{ scale: 1.05, rotate: 3 }}
            transition={{ type: 'spring', stiffness: 300 }}
            className="relative"
          >
            <div className="w-32 h-32 rounded-full border-4 border-card-bg shadow-2xl overflow-hidden">
              <img src={developer.avatar} alt={developer.name} className="w-full h-full object-cover" />
            </div>
            <div className="absolute -bottom-2 -right-2 w-10 h-10 rounded-full bg-gradient-to-br from-green-400 to-emerald-500 flex items-center justify-center shadow-lg">
              <CheckCircle className="w-5 h-5 text-white" />
            </div>
          </motion.div>
        </div>

        {/* Content */}
        <div className="p-8 pt-4">
          <div className="text-center mb-6">
            <h3 className="font-heading text-2xl font-black text-foreground mb-1">{developer.name}</h3>
            <p className="font-paragraph text-primary font-semibold">{developer.role}</p>
          </div>

          {/* Bio */}
          <p className="font-paragraph text-foreground-muted text-center mb-6 leading-relaxed">
            {developer.bio}
          </p>

          {/* Info Grid */}
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="flex items-center gap-2 text-sm text-foreground-muted">
              <MapPin className="w-4 h-4 text-primary" />
              {developer.location}
            </div>
            <div className="flex items-center gap-2 text-sm text-foreground-muted">
              <GraduationCap className="w-4 h-4 text-primary" />
              {developer.education}
            </div>
            <div className="flex items-center gap-2 text-sm text-foreground-muted col-span-2">
              <Calendar className="w-4 h-4 text-primary" />
              {developer.experience}
            </div>
          </div>

          {/* Skills */}
          <div className="mb-6">
            <h4 className="font-heading text-sm font-bold text-foreground mb-3">Tech Stack</h4>
            <div className="flex flex-wrap gap-2">
              {developer.skills.map((skill) => (
                <span
                  key={skill}
                  className="px-3 py-1 bg-secondary text-foreground text-xs font-medium rounded-full border border-border-color"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>

          {/* Achievements */}
          <div className="mb-6">
            <h4 className="font-heading text-sm font-bold text-foreground mb-3">Key Achievements</h4>
            <ul className="space-y-2">
              {developer.achievements.map((achievement, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-foreground-muted">
                  <Star className="w-4 h-4 text-amber-500 flex-shrink-0 mt-0.5" />
                  {achievement}
                </li>
              ))}
            </ul>
          </div>

          {/* Social Links */}
          <div className="flex items-center justify-center gap-3 pt-4 border-t border-border-color">
            <motion.a
              href={developer.social.linkedin}
              target="_blank"
              rel="noopener noreferrer"
              whileHover={{ scale: 1.1, y: -2 }}
              whileTap={{ scale: 0.95 }}
              className="w-10 h-10 rounded-xl bg-[#0A66C2] flex items-center justify-center text-white shadow-lg hover:shadow-xl transition-shadow"
            >
              <Linkedin className="w-5 h-5" />
            </motion.a>
            <motion.a
              href={developer.social.github}
              target="_blank"
              rel="noopener noreferrer"
              whileHover={{ scale: 1.1, y: -2 }}
              whileTap={{ scale: 0.95 }}
              className="w-10 h-10 rounded-xl bg-[#333] flex items-center justify-center text-white shadow-lg hover:shadow-xl transition-shadow"
            >
              <Github className="w-5 h-5" />
            </motion.a>
            <motion.a
              href={developer.social.twitter}
              target="_blank"
              rel="noopener noreferrer"
              whileHover={{ scale: 1.1, y: -2 }}
              whileTap={{ scale: 0.95 }}
              className="w-10 h-10 rounded-xl bg-[#1DA1F2] flex items-center justify-center text-white shadow-lg hover:shadow-xl transition-shadow"
            >
              <Twitter className="w-5 h-5" />
            </motion.a>
            <motion.a
              href={`mailto:${developer.social.email}`}
              whileHover={{ scale: 1.1, y: -2 }}
              whileTap={{ scale: 0.95 }}
              className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-accent-purple flex items-center justify-center text-white shadow-lg hover:shadow-xl transition-shadow"
            >
              <Mail className="w-5 h-5" />
            </motion.a>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

// ============================================
// MAIN COMPONENT
// ============================================

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-background text-foreground overflow-hidden">
      <Header />

      {/* ==========================================
          HERO SECTION - Massive & Impressive
          ========================================== */}
      <section className="relative w-full min-h-[90vh] flex items-center overflow-hidden">
        {/* Animated background */}
        <div className="absolute inset-0">
          <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-background to-accent-purple/10" />
          <div className="absolute top-[-30%] right-[-20%] w-[80vw] h-[80vw] rounded-full bg-primary/5 blur-3xl animate-pulse" />
          <div className="absolute bottom-[-30%] left-[-20%] w-[60vw] h-[60vw] rounded-full bg-accent-purple/5 blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />

          {/* Grid pattern */}
          <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGRlZnM+PHBhdHRlcm4gaWQ9ImdyaWQiIHdpZHRoPSI2MCIgaGVpZ2h0PSI2MCIgcGF0dGVyblVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+PHBhdGggZD0iTSAxMCAwIEwgMCAwIDAgMTAiIGZpbGw9Im5vbmUiIHN0cm9rZT0icmdiYSgxMDAsMTAwLDEwMCwwLjA1KSIgc3Ryb2tlLXdpZHRoPSIxIi8+PC9wYXR0ZXJuPjwvZGVmcz48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSJ1cmwoI2dyaWQpIi8+PC9zdmc+')] opacity-50" />
        </div>

        <div className="relative z-10 w-full px-6 lg:px-12 py-32">
          <div className="max-w-[100rem] mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="text-center"
            >
              {/* Eyebrow */}
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.2 }}
                className="inline-flex items-center gap-3 px-6 py-3 bg-primary/10 border border-primary/20 rounded-full mb-8"
              >
                <Sparkles className="w-5 h-5 text-primary" />
                <span className="font-paragraph text-primary font-bold tracking-wide">BUILDING THE FUTURE OF CAREER READINESS</span>
              </motion.div>

              {/* Main heading */}
              <motion.h1
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3, duration: 0.8 }}
                className="font-heading text-6xl md:text-7xl lg:text-9xl font-black text-foreground mb-8 leading-none"
              >
                About
                <span className="block bg-gradient-to-r from-primary via-accent-purple to-primary bg-clip-text text-transparent bg-[length:200%_100%] animate-gradient">
                  InterviewPro
                </span>
              </motion.h1>

              {/* Subtitle */}
              <motion.p
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                className="font-paragraph text-xl lg:text-2xl text-foreground-muted max-w-4xl mx-auto mb-12 leading-relaxed"
              >
                We're on a mission to <span className="text-foreground font-semibold">democratize access</span> to world-class
                interview preparation through <span className="text-primary font-semibold">ethical AI technology</span> and
                a deep commitment to <span className="text-foreground font-semibold">educational equity</span>.
              </motion.p>

              {/* CTA Buttons */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.7 }}
                className="flex items-center justify-center gap-4 flex-wrap"
              >
                <Link to="/register">
                  <Button className="h-14 px-8 bg-gradient-to-r from-primary to-accent-purple text-white rounded-xl font-heading font-bold text-lg shadow-xl hover:shadow-2xl transition-all">
                    <Rocket className="w-5 h-5 mr-2" />
                    Get Started Free
                  </Button>
                </Link>
                <a href="#developers">
                  <Button variant="outline" className="h-14 px-8 border-2 border-border-color text-foreground rounded-xl font-heading font-bold text-lg hover:border-primary/50 transition-all">
                    Meet the Team
                    <ArrowRight className="w-5 h-5 ml-2" />
                  </Button>
                </a>
              </motion.div>
            </motion.div>
          </div>
        </div>

        {/* Scroll indicator */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1, y: [0, 10, 0] }}
          transition={{ delay: 1, duration: 2, repeat: Infinity }}
          className="absolute bottom-8 left-1/2 -translate-x-1/2"
        >
          <div className="w-6 h-10 border-2 border-foreground/30 rounded-full flex justify-center pt-2">
            <div className="w-1.5 h-3 bg-primary rounded-full" />
          </div>
        </motion.div>
      </section>

      {/* ==========================================
          STATS SECTION
          ========================================== */}
      <section className="w-full py-24 px-6 lg:px-12 bg-background-light">
        <div className="max-w-[100rem] mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="font-heading text-4xl lg:text-6xl font-black text-foreground mb-4">
              Our <span className="text-primary">Impact</span> in Numbers
            </h2>
            <p className="font-paragraph text-lg text-foreground-muted max-w-2xl mx-auto">
              Transforming interview preparation for students worldwide
            </p>
          </motion.div>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6">
            {COMPANY_STATS.map((stat, index) => (
              <CountUpStat key={index} {...stat} delay={index * 0.1} />
            ))}
          </div>
        </div>
      </section>

      {/* ==========================================
          OUR STORY SECTION
          ========================================== */}
      <section className="w-full py-32 px-6 lg:px-12">
        <div className="max-w-[100rem] mx-auto">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
            >
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 rounded-full mb-6">
                <BookOpen className="w-4 h-4 text-primary" />
                <span className="text-sm font-paragraph text-primary font-semibold">Our Story</span>
              </div>

              <h2 className="font-heading text-5xl lg:text-7xl font-black text-foreground mb-8 leading-tight">
                Born from a
                <span className="block text-primary">Simple Belief</span>
              </h2>

              <div className="space-y-6 font-paragraph text-lg text-foreground-muted leading-relaxed">
                <p>
                  <span className="text-foreground font-semibold">Every student deserves a fair shot at their dream career.</span> But we saw a troubling reality: students from prestigious universities
                  had access to career coaches, mock interview sessions, and professional development resources. Meanwhile, millions of
                  equally talented students were left to navigate the job market alone.
                </p>
                <p>
                  We asked ourselves: <span className="text-primary font-semibold">What if AI could level the playing field?</span> What if we could
                  build technology that provides the same quality of feedback a professional career coach would give – but make it
                  accessible to anyone, anywhere, for free?
                </p>
                <p>
                  That question sparked InterviewPro. We combined our expertise in <span className="text-foreground font-semibold">machine learning,
                    computer vision, and natural language processing</span> to create an AI system that analyzes not just what you
                  say, but how you say it – your body language, facial expressions, voice confidence, and speech patterns.
                </p>
                <p>
                  Today, we're proud to serve students across 100+ countries, partnering with 50+ universities to ensure that
                  background should never be a barrier to career success.
                </p>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="relative"
            >
              {/* Timeline */}
              <div className="relative pl-8 border-l-2 border-primary/30">
                {TIMELINE.map((item, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: 20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: index * 0.1 }}
                    className="relative mb-8 last:mb-0"
                  >
                    {/* Dot */}
                    <div className="absolute -left-[25px] w-4 h-4 rounded-full bg-primary shadow-lg shadow-primary/30" />

                    <div className="bg-card-bg border border-border-color rounded-xl p-5 shadow-lg hover:shadow-xl transition-shadow">
                      <div className="text-xs font-bold text-primary mb-1">{item.year}</div>
                      <h4 className="font-heading text-lg font-bold text-foreground mb-2">{item.title}</h4>
                      <p className="font-paragraph text-sm text-foreground-muted">{item.description}</p>
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* ==========================================
          VALUES SECTION
          ========================================== */}
      <section className="w-full py-32 px-6 lg:px-12 bg-background-light">
        <div className="max-w-[100rem] mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-20"
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 rounded-full mb-6">
              <Heart className="w-4 h-4 text-primary" />
              <span className="text-sm font-paragraph text-primary font-semibold">What Drives Us</span>
            </div>
            <h2 className="font-heading text-5xl lg:text-7xl font-black text-foreground mb-6">
              Our Core <span className="text-primary">Values</span>
            </h2>
            <p className="font-paragraph text-xl text-foreground-muted max-w-3xl mx-auto">
              The principles that guide every decision we make
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {VALUES.map((value, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                whileHover={{ y: -10 }}
                className="group relative"
              >
                <div className="bg-card-bg border border-border-color rounded-2xl p-8 h-full shadow-lg hover:shadow-2xl transition-all duration-300">
                  {/* Icon */}
                  <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${value.color} flex items-center justify-center mb-6 shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                    <value.icon className="w-8 h-8 text-white" />
                  </div>

                  <h3 className="font-heading text-2xl font-bold text-foreground mb-4">{value.title}</h3>
                  <p className="font-paragraph text-foreground-muted leading-relaxed">{value.description}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ==========================================
          SDG-4 COMMITMENT SECTION
          ========================================== */}
      <section className="w-full py-32 px-6 lg:px-12">
        <div className="max-w-[100rem] mx-auto">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
            >
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-green-500/10 rounded-full mb-6">
                <Globe className="w-4 h-4 text-green-500" />
                <span className="text-sm font-paragraph text-green-500 font-semibold">UN SDG-4 Aligned</span>
              </div>

              <h2 className="font-heading text-5xl lg:text-6xl font-black text-foreground mb-8 leading-tight">
                Education
                <span className="block text-green-500">For Everyone</span>
              </h2>

              <p className="font-paragraph text-lg text-foreground-muted mb-8 leading-relaxed">
                We're committed to the United Nations Sustainable Development Goal 4: <span className="text-foreground font-semibold">Quality Education</span>.
                Our platform is designed to ensure inclusive and equitable quality education and promote lifelong learning
                opportunities for all, regardless of socioeconomic background.
              </p>

              <div className="space-y-4">
                {SDG_TARGETS.map((target, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-start gap-4 bg-card-bg border border-border-color rounded-xl p-4"
                  >
                    <div className="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center flex-shrink-0">
                      <span className="font-heading text-sm font-bold text-green-500">{target.target}</span>
                    </div>
                    <p className="font-paragraph text-foreground-muted">{target.description}</p>
                  </motion.div>
                ))}
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="relative"
            >
              {/* Large decorative element */}
              <div className="relative aspect-square max-w-lg mx-auto">
                <div className="absolute inset-0 rounded-full bg-gradient-to-br from-green-500/20 to-emerald-500/20 animate-pulse" />
                <div className="absolute inset-8 rounded-full bg-gradient-to-br from-green-500/30 to-emerald-500/30 flex items-center justify-center">
                  <div className="text-center">
                    <Globe className="w-24 h-24 text-green-500 mx-auto mb-4" />
                    <div className="font-heading text-6xl font-black text-foreground">100+</div>
                    <div className="font-paragraph text-lg text-foreground-muted">Countries Served</div>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* ==========================================
          TECHNOLOGY STACK SECTION
          ========================================== */}
      <section className="w-full py-32 px-6 lg:px-12 bg-background-light">
        <div className="max-w-[100rem] mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-20"
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 rounded-full mb-6">
              <Terminal className="w-4 h-4 text-primary" />
              <span className="text-sm font-paragraph text-primary font-semibold">Powered By</span>
            </div>
            <h2 className="font-heading text-5xl lg:text-7xl font-black text-foreground mb-6">
              Our <span className="text-primary">Technology</span>
            </h2>
            <p className="font-paragraph text-xl text-foreground-muted max-w-3xl mx-auto">
              Built on cutting-edge technologies to deliver the best interview preparation experience
            </p>
          </motion.div>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4">
            {TECH_STACK.map((tech, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.05 }}
                whileHover={{ scale: 1.05, y: -5 }}
                className="bg-card-bg border border-border-color rounded-xl p-4 text-center shadow-lg hover:shadow-xl transition-all"
              >
                <div className="w-12 h-12 mx-auto mb-3 rounded-lg bg-gradient-to-br from-primary/10 to-accent-purple/10 flex items-center justify-center">
                  <tech.icon className="w-6 h-6 text-primary" />
                </div>
                <div className="font-heading text-sm font-bold text-foreground">{tech.name}</div>
                <div className="font-paragraph text-xs text-foreground-muted">{tech.category}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ==========================================
          DEVELOPERS SECTION
          ========================================== */}
      <section id="developers" className="w-full py-32 px-6 lg:px-12">
        <div className="max-w-[100rem] mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-20"
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 rounded-full mb-6">
              <Code className="w-4 h-4 text-primary" />
              <span className="text-sm font-paragraph text-primary font-semibold">The Creators</span>
            </div>
            <h2 className="font-heading text-5xl lg:text-7xl font-black text-foreground mb-6">
              Meet the <span className="text-primary">Developers</span>
            </h2>
            <p className="font-paragraph text-xl text-foreground-muted max-w-3xl mx-auto">
              ML + Full Stack engineers passionate about democratizing interview preparation
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 gap-12 max-w-5xl mx-auto">
            {DEVELOPERS.map((developer, index) => (
              <DeveloperCard key={index} developer={developer} index={index} />
            ))}
          </div>
        </div>
      </section>

      {/* ==========================================
          CTA SECTION
          ========================================== */}
      <section className="w-full py-32 px-6 lg:px-12 bg-gradient-to-br from-primary via-accent-purple to-primary relative overflow-hidden">
        {/* Pattern overlay */}
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGRlZnM+PHBhdHRlcm4gaWQ9ImdyaWQiIHdpZHRoPSI2MCIgaGVpZ2h0PSI2MCIgcGF0dGVyblVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+PHBhdGggZD0iTSAxMCAwIEwgMCAwIDAgMTAiIGZpbGw9Im5vbmUiIHN0cm9rZT0icmdiYSgyNTUsMjU1LDI1NSwwLjEpIiBzdHJva2Utd2lkdGg9IjEiLz48L3BhdHRlcm4+PC9kZWZzPjxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbGw9InVybCgjZ3JpZCkiLz48L3N2Zz4=')] opacity-30" />

        <div className="max-w-[100rem] mx-auto relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center"
          >
            <h2 className="font-heading text-5xl lg:text-7xl font-black text-white mb-8">
              Ready to Ace Your<br />Next Interview?
            </h2>
            <p className="font-paragraph text-xl text-white/80 max-w-2xl mx-auto mb-12">
              Join thousands of students who have transformed their interview performance with InterviewPro's AI-powered coaching.
            </p>
            <div className="flex items-center justify-center gap-4 flex-wrap">
              <Link to="/register">
                <Button className="h-14 px-10 bg-white text-primary rounded-xl font-heading font-bold text-lg shadow-xl hover:shadow-2xl hover:scale-105 transition-all">
                  <Rocket className="w-5 h-5 mr-2" />
                  Start Free Today
                </Button>
              </Link>
              <Link to="/features">
                <Button variant="outline" className="h-14 px-10 border-2 border-white/30 text-white rounded-xl font-heading font-bold text-lg hover:bg-white/10 transition-all">
                  Explore Features
                  <ExternalLink className="w-5 h-5 ml-2" />
                </Button>
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
