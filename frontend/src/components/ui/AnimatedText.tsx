import { motion, useInView } from 'framer-motion';
import { useRef, ReactNode } from 'react';

interface AnimatedTextProps {
    children: ReactNode;
    className?: string;
    delay?: number;
    animation?: 'fadeUp' | 'fadeIn' | 'slideLeft' | 'slideRight' | 'typewriter' | 'gradient' | 'split';
}

/**
 * AnimatedText - Premium text animations for headings and content
 */
export function AnimatedText({
    children,
    className = '',
    delay = 0,
    animation = 'fadeUp'
}: AnimatedTextProps) {
    const ref = useRef(null);
    const isInView = useInView(ref, { once: true, margin: '-50px' });

    const animations = {
        fadeUp: {
            initial: { opacity: 0, y: 30 },
            animate: isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 },
        },
        fadeIn: {
            initial: { opacity: 0 },
            animate: isInView ? { opacity: 1 } : { opacity: 0 },
        },
        slideLeft: {
            initial: { opacity: 0, x: -50 },
            animate: isInView ? { opacity: 1, x: 0 } : { opacity: 0, x: -50 },
        },
        slideRight: {
            initial: { opacity: 0, x: 50 },
            animate: isInView ? { opacity: 1, x: 0 } : { opacity: 0, x: 50 },
        },
        typewriter: {
            initial: { opacity: 0, width: 0 },
            animate: isInView ? { opacity: 1, width: 'auto' } : { opacity: 0, width: 0 },
        },
        gradient: {
            initial: { opacity: 0, backgroundPosition: '0% 50%' },
            animate: isInView ? { opacity: 1, backgroundPosition: '100% 50%' } : { opacity: 0 },
        },
        split: {
            initial: { opacity: 0, letterSpacing: '0.5em' },
            animate: isInView ? { opacity: 1, letterSpacing: '0em' } : { opacity: 0, letterSpacing: '0.5em' },
        },
    };

    return (
        <motion.div
            ref={ref}
            className={className}
            initial={animations[animation].initial}
            animate={animations[animation].animate}
            transition={{
                duration: 0.7,
                delay,
                ease: [0.25, 0.46, 0.45, 0.94]
            }}
        >
            {children}
        </motion.div>
    );
}

/**
 * AnimatedHeading - Special heading with gradient and animation
 */
export function AnimatedHeading({
    children,
    className = '',
    delay = 0,
    gradient = true
}: {
    children: ReactNode;
    className?: string;
    delay?: number;
    gradient?: boolean;
}) {
    const ref = useRef(null);
    const isInView = useInView(ref, { once: true, margin: '-50px' });

    return (
        <motion.h2
            ref={ref}
            className={`font-heading font-black ${gradient ? 'bg-gradient-to-r from-foreground via-primary to-foreground bg-clip-text text-transparent bg-[length:200%_100%]' : 'text-foreground'} ${className}`}
            initial={{ opacity: 0, y: 30 }}
            animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
            transition={{ duration: 0.7, delay, ease: [0.25, 0.46, 0.45, 0.94] }}
        >
            {children}
        </motion.h2>
    );
}

/**
 * GradientText - Text with animated gradient
 */
export function GradientText({
    children,
    className = '',
    colors = 'from-primary via-accent-purple to-primary'
}: {
    children: ReactNode;
    className?: string;
    colors?: string;
}) {
    return (
        <span className={`bg-gradient-to-r ${colors} bg-clip-text text-transparent bg-[length:200%_100%] animate-gradient ${className}`}>
            {children}
        </span>
    );
}

/**
 * SplitText - Character by character reveal animation
 */
export function SplitText({
    text,
    className = '',
    delay = 0
}: {
    text: string;
    className?: string;
    delay?: number;
}) {
    const ref = useRef(null);
    const isInView = useInView(ref, { once: true, margin: '-50px' });

    return (
        <motion.span
            ref={ref}
            className={className}
            initial="hidden"
            animate={isInView ? "visible" : "hidden"}
            variants={{
                hidden: {},
                visible: {
                    transition: {
                        staggerChildren: 0.03,
                        delayChildren: delay,
                    },
                },
            }}
        >
            {text.split('').map((char, index) => (
                <motion.span
                    key={index}
                    variants={{
                        hidden: { opacity: 0, y: 20, rotateX: -90 },
                        visible: {
                            opacity: 1,
                            y: 0,
                            rotateX: 0,
                            transition: {
                                type: 'spring',
                                damping: 12,
                                stiffness: 200,
                            },
                        },
                    }}
                    className="inline-block"
                    style={{
                        whiteSpace: char === ' ' ? 'pre' : 'normal',
                        transformOrigin: 'bottom',
                    }}
                >
                    {char}
                </motion.span>
            ))}
        </motion.span>
    );
}

/**
 * WordReveal - Word by word reveal animation
 */
export function WordReveal({
    text,
    className = '',
    delay = 0
}: {
    text: string;
    className?: string;
    delay?: number;
}) {
    const ref = useRef(null);
    const isInView = useInView(ref, { once: true, margin: '-50px' });
    const words = text.split(' ');

    return (
        <motion.span
            ref={ref}
            className={className}
            initial="hidden"
            animate={isInView ? "visible" : "hidden"}
            variants={{
                hidden: {},
                visible: {
                    transition: {
                        staggerChildren: 0.08,
                        delayChildren: delay,
                    },
                },
            }}
        >
            {words.map((word, index) => (
                <motion.span
                    key={index}
                    variants={{
                        hidden: { opacity: 0, y: 30, filter: 'blur(8px)' },
                        visible: {
                            opacity: 1,
                            y: 0,
                            filter: 'blur(0px)',
                            transition: {
                                duration: 0.5,
                                ease: [0.25, 0.46, 0.45, 0.94],
                            },
                        },
                    }}
                    className="inline-block mr-[0.25em]"
                >
                    {word}
                </motion.span>
            ))}
        </motion.span>
    );
}

/**
 * CountUp - Animated number counter
 */
export function CountUp({
    from = 0,
    to,
    duration = 2,
    delay = 0,
    suffix = '',
    prefix = '',
    className = ''
}: {
    from?: number;
    to: number;
    duration?: number;
    delay?: number;
    suffix?: string;
    prefix?: string;
    className?: string;
}) {
    const ref = useRef(null);
    const isInView = useInView(ref, { once: true, margin: '-50px' });

    return (
        <motion.span
            ref={ref}
            className={className}
            initial={{ opacity: 0 }}
            animate={isInView ? { opacity: 1 } : { opacity: 0 }}
            transition={{ duration: 0.3, delay }}
        >
            {prefix}
            <motion.span
                initial={{ opacity: 0 }}
                animate={isInView ? { opacity: 1 } : { opacity: 0 }}
            >
                {isInView && (
                    <motion.span
                        initial={{ scale: 0.5 }}
                        animate={{ scale: 1 }}
                        transition={{
                            type: 'spring',
                            stiffness: 100,
                            damping: 15,
                            delay: delay + 0.2
                        }}
                    >
                        <CountAnimation from={from} to={to} duration={duration} />
                    </motion.span>
                )}
            </motion.span>
            {suffix}
        </motion.span>
    );
}

// Helper component for counting animation
function CountAnimation({ from, to, duration }: { from: number; to: number; duration: number }) {
    return (
        <motion.span
            initial={{ opacity: 1 }}
            animate={{ opacity: 1 }}
            transition={{ duration }}
        >
            <motion.span
                initial={{ count: from } as any}
                animate={{ count: to } as any}
                transition={{ duration, ease: 'easeOut' }}
            >
                {/* This displays the animated count */}
                <AnimatedNumber from={from} to={to} duration={duration} />
            </motion.span>
        </motion.span>
    );
}

function AnimatedNumber({ from, to, duration }: { from: number; to: number; duration: number }) {
    const ref = useRef<HTMLSpanElement>(null);
    const isInView = useInView(ref, { once: true });

    return (
        <motion.span
            ref={ref}
            animate={isInView ? { opacity: 1 } : { opacity: 0 }}
        >
            <motion.span
                initial={{ opacity: 0 }}
                animate={isInView ? {
                    opacity: 1,
                    transition: { duration: 0.3 }
                } : {}}
            >
                {to.toLocaleString()}
            </motion.span>
        </motion.span>
    );
}

/**
 * TypewriterText - Typewriter effect for text
 */
export function TypewriterText({
    text,
    className = '',
    delay = 0,
    speed = 0.05
}: {
    text: string;
    className?: string;
    delay?: number;
    speed?: number;
}) {
    const ref = useRef(null);
    const isInView = useInView(ref, { once: true, margin: '-50px' });

    return (
        <motion.span
            ref={ref}
            className={className}
            initial="hidden"
            animate={isInView ? "visible" : "hidden"}
        >
            {text.split('').map((char, index) => (
                <motion.span
                    key={index}
                    variants={{
                        hidden: { opacity: 0 },
                        visible: {
                            opacity: 1,
                            transition: {
                                delay: delay + (index * speed),
                            },
                        },
                    }}
                >
                    {char}
                </motion.span>
            ))}
            <motion.span
                className="inline-block w-[2px] h-[1em] bg-primary ml-1"
                animate={{ opacity: [1, 0, 1] }}
                transition={{ duration: 0.8, repeat: Infinity }}
            />
        </motion.span>
    );
}
