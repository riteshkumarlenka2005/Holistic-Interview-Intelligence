import { motion, AnimatePresence } from 'framer-motion';
import { useLocation } from 'react-router-dom';
import { ReactNode, useEffect, useState } from 'react';

interface PageTransitionProps {
    children: ReactNode;
}

// Premium page transition variants
const pageVariants: any = {
    initial: {
        opacity: 0,
        y: 30,
        scale: 0.98,
    },
    animate: {
        opacity: 1,
        y: 0,
        scale: 1,
        transition: {
            duration: 0.6,
            ease: [0.25, 0.46, 0.45, 0.94] as [number, number, number, number],
            staggerChildren: 0.1,
        },
    },
    exit: {
        opacity: 0,
        y: -20,
        scale: 0.99,
        transition: {
            duration: 0.4,
            ease: [0.25, 0.46, 0.45, 0.94] as [number, number, number, number],
        },
    },
};

// Stagger container for child elements
const containerVariants = {
    initial: { opacity: 0 },
    animate: {
        opacity: 1,
        transition: {
            staggerChildren: 0.08,
            delayChildren: 0.1,
        },
    },
};

// Child element animations
const itemVariants: any = {
    initial: { opacity: 0, y: 20 },
    animate: {
        opacity: 1,
        y: 0,
        transition: {
            duration: 0.5,
            ease: [0.25, 0.46, 0.45, 0.94] as [number, number, number, number],
        },
    },
};

// Fade variants for subtle transitions
const fadeVariants = {
    initial: { opacity: 0 },
    animate: {
        opacity: 1,
        transition: { duration: 0.5, ease: 'easeOut' },
    },
    exit: {
        opacity: 0,
        transition: { duration: 0.3, ease: 'easeIn' },
    },
};

// Slide variants for directional transitions
const slideVariants = {
    initial: { opacity: 0, x: 60 },
    animate: {
        opacity: 1,
        x: 0,
        transition: {
            duration: 0.6,
            ease: [0.25, 0.46, 0.45, 0.94],
        },
    },
    exit: {
        opacity: 0,
        x: -60,
        transition: {
            duration: 0.4,
            ease: [0.25, 0.46, 0.45, 0.94],
        },
    },
};

// Scale variants for zoom effect
const scaleVariants = {
    initial: { opacity: 0, scale: 0.9 },
    animate: {
        opacity: 1,
        scale: 1,
        transition: {
            duration: 0.5,
            ease: [0.34, 1.56, 0.64, 1], // Bouncy
        },
    },
    exit: {
        opacity: 0,
        scale: 1.05,
        transition: {
            duration: 0.3,
            ease: 'easeIn',
        },
    },
};

/**
 * PageTransition - Wraps page content with premium animated transitions
 */
export function PageTransition({ children }: PageTransitionProps) {
    const location = useLocation();

    return (
        <AnimatePresence mode="wait">
            <motion.div
                key={location.pathname}
                variants={pageVariants}
                initial="initial"
                animate="animate"
                exit="exit"
                className="w-full"
            >
                {children}
            </motion.div>
        </AnimatePresence>
    );
}

/**
 * FadeIn - Simple fade animation wrapper
 */
export function FadeIn({ children, delay = 0 }: { children: ReactNode; delay?: number }) {
    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay, ease: 'easeOut' }}
        >
            {children}
        </motion.div>
    );
}

/**
 * SlideUp - Slide up from bottom with fade
 */
export function SlideUp({ children, delay = 0 }: { children: ReactNode; delay?: number }) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay, ease: [0.25, 0.46, 0.45, 0.94] }}
        >
            {children}
        </motion.div>
    );
}

/**
 * SlideIn - Slide in from side with fade
 */
export function SlideIn({
    children,
    delay = 0,
    direction = 'left'
}: {
    children: ReactNode;
    delay?: number;
    direction?: 'left' | 'right';
}) {
    const x = direction === 'left' ? -60 : 60;

    return (
        <motion.div
            initial={{ opacity: 0, x }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay, ease: [0.25, 0.46, 0.45, 0.94] }}
        >
            {children}
        </motion.div>
    );
}

/**
 * ScaleIn - Scale up with bounce effect
 */
export function ScaleIn({ children, delay = 0 }: { children: ReactNode; delay?: number }) {
    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay, ease: [0.34, 1.56, 0.64, 1] }}
        >
            {children}
        </motion.div>
    );
}

/**
 * StaggerContainer - Container for staggered child animations
 */
export function StaggerContainer({ children, delay = 0 }: { children: ReactNode; delay?: number }) {
    return (
        <motion.div
            initial="initial"
            animate="animate"
            variants={{
                initial: { opacity: 0 },
                animate: {
                    opacity: 1,
                    transition: {
                        staggerChildren: 0.1,
                        delayChildren: delay,
                    },
                },
            }}
        >
            {children}
        </motion.div>
    );
}

/**
 * StaggerItem - Child item for staggered animations
 */
export function StaggerItem({ children }: { children: ReactNode }) {
    return (
        <motion.div variants={itemVariants}>
            {children}
        </motion.div>
    );
}

/**
 * TextReveal - Character by character text reveal
 */
export function TextReveal({ text, delay = 0 }: { text: string; delay?: number }) {
    return (
        <motion.span
            initial="initial"
            animate="animate"
            variants={{
                initial: {},
                animate: {
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
                        initial: { opacity: 0, y: 20 },
                        animate: { opacity: 1, y: 0 },
                    }}
                    className="inline-block"
                    style={{ whiteSpace: char === ' ' ? 'pre' : 'normal' }}
                >
                    {char}
                </motion.span>
            ))}
        </motion.span>
    );
}

/**
 * HoverScale - Interactive hover scale effect
 */
export function HoverScale({
    children,
    scale = 1.05
}: {
    children: ReactNode;
    scale?: number;
}) {
    return (
        <motion.div
            whileHover={{ scale }}
            whileTap={{ scale: 0.98 }}
            transition={{ type: 'spring', stiffness: 400, damping: 17 }}
        >
            {children}
        </motion.div>
    );
}

/**
 * Float - Continuous floating animation
 */
export function Float({
    children,
    duration = 4,
    y = 10
}: {
    children: ReactNode;
    duration?: number;
    y?: number;
}) {
    return (
        <motion.div
            animate={{ y: [-y / 2, y / 2, -y / 2] }}
            transition={{ duration, repeat: Infinity, ease: 'easeInOut' }}
        >
            {children}
        </motion.div>
    );
}

/**
 * Pulse - Subtle pulse glow animation
 */
export function Pulse({ children }: { children: ReactNode }) {
    return (
        <motion.div
            animate={{ scale: [1, 1.02, 1] }}
            transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
        >
            {children}
        </motion.div>
    );
}

/**
 * InView - Animate when element comes into view
 */
export function InView({
    children,
    animation = 'slideUp'
}: {
    children: ReactNode;
    animation?: 'slideUp' | 'fade' | 'scale' | 'slideLeft' | 'slideRight';
}) {
    const animations = {
        slideUp: { opacity: 0, y: 40 },
        fade: { opacity: 0 },
        scale: { opacity: 0, scale: 0.9 },
        slideLeft: { opacity: 0, x: -40 },
        slideRight: { opacity: 0, x: 40 },
    };

    return (
        <motion.div
            initial={animations[animation]}
            whileInView={{ opacity: 1, y: 0, x: 0, scale: 1 }}
            viewport={{ once: true, margin: '-100px' }}
            transition={{ duration: 0.6, ease: [0.25, 0.46, 0.45, 0.94] }}
        >
            {children}
        </motion.div>
    );
}

// Export variants for custom use
export { pageVariants, containerVariants, itemVariants, fadeVariants, slideVariants, scaleVariants };
