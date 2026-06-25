import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Loader2, CheckCircle, XCircle } from 'lucide-react';
import Header from '@/components/Header';
import Footer from '@/components/Footer';

export default function OAuthCallbackPage() {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();

    const accessToken = searchParams.get('access_token');
    const refreshToken = searchParams.get('refresh_token');
    const error = searchParams.get('error');
    const provider = searchParams.get('provider');

    useEffect(() => {
        if (error) {
            // OAuth error, redirect to login with error
            setTimeout(() => {
                navigate(`/login?error=${error}`);
            }, 2000);
            return;
        }

        if (accessToken && refreshToken) {
            // Tokens are already saved by AuthProvider via URL params detection
            // Just redirect to dashboard
            setTimeout(() => {
                navigate('/dashboard');
            }, 1500);
        } else {
            // No tokens, redirect to login
            setTimeout(() => {
                navigate('/login');
            }, 2000);
        }
    }, [accessToken, refreshToken, error, navigate]);

    if (error) {
        return (
            <div className="min-h-screen bg-background text-foreground">
                <Header />
                <div className="w-full py-16 px-8 lg:px-16">
                    <div className="max-w-md mx-auto text-center">
                        <motion.div
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            transition={{ type: "spring", duration: 0.5 }}
                            className="w-24 h-24 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-6"
                        >
                            <XCircle className="w-12 h-12 text-red-500" />
                        </motion.div>
                        <h1 className="font-heading text-3xl font-bold text-foreground mb-4">
                            Authentication Failed
                        </h1>
                        <p className="text-foreground/70 mb-4">
                            We couldn't complete the authentication with {provider || 'the provider'}.
                        </p>
                        <p className="text-foreground/50 text-sm">
                            Redirecting to login...
                        </p>
                    </div>
                </div>
                <Footer />
            </div>
        );
    }

    if (accessToken && refreshToken) {
        return (
            <div className="min-h-screen bg-background text-foreground">
                <Header />
                <div className="w-full py-16 px-8 lg:px-16">
                    <div className="max-w-md mx-auto text-center">
                        <motion.div
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            transition={{ type: "spring", duration: 0.5 }}
                            className="w-24 h-24 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-6"
                        >
                            <CheckCircle className="w-12 h-12 text-green-500" />
                        </motion.div>
                        <h1 className="font-heading text-3xl font-bold text-foreground mb-4">
                            Welcome!
                        </h1>
                        <p className="text-foreground/70 mb-4">
                            Successfully signed in with {provider === 'google' ? 'Google' : 'GitHub'}.
                        </p>
                        <p className="text-foreground/50 text-sm">
                            Redirecting to dashboard...
                        </p>
                    </div>
                </div>
                <Footer />
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-background text-foreground">
            <Header />
            <div className="w-full py-16 px-8 lg:px-16">
                <div className="max-w-md mx-auto text-center">
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="w-24 h-24 bg-primary/20 rounded-full flex items-center justify-center mx-auto mb-6"
                    >
                        <Loader2 className="w-12 h-12 text-primary animate-spin" />
                    </motion.div>
                    <h1 className="font-heading text-3xl font-bold text-foreground mb-4">
                        Processing...
                    </h1>
                    <p className="text-foreground/70">
                        Completing authentication...
                    </p>
                </div>
            </div>
            <Footer />
        </div>
    );
}
