/**
 * TrustedCompanies Component
 * 
 * An infinite-scroll horizontal marquee showcasing trusted company logos.
 * Ultra-premium industrial design with smooth CSS animation.
 */
import React from 'react';
import { motion } from 'framer-motion';

// Company logos as SVG components for crisp rendering
const companyLogos = [
    { name: 'Google', color: '#4285F4' },
    { name: 'Microsoft', color: '#00A4EF' },
    { name: 'Amazon', color: '#FF9900' },
    { name: 'Meta', color: '#0081FB' },
    { name: 'Apple', color: '#A2AAAD' },
    { name: 'Netflix', color: '#E50914' },
    { name: 'Spotify', color: '#1DB954' },
    { name: 'Adobe', color: '#FF0000' },
    { name: 'Salesforce', color: '#00A1E0' },
    { name: 'IBM', color: '#0F62FE' },
    { name: 'Oracle', color: '#C74634' },
    { name: 'SAP', color: '#0FAAFF' },
];

// Simple text-based logo component (clean, industrial look)
const CompanyLogo = ({ name, color }: { name: string; color: string }) => (
    <div className="flex items-center gap-2 px-6 py-3">
        <div
            className="w-3 h-3 rounded-sm"
            style={{ backgroundColor: color }}
        />
        <span
            className="font-heading text-lg font-bold tracking-tight text-foreground-muted dark:text-foreground/70 whitespace-nowrap"
            style={{ fontWeight: 700 }}
        >
            {name}
        </span>
    </div>
);

const TrustedCompanies = () => {
    // Duplicate logos for seamless infinite loop
    const duplicatedLogos = [...companyLogos, ...companyLogos, ...companyLogos];

    return (
        <section className="relative w-full py-12 bg-background-light dark:bg-background overflow-hidden border-t border-b border-border-color">
            {/* Section header */}
            <motion.div
                className="text-center mb-8 px-6"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6 }}
            >
                <p className="font-paragraph text-sm text-foreground-muted dark:text-foreground/60 uppercase tracking-widest mb-2">
                    Trusted By Industry Leaders
                </p>
                <h3 className="font-heading text-xl font-bold text-foreground dark:text-white">
                    Our Users Have Landed Jobs At
                </h3>
            </motion.div>

            {/* Infinite scroll container */}
            <div className="relative">
                {/* Gradient fade edges for premium look */}
                <div className="absolute left-0 top-0 bottom-0 w-24 bg-gradient-to-r from-background-light dark:from-background to-transparent z-10 pointer-events-none" />
                <div className="absolute right-0 top-0 bottom-0 w-24 bg-gradient-to-l from-background-light dark:from-background to-transparent z-10 pointer-events-none" />

                {/* Scrolling track */}
                <div className="flex animate-marquee">
                    {duplicatedLogos.map((company, index) => (
                        <CompanyLogo key={`${company.name}-${index}`} name={company.name} color={company.color} />
                    ))}
                </div>
            </div>

            {/* Decorative line elements for industrial look */}
            <div className="absolute top-0 left-1/4 w-px h-full bg-gradient-to-b from-transparent via-border-color to-transparent opacity-30" />
            <div className="absolute top-0 left-1/2 w-px h-full bg-gradient-to-b from-transparent via-border-color to-transparent opacity-30" />
            <div className="absolute top-0 left-3/4 w-px h-full bg-gradient-to-b from-transparent via-border-color to-transparent opacity-30" />
        </section>
    );
};

export default TrustedCompanies;
