import { motion } from 'framer-motion';
import { ReactNode } from 'react';

interface AnimatedCardProps {
    children: ReactNode;
    className?: string;
    delay?: number;
    hoverEffect?: 'lift' | 'glow' | 'scale' | 'tilt' | 'none';
}

/**
 * AnimatedCard - Premium animated card wrapper with various hover effects
 */
export function AnimatedCard({
    children,
    className = '',
    delay = 0,
    hoverEffect = 'lift'
}: AnimatedCardProps) {
    // Define hover animations based on effect type
    const hoverAnimations = {
        lift: {
            y: -8,
            boxShadow: '0 20px 40px rgba(0, 0, 0, 0.15), 0 10px 20px rgba(91, 76, 217, 0.1)',
        },
        glow: {
            boxShadow: '0 0 30px rgba(91, 76, 217, 0.3), 0 10px 30px rgba(0, 0, 0, 0.1)',
        },
        scale: {
            scale: 1.02,
            boxShadow: '0 15px 35px rgba(0, 0, 0, 0.12)',
        },
        tilt: {
            rotateX: 5,
            rotateY: 5,
            boxShadow: '0 15px 35px rgba(0, 0, 0, 0.15)',
        },
        none: {},
    };

    return (
        <motion.div
            className={className}
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-50px' }}
            transition={{
                duration: 0.6,
                delay,
                ease: [0.25, 0.46, 0.45, 0.94]
            }}
            whileHover={hoverAnimations[hoverEffect]}
            style={{ transformStyle: 'preserve-3d' }}
        >
            {children}
        </motion.div>
    );
}

/**
 * CardGrid - Animated grid container for cards with staggered children
 */
export function CardGrid({
    children,
    className = '',
    columns = 3
}: {
    children: ReactNode;
    className?: string;
    columns?: number;
}) {
    return (
        <motion.div
            className={`grid gap-6 ${columns === 2 ? 'md:grid-cols-2' :
                    columns === 3 ? 'md:grid-cols-2 lg:grid-cols-3' :
                        columns === 4 ? 'md:grid-cols-2 lg:grid-cols-4' :
                            'md:grid-cols-2 lg:grid-cols-3'
                } ${className}`}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: '-100px' }}
            variants={{
                hidden: { opacity: 0 },
                visible: {
                    opacity: 1,
                    transition: {
                        staggerChildren: 0.1,
                        delayChildren: 0.1,
                    },
                },
            }}
        >
            {children}
        </motion.div>
    );
}

/**
 * CardGridItem - Item for CardGrid with entrance animation
 */
export function CardGridItem({
    children,
    className = ''
}: {
    children: ReactNode;
    className?: string;
}) {
    return (
        <motion.div
            className={className}
            variants={{
                hidden: { opacity: 0, y: 30, scale: 0.95 },
                visible: {
                    opacity: 1,
                    y: 0,
                    scale: 1,
                    transition: {
                        duration: 0.5,
                        ease: [0.25, 0.46, 0.45, 0.94],
                    },
                },
            }}
            whileHover={{
                y: -5,
                transition: { duration: 0.2 }
            }}
        >
            {children}
        </motion.div>
    );
}

/**
 * GlassCard - Glassmorphism card with animations
 */
export function GlassCard({
    children,
    className = '',
    delay = 0
}: {
    children: ReactNode;
    className?: string;
    delay?: number;
}) {
    return (
        <motion.div
            className={`
        bg-card-bg/70 backdrop-blur-xl 
        border border-border-color/50 
        rounded-2xl shadow-premium
        ${className}
      `}
            initial={{ opacity: 0, y: 20, scale: 0.98 }}
            whileInView={{ opacity: 1, y: 0, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay, ease: [0.25, 0.46, 0.45, 0.94] }}
            whileHover={{
                boxShadow: '0 20px 50px rgba(0, 0, 0, 0.1), 0 10px 25px rgba(91, 76, 217, 0.08)',
                borderColor: 'rgba(91, 76, 217, 0.2)',
                transition: { duration: 0.3 }
            }}
        >
            {children}
        </motion.div>
    );
}

/**
 * PremiumCard - Ultra-premium card with gradient border and animations
 */
export function PremiumCard({
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
    return (
        <motion.div
            className="relative group"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay, ease: [0.25, 0.46, 0.45, 0.94] }}
        >
            {/* Gradient border glow */}
            {gradient && (
                <div className="absolute -inset-[1px] bg-gradient-to-r from-primary via-accent-purple to-primary rounded-2xl opacity-0 group-hover:opacity-100 blur-sm transition-opacity duration-500" />
            )}

            <motion.div
                className={`
          relative bg-card-bg 
          border border-border-color 
          rounded-2xl shadow-lg
          ${className}
        `}
                whileHover={{
                    y: -5,
                    boxShadow: '0 25px 50px rgba(0, 0, 0, 0.12)',
                }}
                transition={{ duration: 0.3 }}
            >
                {/* Shine effect on hover */}
                <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-white/0 via-white/5 to-white/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000 pointer-events-none" />

                {children}
            </motion.div>
        </motion.div>
    );
}

/**
 * FeatureCard - Card optimized for feature showcases
 */
export function FeatureCard({
    icon,
    title,
    description,
    delay = 0
}: {
    icon: ReactNode;
    title: string;
    description: string;
    delay?: number;
}) {
    return (
        <motion.div
            className="group relative bg-card-bg border border-border-color rounded-2xl p-6 shadow-lg overflow-hidden"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay, ease: [0.25, 0.46, 0.45, 0.94] }}
            whileHover={{ y: -5 }}
        >
            {/* Background gradient on hover */}
            <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-accent-purple/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

            <motion.div
                className="relative z-10"
                whileHover={{ scale: 1.02 }}
                transition={{ duration: 0.2 }}
            >
                {/* Icon container */}
                <motion.div
                    className="w-14 h-14 rounded-xl bg-gradient-to-br from-primary to-accent-purple flex items-center justify-center mb-4 shadow-lg shadow-primary/25"
                    whileHover={{ rotate: 5, scale: 1.05 }}
                    transition={{ type: 'spring', stiffness: 300, damping: 20 }}
                >
                    {icon}
                </motion.div>

                <h3 className="font-heading text-xl font-bold text-foreground mb-2">
                    {title}
                </h3>
                <p className="font-paragraph text-foreground-muted leading-relaxed">
                    {description}
                </p>
            </motion.div>
        </motion.div>
    );
}
