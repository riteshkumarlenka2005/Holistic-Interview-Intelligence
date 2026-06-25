/**
 * ResourcesPage - Ultra Premium Learning Experience
 * 
 * Features:
 * - 25+ Videos, Articles, Guides, Tutorials
 * - Interview Gallery with 15 situational images
 * - Google Search integration
 * - Full filter functionality
 * - Premium animations and design
 */
import { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  BookOpen, Video, FileText, Search, Filter, X, ExternalLink,
  Sparkles, ArrowRight, GraduationCap, Play, Clock, Star, Eye,
  Image as ImageIcon, Download, ChevronRight, Globe, Bookmark
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import { Link } from 'react-router-dom';

// Resource types
type ResourceType = 'Article' | 'Video' | 'Guide' | 'Tutorial' | 'Gallery';

interface Resource {
  id: string;
  title: string;
  description: string;
  type: ResourceType;
  thumbnail: string;
  duration?: string;
  author: string;
  rating: number;
  views: number;
  tags: string[];
  url?: string;
  videoId?: string;
}

interface GalleryImage {
  id: string;
  title: string;
  description: string;
  url: string;
  category: string;
}

// ============================================
// STATIC RESOURCES DATA - 30+ Resources
// ============================================

const RESOURCES: Resource[] = [
  // VIDEOS (25 videos)
  {
    id: 'v1', title: 'How to Answer "Tell Me About Yourself"', description: 'Master the most common interview opening question with proven frameworks.', type: 'Video', thumbnail: 'https://img.youtube.com/vi/kayOhGRcNt4/maxresdefault.jpg', duration: '12:34', author: 'Interview Pro', rating: 4.9, views: 125000, tags: ['behavioral', 'opening', 'introduction'], videoId: 'kayOhGRcNt4'
  },
  {
    id: 'v2', title: 'STAR Method Interview Technique', description: 'Learn the Situation, Task, Action, Result framework for behavioral questions.', type: 'Video', thumbnail: 'https://img.youtube.com/vi/0nN7Q7DrI6Q/maxresdefault.jpg', duration: '15:20', author: 'Career Coach', rating: 4.8, views: 98000, tags: ['STAR', 'behavioral', 'technique'], videoId: '0nN7Q7DrI6Q'
  },
  {
    id: 'v3', title: 'Body Language Tips for Interviews', description: 'Non-verbal communication secrets that impress interviewers instantly.', type: 'Video', thumbnail: 'https://img.youtube.com/vi/cFLjudWTuGQ/maxresdefault.jpg', duration: '10:45', author: 'Communication Expert', rating: 4.7, views: 87000, tags: ['body language', 'non-verbal', 'confidence'], videoId: 'cFLjudWTuGQ'
  },
  {
    id: 'v4', title: 'Top 10 Interview Questions & Answers', description: 'Comprehensive guide to the most frequently asked interview questions.', type: 'Video', thumbnail: 'https://img.youtube.com/vi/1mHjMNZZvFo/maxresdefault.jpg', duration: '25:00', author: 'HR Insider', rating: 4.9, views: 200000, tags: ['common questions', 'preparation', 'answers'], videoId: '1mHjMNZZvFo'
  },
  {
    id: 'v5', title: 'Virtual Interview Best Practices', description: 'Ace your video interviews with professional tips and setup guide.', type: 'Video', thumbnail: 'https://img.youtube.com/vi/HG68Ymazo18/maxresdefault.jpg', duration: '11:30', author: 'Remote Work Pro', rating: 4.6, views: 65000, tags: ['virtual', 'video interview', 'remote'], videoId: 'HG68Ymazo18'
  },
  {
    id: 'v6', title: 'Salary Negotiation Masterclass', description: 'Get paid what you deserve with proven negotiation strategies.', type: 'Video', thumbnail: 'https://img.youtube.com/vi/WWc_xF16LYY/maxresdefault.jpg', duration: '18:15', author: 'Salary Expert', rating: 4.8, views: 110000, tags: ['salary', 'negotiation', 'offer'], videoId: 'WWc_xF16LYY'
  },
  {
    id: 'v7', title: 'Technical Interview Preparation', description: 'Complete guide to preparing for technical and coding interviews.', type: 'Video', thumbnail: 'https://img.youtube.com/vi/1qw5ITr3k9E/maxresdefault.jpg', duration: '22:30', author: 'Tech Career Hub', rating: 4.9, views: 150000, tags: ['technical', 'coding', 'programming'], videoId: '1qw5ITr3k9E'
  },
  {
    id: 'v8', title: 'Handling Stress Questions', description: 'Stay calm and composed when faced with pressure interview questions.', type: 'Video', thumbnail: 'https://img.youtube.com/vi/f_Bz5feDwLA/maxresdefault.jpg', duration: '13:45', author: 'Psychology Today', rating: 4.7, views: 78000, tags: ['stress', 'pressure', 'difficult questions'], videoId: 'f_Bz5feDwLA'
  },
  {
    id: 'v9', title: 'First Impression Techniques', description: 'Make a powerful first impression in the first 30 seconds.', type: 'Video', thumbnail: 'https://img.youtube.com/vi/naIkpQ_cIt0/maxresdefault.jpg', duration: '9:20', author: 'Charisma Coach', rating: 4.8, views: 92000, tags: ['first impression', 'entrance', 'greeting'], videoId: 'naIkpQ_cIt0'
  },
  {
    id: 'v10', title: 'Panel Interview Survival Guide', description: 'Navigate multiple interviewers with confidence and poise.', type: 'Video', thumbnail: 'https://img.youtube.com/vi/qoLFrSNDyjo/maxresdefault.jpg', duration: '14:00', author: 'Interview Coach', rating: 4.6, views: 45000, tags: ['panel', 'group interview', 'multiple interviewers'], videoId: 'qoLFrSNDyjo'
  },
  {
    id: 'v11', title: 'Questions to Ask the Interviewer', description: 'Smart questions that show genuine interest and research.', type: 'Video', thumbnail: 'https://img.youtube.com/vi/Y95eI-ek_E8/maxresdefault.jpg', duration: '11:15', author: 'Career Strategist', rating: 4.9, views: 88000, tags: ['questions', 'closing', 'engagement'], videoId: 'Y95eI-ek_E8'
  },
  {
    id: 'v12', title: 'Overcoming Interview Anxiety', description: 'Practical techniques to manage nerves and perform your best.', type: 'Video', thumbnail: 'https://img.youtube.com/vi/s_KvlQuvhU8/maxresdefault.jpg', duration: '16:40', author: 'Wellness Coach', rating: 4.8, views: 120000, tags: ['anxiety', 'nerves', 'mental preparation'], videoId: 's_KvlQuvhU8'
  },
  {
    id: 'v13', title: 'Leadership Interview Questions', description: 'Demonstrate leadership potential with powerful examples.', type: 'Video', thumbnail: 'https://img.youtube.com/vi/2xvpMl-EzfM/maxresdefault.jpg', duration: '17:30', author: 'Executive Coach', rating: 4.7, views: 67000, tags: ['leadership', 'management', 'executive'], videoId: '2xvpMl-EzfM'
  },
  {
    id: 'v14', title: 'Behavioral Interview Deep Dive', description: 'Advanced strategies for competency-based interviews.', type: 'Video', thumbnail: 'https://img.youtube.com/vi/t1ihg_KOEpU/maxresdefault.jpg', duration: '20:00', author: 'HR Director', rating: 4.8, views: 95000, tags: ['behavioral', 'competency', 'situational'], videoId: 't1ihg_KOEpU'
  },
  {
    id: 'v15', title: 'Remote Work Interview Tips', description: 'Specific strategies for remote and hybrid role interviews.', type: 'Video', thumbnail: 'https://img.youtube.com/vi/Xn6gy1LoA1g/maxresdefault.jpg', duration: '12:50', author: 'Remote Expert', rating: 4.6, views: 54000, tags: ['remote', 'hybrid', 'work from home'], videoId: 'Xn6gy1LoA1g'
  },
  {
    id: 'v16', title: 'Case Interview Framework', description: 'Consulting and business case interview methodology explained.', type: 'Video', thumbnail: 'https://img.youtube.com/vi/AeIa13yS69c/maxresdefault.jpg', duration: '28:00', author: 'McKinsey Alum', rating: 4.9, views: 180000, tags: ['case study', 'consulting', 'problem solving'], videoId: 'AeIa13yS69c'
  },
  {
    id: 'v17', title: 'Weakness Question Strategy', description: 'Turn your weaknesses into strengths with this reframing technique.', type: 'Video', thumbnail: 'https://img.youtube.com/vi/Uo0KjdDJr1c/maxresdefault.jpg', duration: '10:30', author: 'Interview Pro', rating: 4.7, views: 73000, tags: ['weaknesses', 'strengths', 'self-awareness'], videoId: 'Uo0KjdDJr1c'
  },
  {
    id: 'v18', title: 'Follow-up Email Masterclass', description: 'Write compelling thank-you emails that keep you top of mind.', type: 'Video', thumbnail: 'https://img.youtube.com/vi/DHDrj0_bMQ0/maxresdefault.jpg', duration: '8:45', author: 'Communication Expert', rating: 4.8, views: 61000, tags: ['follow-up', 'thank you', 'email'], videoId: 'DHDrj0_bMQ0'
  },
  {
    id: 'v19', title: 'Phone Interview Success', description: 'Impress recruiters during initial phone screening calls.', type: 'Video', thumbnail: 'https://img.youtube.com/vi/LXEIlCq_VTI/maxresdefault.jpg', duration: '11:00', author: 'Recruiter Insights', rating: 4.6, views: 49000, tags: ['phone', 'screening', 'recruiter'], videoId: 'LXEIlCq_VTI'
  },
  {
    id: 'v20', title: 'Group Discussion Techniques', description: 'Stand out in group discussion rounds with these proven tactics.', type: 'Video', thumbnail: 'https://img.youtube.com/vi/7IJ_sK4T8oY/maxresdefault.jpg', duration: '14:20', author: 'Assessment Expert', rating: 4.7, views: 82000, tags: ['group discussion', 'assessment center', 'teamwork'], videoId: '7IJ_sK4T8oY'
  },
  {
    id: 'v21', title: 'Data Science Interview Prep', description: 'Technical questions and case studies for data roles.', type: 'Video', thumbnail: 'https://img.youtube.com/vi/X3paOmcrTjQ/maxresdefault.jpg', duration: '32:00', author: 'Data Scientist', rating: 4.9, views: 140000, tags: ['data science', 'analytics', 'machine learning'], videoId: 'X3paOmcrTjQ'
  },
  {
    id: 'v22', title: 'Creative Role Portfolios', description: 'Present your work effectively for design and creative positions.', type: 'Video', thumbnail: 'https://img.youtube.com/vi/T0Z73Zbtlyg/maxresdefault.jpg', duration: '15:30', author: 'Design Director', rating: 4.8, views: 38000, tags: ['portfolio', 'creative', 'design'], videoId: 'T0Z73Zbtlyg'
  },
  {
    id: 'v23', title: 'Entry Level Interview Tips', description: 'Land your first job with strategies for new graduates.', type: 'Video', thumbnail: 'https://img.youtube.com/vi/DrBj6nzGEK8/maxresdefault.jpg', duration: '13:15', author: 'Career Starter', rating: 4.7, views: 165000, tags: ['entry level', 'graduate', 'first job'], videoId: 'DrBj6nzGEK8'
  },
  {
    id: 'v24', title: 'Executive Presence in Interviews', description: 'Command respect and authority in senior-level interviews.', type: 'Video', thumbnail: 'https://img.youtube.com/vi/uBH0KLN3hN4/maxresdefault.jpg', duration: '19:00', author: 'Executive Coach', rating: 4.9, views: 52000, tags: ['executive', 'senior', 'c-level'], videoId: 'uBH0KLN3hN4'
  },
  {
    id: 'v25', title: 'Mock Interview Practice Session', description: 'Full mock interview with expert commentary and feedback.', type: 'Video', thumbnail: 'https://img.youtube.com/vi/I1Y0cdxB7So/maxresdefault.jpg', duration: '45:00', author: 'Interview Pro', rating: 4.9, views: 210000, tags: ['mock interview', 'practice', 'feedback'], videoId: 'I1Y0cdxB7So'
  },

  // ARTICLES (8 articles)
  {
    id: 'a1', title: 'The Psychology of First Impressions', description: 'Research-backed insights on how interviewers form opinions in the first 7 seconds.', type: 'Article', thumbnail: 'https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?w=800&h=450&fit=crop', author: 'Dr. Sarah Johnson', rating: 4.8, views: 45000, tags: ['psychology', 'first impression', 'research'], url: '#'
  },
  {
    id: 'a2', title: 'Building Authentic Confidence', description: 'Develop genuine self-assurance that shines through in high-pressure situations.', type: 'Article', thumbnail: 'https://images.unsplash.com/photo-1560250097-0b93528c311a?w=800&h=450&fit=crop', author: 'Michael Chen', rating: 4.9, views: 62000, tags: ['confidence', 'authenticity', 'mindset'], url: '#'
  },
  {
    id: 'a3', title: 'Remote Interview Technology Setup', description: 'Complete guide to camera, lighting, and audio for virtual interviews.', type: 'Article', thumbnail: 'https://images.unsplash.com/photo-1587825140708-dfaf72ae4b04?w=800&h=450&fit=crop', author: 'Tech Team', rating: 4.7, views: 38000, tags: ['remote', 'technology', 'setup'], url: '#'
  },
  {
    id: 'a4', title: 'Industry-Specific Interview Trends 2024', description: 'Latest hiring trends across tech, finance, healthcare, and more.', type: 'Article', thumbnail: 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=800&h=450&fit=crop', author: 'Research Team', rating: 4.8, views: 55000, tags: ['trends', 'industry', '2024'], url: '#'
  },
  {
    id: 'a5', title: 'Mastering the Art of Storytelling', description: 'Transform your experiences into compelling narratives interviewers remember.', type: 'Article', thumbnail: 'https://images.unsplash.com/photo-1515378960530-7c0da6231fb1?w=800&h=450&fit=crop', author: 'Communications Expert', rating: 4.9, views: 71000, tags: ['storytelling', 'communication', 'narrative'], url: '#'
  },
  {
    id: 'a6', title: 'Cultural Fit vs. Skill Assessment', description: 'Understanding what companies really evaluate during interviews.', type: 'Article', thumbnail: 'https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=800&h=450&fit=crop', author: 'HR Insights', rating: 4.6, views: 42000, tags: ['cultural fit', 'skills', 'evaluation'], url: '#'
  },
  {
    id: 'a7', title: 'Post-Interview Reflection Framework', description: 'Analyze and improve your performance after every interview.', type: 'Article', thumbnail: 'https://images.unsplash.com/photo-1484480974693-6ca0a78fb36b?w=800&h=450&fit=crop', author: 'Coach Miller', rating: 4.8, views: 33000, tags: ['reflection', 'improvement', 'learning'], url: '#'
  },
  {
    id: 'a8', title: 'Diversity & Inclusion Interview Guide', description: 'Navigate D&I questions and demonstrate inclusive leadership.', type: 'Article', thumbnail: 'https://images.unsplash.com/photo-1573164713988-8665fc963095?w=800&h=450&fit=crop', author: 'D&I Specialist', rating: 4.9, views: 29000, tags: ['diversity', 'inclusion', 'leadership'], url: '#'
  },

  // GUIDES (5 guides)
  {
    id: 'g1', title: 'Complete Interview Preparation Checklist', description: '30-day roadmap to interview success with daily action items.', type: 'Guide', thumbnail: 'https://images.unsplash.com/photo-1434626881859-194d67b2b86f?w=800&h=450&fit=crop', author: 'Interview Pro Team', rating: 4.9, views: 98000, tags: ['checklist', 'preparation', '30-day'], url: '#'
  },
  {
    id: 'g2', title: 'Salary Research & Negotiation Toolkit', description: 'Step-by-step guide with templates for compensation conversations.', type: 'Guide', thumbnail: 'https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=800&h=450&fit=crop', author: 'Compensation Expert', rating: 4.8, views: 75000, tags: ['salary', 'negotiation', 'toolkit'], url: '#'
  },
  {
    id: 'g3', title: 'Resume to Interview Conversion Guide', description: 'Optimize your resume to get 3x more interview callbacks.', type: 'Guide', thumbnail: 'https://images.unsplash.com/photo-1586281380349-632531db7ed4?w=800&h=450&fit=crop', author: 'Resume Expert', rating: 4.7, views: 112000, tags: ['resume', 'optimization', 'callbacks'], url: '#'
  },
  {
    id: 'g4', title: 'Industry Interview Question Banks', description: 'Curated questions for 20+ industries with model answers.', type: 'Guide', thumbnail: 'https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=800&h=450&fit=crop', author: 'Industry Experts', rating: 4.9, views: 89000, tags: ['questions', 'industry', 'answers'], url: '#'
  },
  {
    id: 'g5', title: 'Virtual Presence Optimization', description: 'Technical and personal branding guide for video interviews.', type: 'Guide', thumbnail: 'https://images.unsplash.com/photo-1609220136736-443140cffec6?w=800&h=450&fit=crop', author: 'Digital Expert', rating: 4.8, views: 58000, tags: ['virtual', 'branding', 'video'], url: '#'
  },

  // TUTORIALS (5 tutorials)
  {
    id: 't1', title: 'STAR Method Interactive Workshop', description: 'Practice building STAR responses with instant AI feedback.', type: 'Tutorial', thumbnail: 'https://images.unsplash.com/photo-1524178232363-1fb2b075b655?w=800&h=450&fit=crop', duration: '45 min', author: 'Workshop Team', rating: 4.9, views: 67000, tags: ['STAR', 'interactive', 'practice'], url: '#'
  },
  {
    id: 't2', title: 'Voice Modulation Training', description: 'Exercises to improve tone, pace, and clarity during interviews.', type: 'Tutorial', thumbnail: 'https://images.unsplash.com/photo-1478737270239-2f02b77fc618?w=800&h=450&fit=crop', duration: '30 min', author: 'Voice Coach', rating: 4.8, views: 43000, tags: ['voice', 'speaking', 'modulation'], url: '#'
  },
  {
    id: 't3', title: 'Body Language Mirror Practice', description: 'Video-guided exercises to perfect your non-verbal communication.', type: 'Tutorial', thumbnail: 'https://images.unsplash.com/photo-1521791136064-7986c2920216?w=800&h=450&fit=crop', duration: '25 min', author: 'Coach Smith', rating: 4.7, views: 51000, tags: ['body language', 'practice', 'mirror'], url: '#'
  },
  {
    id: 't4', title: 'Difficult Questions Simulation', description: 'AI-powered practice with challenging interview scenarios.', type: 'Tutorial', thumbnail: 'https://images.unsplash.com/photo-1551836022-deb4988cc6c0?w=800&h=450&fit=crop', duration: '40 min', author: 'AI Team', rating: 4.9, views: 78000, tags: ['simulation', 'AI', 'difficult'], url: '#'
  },
  {
    id: 't5', title: 'Confidence Building Exercises', description: 'Daily micro-practices to build lasting interview confidence.', type: 'Tutorial', thumbnail: 'https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?w=800&h=450&fit=crop', duration: '15 min/day', author: 'Wellness Coach', rating: 4.8, views: 92000, tags: ['confidence', 'daily', 'exercises'], url: '#'
  },
];

// ============================================
// GALLERY IMAGES - 15 Interview Situational Images
// ============================================

const GALLERY_IMAGES: GalleryImage[] = [
  { id: 'img1', title: 'Professional Handshake', description: 'Perfect greeting technique', url: 'https://images.unsplash.com/photo-1560250097-0b93528c311a?w=800&h=600&fit=crop', category: 'greeting' },
  { id: 'img2', title: 'Panel Interview Setup', description: 'Facing multiple interviewers', url: 'https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?w=800&h=600&fit=crop', category: 'panel' },
  { id: 'img3', title: 'Video Interview Setting', description: 'Professional home office setup', url: 'https://images.unsplash.com/photo-1587825140708-dfaf72ae4b04?w=800&h=600&fit=crop', category: 'virtual' },
  { id: 'img4', title: 'Confident Body Language', description: 'Open and engaged posture', url: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=800&h=600&fit=crop', category: 'body-language' },
  { id: 'img5', title: 'Active Listening', description: 'Engaged and attentive demeanor', url: 'https://images.unsplash.com/photo-1551836022-deb4988cc6c0?w=800&h=600&fit=crop', category: 'listening' },
  { id: 'img6', title: 'Note-Taking During Interview', description: 'Professional documentation approach', url: 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=800&h=600&fit=crop', category: 'preparation' },
  { id: 'img7', title: 'Group Discussion Round', description: 'Collaborative assessment setting', url: 'https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=800&h=600&fit=crop', category: 'group' },
  { id: 'img8', title: 'Whiteboard Presentation', description: 'Technical interview scenario', url: 'https://images.unsplash.com/photo-1524178232363-1fb2b075b655?w=800&h=600&fit=crop', category: 'technical' },
  { id: 'img9', title: 'One-on-One Setting', description: 'Traditional interview format', url: 'https://images.unsplash.com/photo-1521791136064-7986c2920216?w=800&h=600&fit=crop', category: 'one-on-one' },
  { id: 'img10', title: 'Waiting Room Composure', description: 'Pre-interview mindset', url: 'https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=800&h=600&fit=crop', category: 'waiting' },
  { id: 'img11', title: 'Resume Review Discussion', description: 'Discussing work history', url: 'https://images.unsplash.com/photo-1586281380349-632531db7ed4?w=800&h=600&fit=crop', category: 'resume' },
  { id: 'img12', title: 'Team Culture Fit', description: 'Meeting potential colleagues', url: 'https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?w=800&h=600&fit=crop', category: 'culture' },
  { id: 'img13', title: 'Executive Interview', description: 'Senior-level interview setting', url: 'https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=800&h=600&fit=crop', category: 'executive' },
  { id: 'img14', title: 'Casual Coffee Interview', description: 'Informal assessment meeting', url: 'https://images.unsplash.com/photo-1515378960530-7c0da6231fb1?w=800&h=600&fit=crop', category: 'casual' },
  { id: 'img15', title: 'Portfolio Presentation', description: 'Creative role interview', url: 'https://images.unsplash.com/photo-1573164713988-8665fc963095?w=800&h=600&fit=crop', category: 'creative' },
];

// Filter options including Gallery
const FILTER_OPTIONS = [
  { value: 'all', label: 'All Resources', icon: Sparkles },
  { value: 'Article', label: 'Articles', icon: FileText },
  { value: 'Video', label: 'Videos', icon: Video },
  { value: 'Guide', label: 'Guides', icon: BookOpen },
  { value: 'Tutorial', label: 'Tutorials', icon: GraduationCap },
  { value: 'Gallery', label: 'Gallery', icon: ImageIcon },
];

// ============================================
// RESOURCE CARD COMPONENT
// ============================================

function ResourceCardComponent({ resource, index }: { resource: Resource; index: number }) {
  const typeColors = {
    Video: 'bg-red-500',
    Article: 'bg-blue-500',
    Guide: 'bg-green-500',
    Tutorial: 'bg-purple-500',
    Gallery: 'bg-pink-500',
  };

  const handleClick = () => {
    if (resource.type === 'Video' && resource.videoId) {
      window.open(`https://www.youtube.com/watch?v=${resource.videoId}`, '_blank');
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5, delay: index * 0.05 }}
      whileHover={{ y: -8, transition: { duration: 0.2 } }}
      className="group cursor-pointer"
      onClick={handleClick}
    >
      <div className="bg-card-bg rounded-2xl border border-border-color overflow-hidden shadow-lg hover:shadow-2xl transition-all duration-300">
        {/* Thumbnail */}
        <div className="relative aspect-video overflow-hidden">
          <img
            src={resource.thumbnail}
            alt={resource.title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />

          {/* Type Badge */}
          <div className={`absolute top-3 left-3 ${typeColors[resource.type]} text-white text-xs font-bold px-3 py-1 rounded-full`}>
            {resource.type}
          </div>

          {/* Duration for videos */}
          {resource.duration && (
            <div className="absolute bottom-3 right-3 bg-black/80 text-white text-xs font-medium px-2 py-1 rounded flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {resource.duration}
            </div>
          )}

          {/* Play button for videos */}
          {resource.type === 'Video' && (
            <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
              <div className="w-16 h-16 rounded-full bg-white/90 flex items-center justify-center shadow-xl">
                <Play className="w-7 h-7 text-primary ml-1" fill="currentColor" />
              </div>
            </div>
          )}
        </div>

        {/* Content */}
        <div className="p-5">
          <h3 className="font-heading text-lg font-bold text-foreground mb-2 line-clamp-2 group-hover:text-primary transition-colors">
            {resource.title}
          </h3>
          <p className="font-paragraph text-sm text-foreground-muted mb-4 line-clamp-2">
            {resource.description}
          </p>

          {/* Meta */}
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-3">
              <span className="flex items-center gap-1 text-amber-500">
                <Star className="w-4 h-4" fill="currentColor" />
                {resource.rating}
              </span>
              <span className="flex items-center gap-1 text-foreground-muted">
                <Eye className="w-4 h-4" />
                {(resource.views / 1000).toFixed(0)}k
              </span>
            </div>
            <span className="text-xs text-foreground-muted">{resource.author}</span>
          </div>

          {/* Tags */}
          <div className="flex flex-wrap gap-2 mt-4">
            {resource.tags.slice(0, 3).map((tag) => (
              <span key={tag} className="text-xs px-2 py-1 bg-secondary rounded-full text-foreground-muted">
                {tag}
              </span>
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  );
}

// ============================================
// GALLERY COMPONENT
// ============================================

function GallerySection() {
  const [selectedImage, setSelectedImage] = useState<GalleryImage | null>(null);

  return (
    <div className="space-y-8">
      {/* Gallery Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        className="text-center"
      >
        <h2 className="font-heading text-3xl font-bold text-foreground mb-4">
          Interview Situational Gallery
        </h2>
        <p className="font-paragraph text-foreground-muted max-w-2xl mx-auto">
          Visual guide to common interview scenarios. Study these situations to prepare for any interview format.
        </p>
      </motion.div>

      {/* Gallery Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
        {GALLERY_IMAGES.map((image, index) => (
          <motion.div
            key={image.id}
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4, delay: index * 0.03 }}
            whileHover={{ scale: 1.05, zIndex: 10 }}
            className="group relative aspect-square rounded-xl overflow-hidden cursor-pointer shadow-lg"
            onClick={() => setSelectedImage(image)}
          >
            <img
              src={image.url}
              alt={image.title}
              className="w-full h-full object-cover"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300">
              <div className="absolute bottom-0 left-0 right-0 p-4">
                <h4 className="font-heading text-sm font-bold text-white mb-1">{image.title}</h4>
                <p className="text-xs text-white/80">{image.description}</p>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Lightbox */}
      <AnimatePresence>
        {selectedImage && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/90 z-50 flex items-center justify-center p-4"
            onClick={() => setSelectedImage(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="relative max-w-4xl w-full"
              onClick={(e) => e.stopPropagation()}
            >
              <img
                src={selectedImage.url}
                alt={selectedImage.title}
                className="w-full rounded-2xl shadow-2xl"
              />
              <div className="absolute bottom-0 left-0 right-0 p-6 bg-gradient-to-t from-black/80 to-transparent rounded-b-2xl">
                <h3 className="font-heading text-2xl font-bold text-white mb-2">{selectedImage.title}</h3>
                <p className="font-paragraph text-white/80">{selectedImage.description}</p>
              </div>
              <button
                onClick={() => setSelectedImage(null)}
                className="absolute top-4 right-4 w-10 h-10 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center text-white hover:bg-white/30 transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// ============================================
// MAIN RESOURCES PAGE COMPONENT
// ============================================

export default function ResourcesPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<string>('all');
  const [isGoogleSearching, setIsGoogleSearching] = useState(false);

  // Filter resources
  const filteredResources = useMemo(() => {
    if (filterType === 'Gallery') return [];

    return RESOURCES.filter(resource => {
      const matchesSearch = searchQuery === '' ||
        resource.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        resource.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        resource.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));

      const matchesFilter = filterType === 'all' || resource.type === filterType;

      return matchesSearch && matchesFilter;
    });
  }, [searchQuery, filterType]);

  // Stats
  const stats = useMemo(() => ({
    videos: RESOURCES.filter(r => r.type === 'Video').length,
    articles: RESOURCES.filter(r => r.type === 'Article').length,
    guides: RESOURCES.filter(r => r.type === 'Guide').length,
    tutorials: RESOURCES.filter(r => r.type === 'Tutorial').length,
    gallery: GALLERY_IMAGES.length,
  }), []);

  // Google Search Handler
  const handleGoogleSearch = () => {
    if (searchQuery.trim()) {
      const query = encodeURIComponent(`interview tips ${searchQuery}`);
      window.open(`https://www.google.com/search?q=${query}`, '_blank');
      setIsGoogleSearching(false);
    }
  };

  const handleSearchKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && isGoogleSearching) {
      handleGoogleSearch();
    }
  };

  const clearFilters = () => {
    setSearchQuery('');
    setFilterType('all');
  };

  const hasActiveFilters = searchQuery !== '' || filterType !== 'all';

  return (
    <div className="min-h-screen bg-background">
      <Header />

      {/* Hero Section */}
      <section className="relative w-full pt-24 pb-16 px-6 lg:px-16 overflow-hidden">
        {/* Background decorations */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-[-20%] right-[-10%] w-[60vw] h-[60vw] rounded-full bg-primary/5 blur-3xl" />
          <div className="absolute bottom-[-30%] left-[-10%] w-[50vw] h-[50vw] rounded-full bg-accent-purple/5 blur-3xl" />
        </div>

        <div className="max-w-[100rem] mx-auto relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center mb-12"
          >
            {/* Eyebrow */}
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2 }}
              className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 rounded-full mb-6"
            >
              <GraduationCap className="w-4 h-4 text-primary" />
              <span className="text-sm font-semibold text-primary">Complete Learning Hub</span>
            </motion.div>

            <h1 className="font-heading text-5xl lg:text-7xl font-black text-foreground mb-6 leading-tight">
              Master Your <span className="bg-gradient-to-r from-primary to-accent-purple bg-clip-text text-transparent">Interview Skills</span>
            </h1>

            <p className="font-paragraph text-lg lg:text-xl text-foreground-muted max-w-3xl mx-auto leading-relaxed">
              {stats.videos}+ videos, {stats.articles} articles, {stats.guides} guides, {stats.tutorials} tutorials,
              and {stats.gallery} situational images to transform you into an interview expert.
            </p>

            {/* Quick stats */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="flex items-center justify-center gap-6 lg:gap-10 mt-10 flex-wrap"
            >
              {[
                { value: `${stats.videos}+`, label: 'Videos', color: 'text-red-500' },
                { value: stats.articles, label: 'Articles', color: 'text-blue-500' },
                { value: stats.guides, label: 'Guides', color: 'text-green-500' },
                { value: stats.tutorials, label: 'Tutorials', color: 'text-purple-500' },
                { value: stats.gallery, label: 'Gallery', color: 'text-pink-500' },
              ].map((stat, i) => (
                <div key={i} className="text-center">
                  <div className={`text-2xl lg:text-3xl font-bold ${stat.color}`}>{stat.value}</div>
                  <div className="text-sm text-foreground-muted">{stat.label}</div>
                </div>
              ))}
            </motion.div>
          </motion.div>

          {/* Enhanced Search with Google Integration */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="mb-10"
          >
            <div className="relative max-w-3xl mx-auto">
              <div className="relative">
                <Search className="absolute left-5 top-1/2 transform -translate-y-1/2 w-5 h-5 text-foreground-muted" />
                <Input
                  type="text"
                  placeholder="Search resources or press Enter for Google search..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={handleSearchKeyDown}
                  onFocus={() => setIsGoogleSearching(true)}
                  className="pl-14 pr-32 h-16 bg-card-bg border-border-color text-foreground text-lg
                             placeholder:text-foreground-muted rounded-2xl font-paragraph
                             shadow-lg focus:border-primary focus:ring-2 focus:ring-primary/20
                             transition-all duration-300"
                />

                {/* Google Search Button */}
                <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-2">
                  {searchQuery && (
                    <button
                      onClick={() => setSearchQuery('')}
                      className="p-2 rounded-lg hover:bg-secondary transition-colors"
                    >
                      <X className="w-4 h-4 text-foreground-muted" />
                    </button>
                  )}
                  <Button
                    onClick={handleGoogleSearch}
                    disabled={!searchQuery.trim()}
                    className="h-10 px-4 bg-gradient-to-r from-primary to-accent-purple text-white rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all disabled:opacity-50"
                  >
                    <Globe className="w-4 h-4 mr-2" />
                    Google
                  </Button>
                </div>
              </div>

              {/* Search hint */}
              {isGoogleSearching && searchQuery && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="absolute top-full left-0 right-0 mt-2 p-3 bg-card-bg border border-border-color rounded-xl shadow-lg"
                >
                  <p className="text-sm text-foreground-muted">
                    Press <kbd className="px-2 py-1 bg-secondary rounded text-xs font-mono">Enter</kbd> or click
                    <span className="text-primary font-semibold"> Google</span> to search the web for interview tips about "{searchQuery}"
                  </p>
                </motion.div>
              )}
            </div>

            {/* Filter Chips */}
            <div className="flex items-center gap-3 flex-wrap justify-center mt-8">
              <span className="text-sm text-foreground-muted font-medium mr-2 flex items-center gap-1">
                <Filter className="w-4 h-4" />
                Filter:
              </span>
              {FILTER_OPTIONS.map((option) => {
                const Icon = option.icon;
                return (
                  <motion.button
                    key={option.value}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => setFilterType(option.value)}
                    className={`
                      flex items-center gap-2 px-4 py-2.5 rounded-xl font-paragraph text-sm font-semibold
                      transition-all duration-300 border
                      ${filterType === option.value
                        ? 'bg-gradient-to-r from-primary to-accent-purple text-white border-transparent shadow-lg shadow-primary/30'
                        : 'bg-card-bg text-foreground border-border-color hover:border-primary/50 hover:shadow-md'
                      }
                    `}
                  >
                    <Icon className="w-4 h-4" />
                    {option.label}
                  </motion.button>
                );
              })}
            </div>
          </motion.div>
        </div>
      </section>

      {/* Main Content */}
      <section className="w-full max-w-[120rem] mx-auto px-6 lg:px-16 pb-24">
        <div className="max-w-[100rem] mx-auto">
          {/* Active filters indicator */}
          {hasActiveFilters && filterType !== 'Gallery' && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center gap-3 mb-8"
            >
              <span className="text-sm text-foreground-muted">
                Showing {filteredResources.length} result{filteredResources.length !== 1 ? 's' : ''}
                {searchQuery && ` for "${searchQuery}"`}
              </span>
              <Button
                variant="ghost"
                size="sm"
                onClick={clearFilters}
                className="text-primary hover:text-primary/80 hover:bg-primary/10"
              >
                <X className="w-4 h-4 mr-1" />
                Clear filters
              </Button>
            </motion.div>
          )}

          {/* Gallery View */}
          {filterType === 'Gallery' ? (
            <GallerySection />
          ) : filteredResources.length > 0 ? (
            /* Resources Grid */
            <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {filteredResources.map((resource, index) => (
                <ResourceCardComponent key={resource.id} resource={resource} index={index} />
              ))}
            </div>
          ) : (
            /* Empty State */
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="text-center py-20"
            >
              <div className="w-24 h-24 mx-auto mb-6 rounded-full bg-secondary flex items-center justify-center">
                <Sparkles className="w-12 h-12 text-primary/60" />
              </div>

              <h3 className="font-heading text-2xl font-bold text-foreground mb-3">
                No results found
              </h3>

              <p className="font-paragraph text-foreground-muted max-w-md mx-auto mb-8 leading-relaxed">
                Try searching for topics like <span className="font-semibold text-primary">confidence</span>,
                <span className="font-semibold text-primary"> STAR method</span>, or
                <span className="font-semibold text-primary"> body language</span>.
              </p>

              <div className="flex items-center justify-center gap-3 flex-wrap mb-6">
                {['Confidence', 'STAR Method', 'Body Language', 'Technical', 'Salary'].map((suggestion) => (
                  <Button
                    key={suggestion}
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setSearchQuery(suggestion);
                      setFilterType('all');
                    }}
                    className="border-border-color text-foreground hover:border-primary/50 hover:bg-primary/5 rounded-lg"
                  >
                    {suggestion}
                    <ChevronRight className="w-3 h-3 ml-1" />
                  </Button>
                ))}
              </div>

              <Button
                onClick={handleGoogleSearch}
                className="bg-gradient-to-r from-primary to-accent-purple text-white"
              >
                <Globe className="w-4 h-4 mr-2" />
                Search on Google
              </Button>
            </motion.div>
          )}
        </div>
      </section>

      <Footer />
    </div>
  );
}
