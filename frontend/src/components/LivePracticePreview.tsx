/**
 * LivePracticePreview Component
 * 
 * Premium section showcasing the live interview practice interface
 * with a laptop mockup and descriptive text below.
 */
import React from 'react';
import { motion } from 'framer-motion';
import { Play, Video, Code, MessageSquare, Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';

const LivePracticePreview = () => {
    return (
        <section className="relative py-24 bg-background overflow-hidden">
            {/* Background decorations */}
            <div className="absolute inset-0 grid-pattern pointer-events-none opacity-30" />
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[1000px] h-[600px] bg-primary/5 dark:bg-primary/10 rounded-full blur-[150px] pointer-events-none" />

            <div className="max-w-6xl mx-auto px-6 lg:px-12 relative z-10">
                {/* Section Header */}
                <motion.div
                    className="text-center mb-16"
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6 }}
                >
                    <h2 className="font-heading text-4xl lg:text-5xl font-black text-foreground dark:text-white mb-4">
                        Get Real{' '}
                        <span className="text-primary">Interview Practice</span>
                    </h2>

                    <p className="font-paragraph text-lg text-foreground-muted dark:text-foreground/70 max-w-3xl mx-auto">
                        Acing job interviews requires many skills: problem-solving, communication,
                        product sensibility, and strong technical aptitude. There's one certain way
                        to get dramatically better: <strong className="text-foreground dark:text-white">Practicing Live Interviews.</strong>
                    </p>
                </motion.div>

                {/* Laptop Mockup */}
                <motion.div
                    className="relative max-w-4xl mx-auto"
                    initial={{ opacity: 0, y: 50 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.8, delay: 0.2 }}
                >
                    {/* Laptop Frame */}
                    <div className="relative">
                        {/* Screen bezel */}
                        <div className="bg-gradient-to-b from-gray-700 to-gray-800 dark:from-gray-600 dark:to-gray-700 rounded-t-2xl pt-3 px-3 pb-0">
                            {/* Camera notch */}
                            <div className="absolute top-1.5 left-1/2 -translate-x-1/2 w-2 h-2 rounded-full bg-gray-500" />

                            {/* Screen */}
                            <div className="bg-gray-900 rounded-t-lg overflow-hidden shadow-2xl">
                                {/* Browser bar */}
                                <div className="bg-gray-800 px-4 py-2 flex items-center gap-3">
                                    <div className="flex gap-1.5">
                                        <div className="w-3 h-3 rounded-full bg-red-400" />
                                        <div className="w-3 h-3 rounded-full bg-yellow-400" />
                                        <div className="w-3 h-3 rounded-full bg-green-400" />
                                    </div>
                                    <div className="flex-1 bg-gray-700 rounded-md px-3 py-1 text-xs text-gray-400 flex items-center gap-2">
                                        <span className="truncate">https://interviewpro.ai/practice</span>
                                    </div>
                                </div>

                                {/* App interface mockup */}
                                <div className="aspect-[16/9] bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 relative">
                                    {/* Split view layout */}
                                    <div className="absolute inset-0 flex">
                                        {/* Left side - Question/Code panel */}
                                        <div className="w-1/2 border-r border-gray-700 p-4 flex flex-col">
                                            {/* Toolbar */}
                                            <div className="flex items-center gap-2 mb-4">
                                                <div className="px-3 py-1 bg-emerald-600 text-white text-xs rounded font-bold">DASHBOARD</div>
                                                <div className="px-3 py-1 bg-amber-500 text-black text-xs rounded font-bold">SWAP ROLES</div>
                                            </div>

                                            {/* Question tabs */}
                                            <div className="flex gap-2 mb-4">
                                                <div className="px-3 py-1 bg-gray-700 text-white text-xs rounded">QUESTION</div>
                                                <div className="px-3 py-1 text-gray-400 text-xs">HINTS</div>
                                                <div className="px-3 py-1 text-gray-400 text-xs">ANSWER</div>
                                            </div>

                                            {/* Question title */}
                                            <h3 className="text-white font-bold text-lg mb-2">Anonymous Love Letter</h3>

                                            {/* Question description placeholder */}
                                            <div className="flex-1 space-y-2">
                                                <div className="h-2 bg-gray-700 rounded w-full" />
                                                <div className="h-2 bg-gray-700 rounded w-5/6" />
                                                <div className="h-2 bg-gray-700 rounded w-4/6" />
                                                <div className="h-2 bg-gray-700 rounded w-full" />
                                                <div className="h-2 bg-gray-700 rounded w-3/6" />

                                                {/* Code snippet */}
                                                <div className="mt-4 bg-gray-800 rounded p-3 space-y-1.5">
                                                    <div className="h-2 bg-blue-400/30 rounded w-4/6" />
                                                    <div className="h-2 bg-green-400/30 rounded w-5/6" />
                                                    <div className="h-2 bg-purple-400/30 rounded w-3/6" />
                                                    <div className="h-2 bg-yellow-400/30 rounded w-4/6" />
                                                </div>
                                            </div>
                                        </div>

                                        {/* Right side - Code & Video panel */}
                                        <div className="w-1/2 p-4 flex flex-col">
                                            {/* Code editor header */}
                                            <div className="flex items-center gap-2 mb-2">
                                                <Code className="w-4 h-4 text-gray-400" />
                                                <span className="text-xs text-gray-400">Python</span>
                                                <div className="ml-auto px-2 py-0.5 bg-gray-700 text-gray-300 text-xs rounded">Reset</div>
                                            </div>

                                            {/* Code editor */}
                                            <div className="flex-1 bg-gray-800 rounded-lg p-3 mb-4 font-mono text-xs space-y-1">
                                                <div className="flex">
                                                    <span className="text-gray-500 w-6">1</span>
                                                    <span className="text-blue-400">from</span>
                                                    <span className="text-white ml-1">collections</span>
                                                    <span className="text-blue-400 ml-1">import</span>
                                                    <span className="text-yellow-300 ml-1">Counter</span>
                                                </div>
                                                <div className="flex">
                                                    <span className="text-gray-500 w-6">2</span>
                                                    <span className="text-gray-600"># Your solution here</span>
                                                </div>
                                                <div className="flex">
                                                    <span className="text-gray-500 w-6">3</span>
                                                    <span className="text-purple-400">def</span>
                                                    <span className="text-yellow-300 ml-1">solve</span>
                                                    <span className="text-white">(letter, chars):</span>
                                                </div>
                                                <div className="flex">
                                                    <span className="text-gray-500 w-6">4</span>
                                                    <span className="text-white ml-4">...</span>
                                                </div>
                                            </div>

                                            {/* Video feeds */}
                                            <div className="flex gap-2">
                                                <div className="flex-1 aspect-video bg-gradient-to-br from-gray-700 to-gray-800 rounded-lg relative overflow-hidden flex items-center justify-center">
                                                    <Video className="w-6 h-6 text-gray-500" />
                                                    <div className="absolute bottom-1 left-1 px-1.5 py-0.5 bg-emerald-500 text-white text-[10px] rounded flex items-center gap-1">
                                                        <div className="w-1.5 h-1.5 bg-white rounded-full animate-pulse" />
                                                        You
                                                    </div>
                                                </div>
                                                <div className="flex-1 aspect-video bg-gradient-to-br from-gray-700 to-gray-800 rounded-lg relative overflow-hidden flex items-center justify-center">
                                                    <Video className="w-6 h-6 text-gray-500" />
                                                    <div className="absolute bottom-1 left-1 px-1.5 py-0.5 bg-blue-500 text-white text-[10px] rounded flex items-center gap-1">
                                                        <div className="w-1.5 h-1.5 bg-white rounded-full animate-pulse" />
                                                        Peer
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Live indicator */}
                                    <div className="absolute top-3 right-3 flex items-center gap-2 px-2 py-1 bg-red-600/90 rounded-full">
                                        <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
                                        <span className="text-white text-xs font-bold">LIVE</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Laptop base */}
                        <div className="relative h-4 bg-gradient-to-b from-gray-600 to-gray-700 dark:from-gray-500 dark:to-gray-600 rounded-b-xl">
                            {/* Trackpad indent */}
                            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-24 h-1 bg-gray-500 rounded-b-full" />
                        </div>

                        {/* Laptop shadow */}
                        <div className="absolute -bottom-4 left-1/2 -translate-x-1/2 w-[90%] h-4 bg-gradient-to-b from-black/20 to-transparent blur-md rounded-full" />
                    </div>
                </motion.div>

                {/* Text Below Laptop */}
                <motion.div
                    className="text-center mt-16"
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6, delay: 0.4 }}
                >
                    {/* Feature highlights */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-3xl mx-auto mb-10">
                        <div className="flex items-center gap-3 justify-center">
                            <div className="w-10 h-10 rounded-full bg-primary/10 dark:bg-primary/20 flex items-center justify-center">
                                <MessageSquare className="w-5 h-5 text-primary" />
                            </div>
                            <span className="font-paragraph font-semibold text-foreground dark:text-white">Real-time Feedback</span>
                        </div>
                        <div className="flex items-center gap-3 justify-center">
                            <div className="w-10 h-10 rounded-full bg-primary/10 dark:bg-primary/20 flex items-center justify-center">
                                <Video className="w-5 h-5 text-primary" />
                            </div>
                            <span className="font-paragraph font-semibold text-foreground dark:text-white">Video Analysis</span>
                        </div>
                        <div className="flex items-center gap-3 justify-center">
                            <div className="w-10 h-10 rounded-full bg-primary/10 dark:bg-primary/20 flex items-center justify-center">
                                <Sparkles className="w-5 h-5 text-primary" />
                            </div>
                            <span className="font-paragraph font-semibold text-foreground dark:text-white">AI-Powered Insights</span>
                        </div>
                    </div>

                    {/* Description */}
                    <p className="font-paragraph text-foreground-muted dark:text-foreground/70 max-w-2xl mx-auto mb-8">
                        Practice coding interviews, behavioral questions, and system design with our AI-powered platform.
                        Get instant feedback on your communication, body language, and technical accuracy.
                    </p>

                    {/* CTA Button */}
                    <Link to="/practice">
                        <Button className="bg-primary text-white hover:bg-accent-purple px-8 py-6 text-lg font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 group">
                            <Play className="w-5 h-5 mr-2 group-hover:scale-110 transition-transform" />
                            Start Practicing Now
                        </Button>
                    </Link>
                </motion.div>
            </div>
        </section>
    );
};

export default LivePracticePreview;
