import { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Menu, X, Brain, User, Sun, Moon, Sparkles, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useMember } from '@/integrations';
import { useThemeStore } from '@/hooks/useThemeStore';

export default function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const location = useLocation();
  const { member, isAuthenticated, actions } = useMember();
  const { theme, toggleTheme } = useThemeStore();

  // Handle scroll effect for navbar
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navLinks = [
    { href: '/', label: 'Home' },
    { href: '/features', label: 'Features' },
    { href: '/practice', label: 'Practice' },
    { href: '/dashboard', label: 'Dashboard' },
    { href: '/progress', label: 'Progress' },
    { href: '/resources', label: 'Resources' },
    { href: '/about', label: 'About' },
  ];

  const isActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${isScrolled
          ? 'bg-card-bg/95 backdrop-blur-xl border-b border-border-color shadow-lg shadow-black/5'
          : 'bg-card-bg/80 backdrop-blur-md'
        }`}
    >
      {/* Top accent line */}
      <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-primary to-transparent opacity-80" />

      <nav className="max-w-[100rem] mx-auto px-6 lg:px-12">
        <div className="flex items-center justify-between h-20">

          {/* Logo - Premium Design */}
          <Link to="/" className="flex items-center gap-3 group relative">
            {/* Logo glow effect */}
            <div className="absolute -inset-3 bg-primary/20 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

            <motion.div
              className="relative w-11 h-11 bg-gradient-to-br from-primary via-accent-purple to-primary rounded-xl flex items-center justify-center shadow-lg shadow-primary/30 overflow-hidden"
              whileHover={{ scale: 1.05, rotate: 5 }}
              whileTap={{ scale: 0.95 }}
              transition={{ type: "spring", stiffness: 400, damping: 17 }}
            >
              {/* Animated gradient background */}
              <div className="absolute inset-0 bg-gradient-to-br from-primary via-accent-purple to-primary bg-[length:200%_200%] animate-gradient" />
              <Brain className="w-6 h-6 text-white relative z-10" />

              {/* Shine effect */}
              <div className="absolute inset-0 bg-gradient-to-tr from-white/0 via-white/30 to-white/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700" />
            </motion.div>

            <div className="relative hidden sm:block">
              <span className="font-heading text-xl font-black text-foreground tracking-tight">
                Interview<span className="bg-gradient-to-r from-primary to-accent-purple bg-clip-text text-transparent">Pro</span>
              </span>
              <span className="absolute -bottom-1 left-0 text-[10px] font-paragraph text-primary uppercase tracking-[0.2em] font-semibold">AI Platform</span>
            </div>
          </Link>

          {/* Desktop Navigation - Premium Pills */}
          <div className="hidden lg:flex items-center">
            <div className="flex items-center gap-1 bg-secondary/80 backdrop-blur-sm rounded-full p-1.5 border border-border-color">
              {navLinks.map((link) => (
                <Link
                  key={link.href}
                  to={link.href}
                  className="relative"
                >
                  <motion.div
                    className={`px-4 py-2 rounded-full text-sm font-paragraph font-semibold transition-all duration-300 ${isActive(link.href)
                        ? 'text-white'
                        : 'text-foreground hover:text-primary'
                      }`}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    {/* Active pill background */}
                    {isActive(link.href) && (
                      <motion.div
                        className="absolute inset-0 bg-gradient-to-r from-primary to-accent-purple rounded-full shadow-md shadow-primary/40"
                        layoutId="activeNavPill"
                        transition={{ type: "spring", stiffness: 400, damping: 30 }}
                      />
                    )}
                    <span className="relative z-10">{link.label}</span>
                  </motion.div>
                </Link>
              ))}
            </div>
          </div>

          {/* Right Side Actions - Premium Buttons */}
          <div className="hidden lg:flex items-center gap-3">

            {/* Theme Toggle - Premium Style */}
            <motion.button
              onClick={toggleTheme}
              className="relative w-11 h-11 rounded-xl border border-border-color bg-secondary/80 backdrop-blur-sm flex items-center justify-center overflow-hidden group"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} theme`}
            >
              {/* Hover glow */}
              <div className="absolute inset-0 bg-gradient-to-br from-amber-500/20 to-primary/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

              <Sun
                className={`w-5 h-5 absolute transition-all duration-500 ${theme === 'light'
                    ? 'opacity-100 rotate-0 scale-100 text-amber-500'
                    : 'opacity-0 rotate-180 scale-50 text-amber-500'
                  }`}
              />
              <Moon
                className={`w-5 h-5 absolute transition-all duration-500 ${theme === 'dark'
                    ? 'opacity-100 rotate-0 scale-100 text-primary-light'
                    : 'opacity-0 -rotate-180 scale-50 text-primary-light'
                  }`}
              />
            </motion.button>

            {isAuthenticated ? (
              <>
                <Link to="/profile">
                  <motion.div
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <Button
                      variant="outline"
                      className="h-11 px-5 border-border-color bg-secondary/80 backdrop-blur-sm text-foreground font-semibold hover:bg-secondary hover:border-primary/50 rounded-xl font-paragraph transition-all duration-300"
                    >
                      <div className="w-7 h-7 rounded-full bg-gradient-to-br from-primary to-accent-purple flex items-center justify-center mr-2">
                        <User className="w-4 h-4 text-white" />
                      </div>
                      {member?.profile?.nickname || 'Profile'}
                    </Button>
                  </motion.div>
                </Link>
                <motion.div
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <Button
                    onClick={actions.logout}
                    variant="outline"
                    className="h-11 px-5 border-border-color text-foreground font-semibold hover:bg-secondary hover:border-red-500/30 rounded-xl font-paragraph transition-all duration-300"
                  >
                    Sign Out
                  </Button>
                </motion.div>
              </>
            ) : (
              <>
                {/* Login Button - Clear and Visible */}
                <Link to="/login">
                  <motion.div
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <Button
                      variant="outline"
                      className="h-11 px-6 border-border-color bg-secondary/80 backdrop-blur-sm text-foreground font-bold hover:bg-secondary hover:border-primary/50 rounded-xl font-paragraph transition-all duration-300"
                    >
                      Login
                    </Button>
                  </motion.div>
                </Link>

                {/* Get Started Button - Premium CTA */}
                <Link to="/register">
                  <motion.div
                    className="relative group"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    {/* Glow effect */}
                    <div className="absolute -inset-1 bg-gradient-to-r from-primary to-accent-purple rounded-xl blur-lg opacity-60 group-hover:opacity-90 transition-opacity duration-300" />

                    <Button
                      className="relative h-11 px-6 bg-gradient-to-r from-primary to-accent-purple text-white rounded-xl font-heading font-bold shadow-lg shadow-primary/40 hover:shadow-xl hover:shadow-primary/50 transition-all duration-300 overflow-hidden"
                    >
                      {/* Animated shine */}
                      <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/25 to-white/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700" />

                      <span className="relative z-10 flex items-center gap-2">
                        <Sparkles className="w-4 h-4" />
                        Get Started
                        <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform duration-300" />
                      </span>
                    </Button>
                  </motion.div>
                </Link>
              </>
            )}
          </div>

          {/* Mobile Menu Button + Theme Toggle */}
          <div className="lg:hidden flex items-center gap-3">
            {/* Mobile Theme Toggle */}
            <motion.button
              onClick={toggleTheme}
              className="w-10 h-10 rounded-xl border border-border-color bg-secondary/80 backdrop-blur-sm flex items-center justify-center"
              whileTap={{ scale: 0.95 }}
              aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} theme`}
            >
              <Sun
                className={`w-5 h-5 absolute transition-all duration-500 ${theme === 'light'
                    ? 'opacity-100 rotate-0 scale-100 text-amber-500'
                    : 'opacity-0 rotate-180 scale-50'
                  }`}
              />
              <Moon
                className={`w-5 h-5 absolute transition-all duration-500 ${theme === 'dark'
                    ? 'opacity-100 rotate-0 scale-100 text-primary-light'
                    : 'opacity-0 -rotate-180 scale-50'
                  }`}
              />
            </motion.button>

            {/* Hamburger Menu Button */}
            <motion.button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="w-10 h-10 rounded-xl border border-border-color bg-secondary/80 backdrop-blur-sm flex items-center justify-center text-foreground"
              whileTap={{ scale: 0.95 }}
              aria-label="Toggle menu"
            >
              <AnimatePresence mode="wait">
                {isMenuOpen ? (
                  <motion.div
                    key="close"
                    initial={{ rotate: -90, opacity: 0 }}
                    animate={{ rotate: 0, opacity: 1 }}
                    exit={{ rotate: 90, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    <X className="w-5 h-5" />
                  </motion.div>
                ) : (
                  <motion.div
                    key="menu"
                    initial={{ rotate: 90, opacity: 0 }}
                    animate={{ rotate: 0, opacity: 1 }}
                    exit={{ rotate: -90, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    <Menu className="w-5 h-5" />
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.button>
          </div>
        </div>

        {/* Mobile Navigation - Premium Slide Down */}
        <AnimatePresence>
          {isMenuOpen && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.3, ease: [0.25, 0.46, 0.45, 0.94] }}
              className="lg:hidden overflow-hidden"
            >
              <div className="py-6 space-y-2 border-t border-border-color mt-4">
                {navLinks.map((link, index) => (
                  <motion.div
                    key={link.href}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                  >
                    <Link
                      to={link.href}
                      onClick={() => setIsMenuOpen(false)}
                      className={`flex items-center justify-between px-4 py-3 rounded-xl font-paragraph text-base font-semibold transition-all duration-300 ${isActive(link.href)
                          ? 'bg-gradient-to-r from-primary to-accent-purple text-white shadow-md shadow-primary/30'
                          : 'text-foreground hover:text-primary hover:bg-secondary/80'
                        }`}
                    >
                      {link.label}
                      {isActive(link.href) && <ArrowRight className="w-4 h-4" />}
                    </Link>
                  </motion.div>
                ))}

                <motion.div
                  className="pt-4 space-y-3 border-t border-border-color mt-4"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.3 }}
                >
                  {isAuthenticated ? (
                    <>
                      <Link to="/profile" onClick={() => setIsMenuOpen(false)}>
                        <Button variant="outline" className="w-full h-12 border-border-color text-foreground font-semibold hover:bg-secondary rounded-xl font-paragraph">
                          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-accent-purple flex items-center justify-center mr-3">
                            <User className="w-4 h-4 text-white" />
                          </div>
                          {member?.profile?.nickname || 'Profile'}
                        </Button>
                      </Link>
                      <Button
                        onClick={() => {
                          actions.logout();
                          setIsMenuOpen(false);
                        }}
                        variant="outline"
                        className="w-full h-12 border-border-color text-foreground font-semibold hover:bg-secondary rounded-xl font-paragraph"
                      >
                        Sign Out
                      </Button>
                    </>
                  ) : (
                    <>
                      <Link to="/login" onClick={() => setIsMenuOpen(false)}>
                        <Button variant="outline" className="w-full h-12 border-border-color text-foreground font-bold hover:bg-secondary rounded-xl font-paragraph">
                          Login
                        </Button>
                      </Link>
                      <Link to="/register" onClick={() => setIsMenuOpen(false)}>
                        <Button className="w-full h-12 bg-gradient-to-r from-primary to-accent-purple text-white rounded-xl font-heading font-bold shadow-lg shadow-primary/30">
                          <Sparkles className="w-4 h-4 mr-2" />
                          Get Started
                        </Button>
                      </Link>
                    </>
                  )}
                </motion.div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </nav>
    </header>
  );
}
