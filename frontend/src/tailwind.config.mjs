/** @type {import('tailwindcss').Config} */
export default {
    darkMode: 'class',
    content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}', './public/**/*.html'],
    theme: {
        extend: {
            fontSize: {
                xs: ["0.75rem", { lineHeight: "1.25", letterSpacing: "0.02em", fontWeight: "500" }],
                sm: ["0.875rem", { lineHeight: "1.35", letterSpacing: "0.015em", fontWeight: "500" }],
                base: ["1rem", { lineHeight: "1.5", letterSpacing: "0.01em", fontWeight: "500" }],
                lg: ["1.125rem", { lineHeight: "1.5", letterSpacing: "0.005em", fontWeight: "600" }],
                xl: ["1.25rem", { lineHeight: "1.5", letterSpacing: "0em", fontWeight: "600" }],
                "2xl": ["1.5rem", { lineHeight: "1.4", letterSpacing: "-0.005em", fontWeight: "700" }],
                "3xl": ["1.875rem", { lineHeight: "1.3", letterSpacing: "-0.01em", fontWeight: "800" }],
                "4xl": ["2.25rem", { lineHeight: "1.2", letterSpacing: "-0.015em", fontWeight: "800" }],
                "5xl": ["3rem", { lineHeight: "1.1", letterSpacing: "-0.02em", fontWeight: "900" }],
                "6xl": ["3.75rem", { lineHeight: "1.1", letterSpacing: "-0.025em", fontWeight: "900" }],
                "7xl": ["4.5rem", { lineHeight: "1", letterSpacing: "-0.03em", fontWeight: "900" }],
                "8xl": ["6rem", { lineHeight: "1", letterSpacing: "-0.035em", fontWeight: "900" }],
                "9xl": ["8rem", { lineHeight: "1", letterSpacing: "-0.04em", fontWeight: "900" }],
            },
            fontFamily: {
                // Premium font stack with Outfit for headings, Inter for body
                heading: ["Outfit", "helvetica-w01-bold", "system-ui", "sans-serif"],
                paragraph: ["Inter", "helvetica-w01-roman", "system-ui", "sans-serif"],
                // Add display variant for extra emphasis
                display: ["Outfit", "system-ui", "sans-serif"],
            },
            colors: {
                destructive: "#E74C3C",
                "destructive-foreground": "#FFFFFF",
                // Slightly deeper background for better contrast
                background: "#F5F4FA",
                "background-light": "#FAFBFF",
                secondary: "#E8E5F5",
                // DEEPER foreground colors for better visibility
                foreground: "#0F0F1A",
                "foreground-muted": "#3A3A52",
                "primary-foreground": "#0F0F1A",
                // Slightly more saturated primary for punch
                primary: "#5B4CD9",
                "primary-light": "#7B6CE8",
                "primary-lighter": "#A8A0F0",
                "secondary-foreground": "#1D1D2A",
                "accent-purple": "#6B5DD8",
                "accent-light": "#D4CCFF",
                "border-color": "#E0DCF0",
                "card-bg": "#FFFFFF",
                "shadow-soft": "rgba(91, 76, 217, 0.1)",
            },
            // Animation extensions for Framer Motion compatibility
            animation: {
                'gradient': 'gradient 4s ease infinite',
                'float': 'float 6s ease-in-out infinite',
                'glow': 'glow 2s ease-in-out infinite alternate',
                'slide-up': 'slideUp 0.5s ease-out',
                'slide-down': 'slideDown 0.5s ease-out',
                'fade-in': 'fadeIn 0.5s ease-out',
                'scale-in': 'scaleIn 0.3s ease-out',
                'bounce-subtle': 'bounceSubtle 2s ease-in-out infinite',
            },
            keyframes: {
                gradient: {
                    '0%, 100%': { backgroundPosition: '0% 50%' },
                    '50%': { backgroundPosition: '100% 50%' },
                },
                float: {
                    '0%, 100%': { transform: 'translateY(0)' },
                    '50%': { transform: 'translateY(-10px)' },
                },
                glow: {
                    '0%': { boxShadow: '0 0 20px rgba(91, 76, 217, 0.3)' },
                    '100%': { boxShadow: '0 0 40px rgba(91, 76, 217, 0.6)' },
                },
                slideUp: {
                    '0%': { opacity: '0', transform: 'translateY(20px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' },
                },
                slideDown: {
                    '0%': { opacity: '0', transform: 'translateY(-20px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' },
                },
                fadeIn: {
                    '0%': { opacity: '0' },
                    '100%': { opacity: '1' },
                },
                scaleIn: {
                    '0%': { opacity: '0', transform: 'scale(0.95)' },
                    '100%': { opacity: '1', transform: 'scale(1)' },
                },
                bounceSubtle: {
                    '0%, 100%': { transform: 'translateY(0)' },
                    '50%': { transform: 'translateY(-5px)' },
                },
            },
            // Transition durations
            transitionDuration: {
                '400': '400ms',
                '600': '600ms',
                '800': '800ms',
            },
            // Custom box shadows for premium feel
            boxShadow: {
                'glow-sm': '0 0 15px rgba(91, 76, 217, 0.2)',
                'glow-md': '0 0 30px rgba(91, 76, 217, 0.3)',
                'glow-lg': '0 0 50px rgba(91, 76, 217, 0.4)',
                'premium': '0 4px 20px rgba(0, 0, 0, 0.08), 0 2px 8px rgba(0, 0, 0, 0.04)',
            },
        },
    },
    future: {
        hoverOnlyWhenSupported: true,
    },
    plugins: [require('@tailwindcss/container-queries'), require('@tailwindcss/typography')],
}
