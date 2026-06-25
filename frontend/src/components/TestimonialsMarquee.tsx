/**
 * TestimonialsMarquee Component
 * 
 * Premium testimonials section with two rows of cards moving in opposite directions.
 * Infinite scroll animation with pause on hover.
 */
import React from 'react';
import { motion } from 'framer-motion';
import { Star } from 'lucide-react';

interface Testimonial {
    name: string;
    role: string;
    company: string;
    quote: string;
    avatar: string; // Initials for avatar
    rating: number;
}

const testimonialsRow1: Testimonial[] = [
    {
        name: "Adi G.",
        role: "Product Manager",
        company: "Capital One",
        quote: "InterviewPro played a crucial role in helping me land my current offer—I doubled my salary thanks to their excellent resources!",
        avatar: "AG",
        rating: 5
    },
    {
        name: "Devang S.",
        role: "Lead Software Engineer",
        company: "FAANG",
        quote: "This is an amazing platform that bridges the gap between technical excellence and leadership impact. The behavioral patterns and communication strategies helped me tremendously.",
        avatar: "DS",
        rating: 5
    },
    {
        name: "Eugene K.",
        role: "Senior Software Engineer",
        company: "Mid-Sized Tech Company",
        quote: "I really liked the course. It had lots of helpful examples and a clear structure. The tips on how to communicate better in interviews were very useful.",
        avatar: "EK",
        rating: 5
    },
    {
        name: "Priya M.",
        role: "Data Scientist",
        company: "Microsoft",
        quote: "The AI feedback on my non-verbal communication was eye-opening. I never realized how much my body language affected my interview performance.",
        avatar: "PM",
        rating: 5
    },
    {
        name: "James L.",
        role: "Backend Developer",
        company: "Stripe",
        quote: "After 3 weeks of practice with InterviewPro, I felt completely prepared for my system design interviews. Landed my dream job!",
        avatar: "JL",
        rating: 5
    }
];

const testimonialsRow2: Testimonial[] = [
    {
        name: "Nicole T.",
        role: "UX Designer",
        company: "Qualtrics",
        quote: "I'm so glad I came across InterviewPro – I appreciated the clean user experience & community. The step by step guides helped me feel less overwhelmed.",
        avatar: "NT",
        rating: 5
    },
    {
        name: "Amit R.",
        role: "PM, Technical",
        company: "Amazon",
        quote: "I have strongly recommended it to all my peers preparing for PM interviews. The structured approach to behavioral questions is excellent.",
        avatar: "AR",
        rating: 5
    },
    {
        name: "Daniel W.",
        role: "Product Manager",
        company: "Google",
        quote: "Three weeks of studying with InterviewPro helped me land a PM offer. The practice sessions with AI feedback were invaluable.",
        avatar: "DW",
        rating: 5
    },
    {
        name: "Sarah C.",
        role: "Engineering Manager",
        company: "Netflix",
        quote: "The leadership interview prep content is phenomenal. I was able to articulate my management philosophy much more clearly.",
        avatar: "SC",
        rating: 5
    },
    {
        name: "Michael B.",
        role: "Solutions Architect",
        company: "AWS",
        quote: "InterviewPro's focus on communication skills alongside technical knowledge is what sets it apart. Highly recommend to anyone serious about career growth.",
        avatar: "MB",
        rating: 5
    }
];

const TestimonialCard = ({ testimonial }: { testimonial: Testimonial }) => (
    <div className="flex-shrink-0 w-[380px] mx-3 p-6 bg-card-bg dark:bg-card-bg/80 rounded-2xl border border-border-color shadow-sm hover:shadow-md transition-shadow duration-300 group">
        {/* Header with avatar and info */}
        <div className="flex items-center gap-4 mb-4">
            {/* Avatar */}
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary to-accent-purple flex items-center justify-center text-white font-heading font-bold text-sm">
                {testimonial.avatar}
            </div>

            {/* Name and role */}
            <div className="flex-1">
                <h4 className="font-heading font-bold text-foreground dark:text-white group-hover:text-primary transition-colors duration-300">
                    {testimonial.name}
                </h4>
                <p className="font-paragraph text-sm text-foreground-muted dark:text-foreground/60">
                    {testimonial.role}, {testimonial.company}
                </p>
            </div>
        </div>

        {/* Rating */}
        <div className="flex gap-1 mb-3">
            {[...Array(testimonial.rating)].map((_, i) => (
                <Star key={i} className="w-4 h-4 fill-amber-400 text-amber-400" />
            ))}
        </div>

        {/* Quote */}
        <p className="font-paragraph text-foreground-muted dark:text-foreground/70 leading-relaxed text-sm">
            "{testimonial.quote}"
        </p>
    </div>
);

const TestimonialsMarquee = () => {
    // Duplicate for seamless loop
    const row1Duplicated = [...testimonialsRow1, ...testimonialsRow1, ...testimonialsRow1];
    const row2Duplicated = [...testimonialsRow2, ...testimonialsRow2, ...testimonialsRow2];

    return (
        <section className="relative py-24 bg-background-light dark:bg-background overflow-hidden">
            {/* Background decorations */}
            <div className="absolute inset-0 grid-pattern pointer-events-none opacity-50" />

            <div className="relative z-10">
                {/* Section Header */}
                <motion.div
                    className="text-center mb-16 px-6"
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6 }}
                >
                    <h2 className="font-heading text-4xl lg:text-5xl font-black text-foreground dark:text-white mb-4">
                        What People Are{' '}
                        <span className="text-primary">Saying</span>
                    </h2>

                    <div className="flex items-center justify-center gap-2 mb-4">
                        <div className="flex gap-1">
                            {[...Array(5)].map((_, i) => (
                                <Star key={i} className="w-5 h-5 fill-amber-400 text-amber-400" />
                            ))}
                        </div>
                        <span className="font-paragraph text-foreground-muted dark:text-foreground/70">
                            4.8 rating from over <strong className="text-foreground dark:text-white">2,400</strong> reviews
                        </span>
                    </div>
                </motion.div>

                {/* Row 1 - Moving Left */}
                <div className="relative mb-6">
                    {/* Gradient fade edges */}
                    <div className="absolute left-0 top-0 bottom-0 w-32 bg-gradient-to-r from-background-light dark:from-background to-transparent z-10 pointer-events-none" />
                    <div className="absolute right-0 top-0 bottom-0 w-32 bg-gradient-to-l from-background-light dark:from-background to-transparent z-10 pointer-events-none" />

                    <div className="flex animate-marquee-slow">
                        {row1Duplicated.map((testimonial, index) => (
                            <TestimonialCard key={`row1-${index}`} testimonial={testimonial} />
                        ))}
                    </div>
                </div>

                {/* Row 2 - Moving Right (opposite direction) */}
                <div className="relative">
                    {/* Gradient fade edges */}
                    <div className="absolute left-0 top-0 bottom-0 w-32 bg-gradient-to-r from-background-light dark:from-background to-transparent z-10 pointer-events-none" />
                    <div className="absolute right-0 top-0 bottom-0 w-32 bg-gradient-to-l from-background-light dark:from-background to-transparent z-10 pointer-events-none" />

                    <div className="flex animate-marquee-reverse">
                        {row2Duplicated.map((testimonial, index) => (
                            <TestimonialCard key={`row2-${index}`} testimonial={testimonial} />
                        ))}
                    </div>
                </div>
            </div>
        </section>
    );
};

export default TestimonialsMarquee;
