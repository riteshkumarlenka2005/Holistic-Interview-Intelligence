/**
 * Intelligence Interlude Section
 * 
 * A non-intrusive, full-width narrative section featuring illustrated boards
 * with presenters and subtle, research-grade motion animations.
 * Designed to reinforce multimodal intelligence, fairness, and reflective learning.
 */
import React, { useRef } from 'react';
import { motion, useScroll, useTransform, useSpring, useInView } from 'framer-motion';

// --- BOARD DATA ---
const insightBoards = [
    {
        id: 1,
        mainText: "Interviews are not evaluated only by answers.",
        microCaption: "They're judged by behavior you rarely notice.",
        keywords: [],
        presenterSide: 'right' as const,
    },
    {
        id: 2,
        mainText: "Human communication is multimodal.",
        microCaption: null,
        keywords: ["Voice", "Expression", "Eye contact", "Posture", "Timing"],
        presenterSide: 'left' as const,
    },
    {
        id: 3,
        mainText: "Our AI observes synchrony — not isolated signals.",
        microCaption: "Because confidence is a pattern, not a metric.",
        keywords: [],
        presenterSide: 'right' as const,
    },
    {
        id: 4,
        mainText: "Designed for fairness, clarity, and self-improvement.",
        microCaption: null,
        keywords: ["Explainable", "Bias-aware", "Privacy-first", "SDG-4 aligned"],
        presenterSide: 'left' as const,
    },
    {
        id: 5,
        mainText: "Practice with intelligence. Reflect with clarity.",
        microCaption: null,
        keywords: [],
        presenterSide: 'center' as const,
    },
];

// --- PRESENTER ILLUSTRATIONS ---
// Bold strokes for 100% visibility in both light and dark themes
const PresenterMale = ({ className = "" }: { className?: string }) => (
    <svg viewBox="0 0 200 280" className={className} fill="none" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
        {/* Head */}
        <circle cx="100" cy="60" r="35" className="stroke-primary dark:stroke-primary-light" />
        {/* Eyes */}
        <circle cx="88" cy="55" r="5" className="fill-primary dark:fill-primary-light" />
        <circle cx="112" cy="55" r="5" className="fill-primary dark:fill-primary-light" />
        {/* Smile */}
        <path d="M90 72 Q100 82 110 72" className="stroke-primary dark:stroke-primary-light" strokeWidth="2.5" />
        {/* Body - Suit */}
        <path d="M65 95 L55 200" className="stroke-foreground dark:stroke-white" />
        <path d="M135 95 L145 200" className="stroke-foreground dark:stroke-white" />
        <path d="M65 95 Q100 115 135 95" className="stroke-foreground dark:stroke-white" />
        {/* Tie */}
        <path d="M100 95 L95 130 L100 140 L105 130 L100 95" className="stroke-primary fill-primary/30 dark:stroke-primary-light dark:fill-primary/40" strokeWidth="2" />
        {/* Arm pointing */}
        <path d="M135 120 Q170 110 180 95" className="stroke-foreground dark:stroke-white" />
        <circle cx="185" cy="92" r="10" className="stroke-foreground dark:stroke-white" />
        {/* Other arm */}
        <path d="M65 120 Q50 140 55 170" className="stroke-foreground dark:stroke-white" />
        {/* Legs */}
        <path d="M85 200 L80 275" className="stroke-foreground dark:stroke-white" />
        <path d="M115 200 L120 275" className="stroke-foreground dark:stroke-white" />
    </svg>
);

const PresenterFemale = ({ className = "" }: { className?: string }) => (
    <svg viewBox="0 0 200 280" className={className} fill="none" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
        {/* Head */}
        <circle cx="100" cy="55" r="32" className="stroke-primary dark:stroke-primary-light" />
        {/* Hair */}
        <path d="M68 45 Q70 20 100 25 Q130 20 132 45" className="stroke-foreground dark:stroke-white" />
        <path d="M68 45 Q60 70 65 85" className="stroke-foreground dark:stroke-white" />
        <path d="M132 45 Q140 70 135 85" className="stroke-foreground dark:stroke-white" />
        {/* Eyes */}
        <circle cx="88" cy="50" r="5" className="fill-primary dark:fill-primary-light" />
        <circle cx="112" cy="50" r="5" className="fill-primary dark:fill-primary-light" />
        {/* Smile */}
        <path d="M90 68 Q100 77 110 68" className="stroke-primary dark:stroke-primary-light" strokeWidth="2.5" />
        {/* Body - Blazer */}
        <path d="M68 87 L58 180" className="stroke-foreground dark:stroke-white" />
        <path d="M132 87 L142 180" className="stroke-foreground dark:stroke-white" />
        <path d="M68 87 Q100 105 132 87" className="stroke-foreground dark:stroke-white" />
        {/* Collar */}
        <path d="M88 87 L100 100 L112 87" className="stroke-primary dark:stroke-primary-light" strokeWidth="2" />
        {/* Arm presenting */}
        <path d="M68 110 Q35 95 25 105 L15 100" className="stroke-foreground dark:stroke-white" />
        <path d="M15 95 L15 100 L20 102" className="stroke-foreground dark:stroke-white" strokeWidth="2.5" />
        {/* Other arm */}
        <path d="M132 110 Q150 130 145 160" className="stroke-foreground dark:stroke-white" />
        {/* Skirt */}
        <path d="M70 180 L65 240" className="stroke-foreground dark:stroke-white" />
        <path d="M130 180 L135 240" className="stroke-foreground dark:stroke-white" />
        <path d="M70 180 Q100 185 130 180" className="stroke-foreground dark:stroke-white" />
        {/* Legs */}
        <path d="M80 240 L78 275" className="stroke-foreground dark:stroke-white" />
        <path d="M120 240 L122 275" className="stroke-foreground dark:stroke-white" />
    </svg>
);


// --- INSIGHT BOARD COMPONENT ---
interface InsightBoardProps {
    board: typeof insightBoards[0];
    index: number;
}

const InsightBoard = ({ board, index }: InsightBoardProps) => {
    const ref = useRef<HTMLDivElement>(null);
    const isInView = useInView(ref, { once: false, margin: "-20% 0px -20% 0px" });

    // Staggered keyword animation
    const keywordVariants = {
        hidden: { opacity: 0, y: 20 },
        visible: (i: number) => ({
            opacity: 1,
            y: 0,
            transition: {
                delay: 0.5 + (i * 0.15),
                duration: 0.6,
                ease: [0.25, 0.46, 0.45, 0.94] as [number, number, number, number],
            },
        }),
    };

    // Spring config for smooth, confident motion
    const springConfig = { stiffness: 100, damping: 30, mass: 1 };

    const isCenter = board.presenterSide === 'center';
    const isLeft = board.presenterSide === 'left';

    return (
        <motion.div
            ref={ref}
            className={`relative flex items-center justify-center min-h-[35vh] py-6 px-6 lg:px-12 ${index % 2 === 0 ? 'bg-transparent' : 'bg-secondary/5'
                }`}
            initial={{ opacity: 0 }}
            animate={isInView ? { opacity: 1 } : { opacity: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
        >
            <div className={`max-w-6xl mx-auto w-full flex items-center gap-8 lg:gap-16 ${isCenter ? 'flex-col text-center' : isLeft ? 'flex-row-reverse' : 'flex-row'
                }`}>

                {/* Presenter Illustration */}
                {!isCenter && (
                    <motion.div
                        className="hidden lg:block w-48 flex-shrink-0"
                        initial={{ opacity: 0, x: isLeft ? 50 : -50 }}
                        animate={isInView ? { opacity: 1, x: 0 } : { opacity: 0, x: isLeft ? 50 : -50 }}
                        transition={{ duration: 0.8, delay: 0.2, ...springConfig }}
                    >
                        {index % 2 === 0 ? (
                            <PresenterMale className="w-full h-auto" />
                        ) : (
                            <PresenterFemale className="w-full h-auto" />
                        )}
                    </motion.div>
                )}

                {/* Content Board */}
                <motion.div
                    className={`flex-1 ${isCenter ? 'max-w-3xl' : ''}`}
                    initial={{ opacity: 0, y: 30 }}
                    animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
                    transition={{ duration: 0.7, delay: 0.1, ease: [0.25, 0.46, 0.45, 0.94] }}
                >
                    {/* Main Quote Board */}
                    <div className="relative bg-card-bg/80 backdrop-blur-sm border border-border-color/50 rounded-2xl p-8 lg:p-12 shadow-sm">
                        {/* Subtle decorative corner */}
                        <div className="absolute top-0 left-0 w-16 h-16 border-t-2 border-l-2 border-primary/20 rounded-tl-2xl" />
                        <div className="absolute bottom-0 right-0 w-16 h-16 border-b-2 border-r-2 border-primary/20 rounded-br-2xl" />

                        {/* Main Text */}
                        <motion.h3
                            className={`font-heading text-2xl lg:text-4xl font-bold text-foreground leading-snug ${isCenter ? 'text-center' : ''
                                }`}
                            initial={{ opacity: 0, y: 20 }}
                            animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
                            transition={{ duration: 0.6, delay: 0.3 }}
                        >
                            {board.mainText}
                        </motion.h3>

                        {/* Micro Caption */}
                        {board.microCaption && (
                            <motion.p
                                className={`mt-4 font-paragraph text-base lg:text-lg text-foreground-muted italic ${isCenter ? 'text-center' : ''
                                    }`}
                                initial={{ opacity: 0, y: 15 }}
                                animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 15 }}
                                transition={{ duration: 0.6, delay: 0.5 }}
                            >
                                {board.microCaption}
                            </motion.p>
                        )}

                        {/* Animated Keywords */}
                        {board.keywords.length > 0 && (
                            <div className={`mt-8 flex flex-wrap gap-3 ${isCenter ? 'justify-center' : ''}`}>
                                {board.keywords.map((keyword, i) => (
                                    <motion.span
                                        key={keyword}
                                        custom={i}
                                        variants={keywordVariants}
                                        initial="hidden"
                                        animate={isInView ? "visible" : "hidden"}
                                        className="px-4 py-2 bg-primary/5 border border-primary/20 rounded-full font-paragraph text-sm text-primary font-medium"
                                    >
                                        {keyword}
                                    </motion.span>
                                ))}
                            </div>
                        )}
                    </div>
                </motion.div>

                {/* Center presenter (for closing board) */}
                {isCenter && (
                    <motion.div
                        className="w-32 mt-8"
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={isInView ? { opacity: 1, scale: 1 } : { opacity: 0, scale: 0.9 }}
                        transition={{ duration: 0.6, delay: 0.4 }}
                    >
                        <div className="flex gap-4 justify-center">
                            <PresenterMale className="w-16 h-auto opacity-50" />
                            <PresenterFemale className="w-16 h-auto opacity-50" />
                        </div>
                    </motion.div>
                )}
            </div>
        </motion.div>
    );
};

// --- MAIN COMPONENT ---
const IntelligenceInterlude = () => {
    const sectionRef = useRef<HTMLElement>(null);
    const { scrollYProgress } = useScroll({
        target: sectionRef,
        offset: ["start end", "end start"],
    });

    // Subtle parallax for background elements
    const bgY = useTransform(scrollYProgress, [0, 1], ["0%", "10%"]);
    const bgOpacity = useTransform(scrollYProgress, [0, 0.1, 0.9, 1], [0, 1, 1, 0]);

    return (
        <section
            ref={sectionRef}
            className="relative w-full overflow-hidden"
            aria-label="Intelligence Insights"
        >
            {/* Soft ambient background */}
            <motion.div
                className="absolute inset-0 pointer-events-none"
                style={{ y: bgY, opacity: bgOpacity }}
            >
                <div className="absolute top-1/4 left-[-10%] w-[40vw] h-[40vw] bg-primary/3 rounded-full blur-[150px]" />
                <div className="absolute bottom-1/4 right-[-10%] w-[35vw] h-[35vw] bg-accent-light/5 rounded-full blur-[150px]" />
            </motion.div>

            {/* Section header - subtle introduction */}
            <motion.div
                className="relative py-16 text-center px-6"
                initial={{ opacity: 0 }}
                whileInView={{ opacity: 1 }}
                viewport={{ once: true, margin: "-100px" }}
                transition={{ duration: 1 }}
            >
                <div className="inline-flex items-center gap-2 px-4 py-2 bg-secondary/50 border border-border-color/30 rounded-full mb-4">
                    <div className="w-1.5 h-1.5 bg-primary/60 rounded-full" />
                    <span className="font-paragraph text-xs text-foreground-muted tracking-wider uppercase">
                        Understanding Intelligence
                    </span>
                </div>
            </motion.div>

            {/* Insight Boards */}
            <div className="relative">
                {insightBoards.map((board, index) => (
                    <InsightBoard key={board.id} board={board} index={index} />
                ))}
            </div>

            {/* Soft exit gradient */}
            <div className="h-24 bg-gradient-to-b from-transparent to-background" />
        </section>
    );
};

export default IntelligenceInterlude;
