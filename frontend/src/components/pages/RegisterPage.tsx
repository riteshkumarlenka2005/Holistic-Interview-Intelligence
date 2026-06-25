import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { UserPlus, ArrowRight, CheckCircle, Mail, Lock, User, AlertCircle } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useMember } from '@/integrations';
import Header from '@/components/Header';
import Footer from '@/components/Footer';

// OAuth Icons as SVG components
const GoogleIcon = () => (
  <svg className="w-5 h-5" viewBox="0 0 24 24">
    <path
      fill="currentColor"
      d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
    />
    <path
      fill="currentColor"
      d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
    />
    <path
      fill="currentColor"
      d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
    />
    <path
      fill="currentColor"
      d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
    />
  </svg>
);

const GitHubIcon = () => (
  <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
    <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
  </svg>
);

export default function RegisterPage() {
  const { actions, error, isLoading, isAuthenticated, pendingVerification, pendingEmail } = useMember();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [formError, setFormError] = useState('');

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  // Redirect to verification if pending
  useEffect(() => {
    if (pendingVerification && pendingEmail) {
      navigate(`/verify-email?email=${encodeURIComponent(pendingEmail)}`);
    }
  }, [pendingVerification, pendingEmail, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError('');

    if (!formData.email || !formData.password) {
      setFormError('Please fill in all required fields');
      return;
    }

    if (formData.password.length < 8) {
      setFormError('Password must be at least 8 characters');
      return;
    }

    if (!/[A-Z]/.test(formData.password)) {
      setFormError('Password must contain at least one uppercase letter');
      return;
    }

    if (!/[a-z]/.test(formData.password)) {
      setFormError('Password must contain at least one lowercase letter');
      return;
    }

    if (!/\d/.test(formData.password)) {
      setFormError('Password must contain at least one number');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setFormError('Passwords do not match');
      return;
    }

    const success = await actions.register({
      email: formData.email,
      password: formData.password,
      firstName: formData.firstName,
      lastName: formData.lastName,
    });

    if (success) {
      // Will be redirected by the useEffect above when pendingVerification becomes true
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  const handleGoogleLogin = () => {
    actions.loginWithGoogle();
  };

  const handleGitHubLogin = () => {
    actions.loginWithGitHub();
  };

  const benefits = [
    'Unlimited practice sessions',
    'AI-powered feedback on verbal and non-verbal communication',
    'Progress tracking and analytics',
    'Access to learning resources and guides',
    'Personalized improvement recommendations',
    'Free forever for students'
  ];

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Header />

      <div className="w-full py-16 px-8 lg:px-16">
        <div className="max-w-[100rem] mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 max-w-5xl mx-auto">
            {/* Form Section */}
            <motion.div
              initial={{ opacity: 0, x: -30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6 }}
            >
              <div className="text-center lg:text-left mb-8">
                <h1
                  className="font-heading text-4xl lg:text-5xl font-black text-foreground mb-4"
                >
                  Start Your <span className="text-primary">Journey</span>
                </h1>
                <p className="font-paragraph text-lg text-foreground font-semibold">
                  Create your free account today
                </p>
              </div>

              <div className="bg-gradient-to-br from-background to-gradient-start/10 border border-primary/30 rounded-lg p-8">
                <div className="flex items-center justify-center mb-6">
                  <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
                    <UserPlus className="w-6 h-6 text-primary" />
                  </div>
                </div>

                {/* OAuth Buttons */}
                <div className="space-y-3 mb-6">
                  <Button
                    type="button"
                    onClick={handleGoogleLogin}
                    disabled={isLoading}
                    variant="outline"
                    className="w-full py-5 text-base font-medium border-primary/30 hover:bg-primary/5 hover:border-primary/50 transition-all"
                  >
                    <GoogleIcon />
                    <span className="ml-3">Continue with Google</span>
                  </Button>

                  <Button
                    type="button"
                    onClick={handleGitHubLogin}
                    disabled={isLoading}
                    variant="outline"
                    className="w-full py-5 text-base font-medium border-primary/30 hover:bg-primary/5 hover:border-primary/50 transition-all"
                  >
                    <GitHubIcon />
                    <span className="ml-3">Continue with GitHub</span>
                  </Button>
                </div>

                {/* Divider */}
                <div className="relative my-6">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-primary/20"></div>
                  </div>
                  <div className="relative flex justify-center text-sm">
                    <span className="px-4 bg-background text-foreground/50">or register with email</span>
                  </div>
                </div>

                {(error || formError) && (
                  <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-lg flex items-center gap-3">
                    <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
                    <p className="text-sm text-red-500">{error || formError}</p>
                  </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-foreground/70 mb-2">
                        First Name
                      </label>
                      <div className="relative">
                        <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-foreground/40" />
                        <Input
                          type="text"
                          name="firstName"
                          value={formData.firstName}
                          onChange={handleChange}
                          placeholder="John"
                          className="pl-10 py-5"
                        />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-foreground/70 mb-2">
                        Last Name
                      </label>
                      <div className="relative">
                        <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-foreground/40" />
                        <Input
                          type="text"
                          name="lastName"
                          value={formData.lastName}
                          onChange={handleChange}
                          placeholder="Doe"
                          className="pl-10 py-5"
                        />
                      </div>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-foreground/70 mb-2">
                      Email Address *
                    </label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-foreground/40" />
                      <Input
                        type="email"
                        name="email"
                        value={formData.email}
                        onChange={handleChange}
                        placeholder="john@example.com"
                        className="pl-10 py-5"
                        required
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-foreground/70 mb-2">
                      Password *
                    </label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-foreground/40" />
                      <Input
                        type="password"
                        name="password"
                        value={formData.password}
                        onChange={handleChange}
                        placeholder="Min 8 chars, 1 upper, 1 lower, 1 number"
                        className="pl-10 py-5"
                        required
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-foreground/70 mb-2">
                      Confirm Password *
                    </label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-foreground/40" />
                      <Input
                        type="password"
                        name="confirmPassword"
                        value={formData.confirmPassword}
                        onChange={handleChange}
                        placeholder="Confirm your password"
                        className="pl-10 py-5"
                        required
                      />
                    </div>
                  </div>

                  <Button
                    type="submit"
                    disabled={isLoading}
                    className="w-full bg-primary text-primary-foreground hover:bg-primary/90 rounded py-6 text-lg font-semibold"
                  >
                    {isLoading ? 'Creating account...' : 'Create Account'}
                    <ArrowRight className="w-5 h-5 ml-2" />
                  </Button>
                </form>

                <div className="text-center mt-6">
                  <p className="font-paragraph text-sm text-foreground/70">
                    Already have an account?{' '}
                    <Link to="/login" className="text-primary hover:text-primary/80 transition-colors font-semibold">
                      Sign in
                    </Link>
                  </p>
                </div>
              </div>

              <p className="font-paragraph text-xs text-foreground/50 mt-4 text-center lg:text-left">
                By signing up, you agree to our{' '}
                <Link to="/terms" className="text-primary hover:text-primary/80">Terms</Link>
                {' '}and{' '}
                <Link to="/privacy" className="text-primary hover:text-primary/80">Privacy Policy</Link>
              </p>
            </motion.div>

            {/* Benefits Section */}
            <motion.div
              initial={{ opacity: 0, x: 30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="hidden lg:block"
            >
              <div className="bg-gradient-to-br from-primary/5 to-secondary/5 border border-primary/30 rounded-lg p-8 h-full">
                <h3 className="font-heading text-2xl font-bold text-foreground mb-8">
                  What You'll Get
                </h3>

                <div className="space-y-5">
                  {benefits.map((benefit, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.5, delay: 0.4 + index * 0.1 }}
                      className="flex items-start gap-4"
                    >
                      <div className="w-8 h-8 bg-primary/20 rounded-full flex items-center justify-center flex-shrink-0">
                        <CheckCircle className="w-5 h-5 text-primary" />
                      </div>
                      <span className="font-paragraph text-foreground/80 text-lg">{benefit}</span>
                    </motion.div>
                  ))}
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
}
