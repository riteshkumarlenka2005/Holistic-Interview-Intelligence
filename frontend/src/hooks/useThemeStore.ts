/**
 * Theme Store
 * 
 * Manages theme state with localStorage persistence.
 * Supports light and dark themes with system preference detection.
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

type Theme = 'light' | 'dark';

interface ThemeState {
    theme: Theme;
    setTheme: (theme: Theme) => void;
    toggleTheme: () => void;
}

// Apply theme to document
const applyTheme = (theme: Theme) => {
    const root = document.documentElement;
    if (theme === 'dark') {
        root.classList.add('dark');
    } else {
        root.classList.remove('dark');
    }
};

// Get initial theme based on system preference or stored value
const getInitialTheme = (): Theme => {
    if (typeof window === 'undefined') return 'light';

    // Check localStorage first
    const stored = localStorage.getItem('theme-storage');
    if (stored) {
        try {
            const parsed = JSON.parse(stored);
            if (parsed.state?.theme) {
                return parsed.state.theme;
            }
        } catch {
            // Ignore parse errors
        }
    }

    // Fall back to system preference
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
        return 'dark';
    }

    return 'light';
};

export const useThemeStore = create<ThemeState>()(
    persist(
        (set, get) => ({
            theme: getInitialTheme(),
            setTheme: (theme: Theme) => {
                applyTheme(theme);
                set({ theme });
            },
            toggleTheme: () => {
                const currentTheme = get().theme;
                const newTheme = currentTheme === 'light' ? 'dark' : 'light';
                applyTheme(newTheme);
                set({ theme: newTheme });
            },
        }),
        {
            name: 'theme-storage',
            onRehydrateStorage: () => (state) => {
                // Apply theme on rehydration
                if (state?.theme) {
                    applyTheme(state.theme);
                }
            },
        }
    )
);

// Initialize theme on module load
if (typeof window !== 'undefined') {
    const initialTheme = getInitialTheme();
    applyTheme(initialTheme);
}
