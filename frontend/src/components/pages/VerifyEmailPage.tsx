import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { Mail, ArrowRight, RefreshCw, CheckCircle, AlertCircle } from 'lucide-react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { useMember } from '@/integrations';
import Header from '@/components/Header';
import Footer from '@/components/Footer';

export default function VerifyEmailPage() {
    const { actions, error, isLoading, pendingEmail, isAuthenticated } = useMember();
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const [otp, setOtp] = useState(['', '', '', '', '', '']);
    const [resendCooldown, setResendCooldown] = useState(0);
    const [verificationSuccess, setVerificationSuccess] = useState(false);
    const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

    const email = pendingEmail || searchParams.get('email') || '';

    // Redirect if already authenticated
    useEffect(() => {
        if (isAuthenticated) {
            navigate('/dashboard');
        }
    }, [isAuthenticated, navigate]);

    // Redirect if no email
    useEffect(() => {
        if (!email) {
            navigate('/register');
        }
    }, [email, navigate]);

    // Resend cooldown timer
    useEffect(() => {
        if (resendCooldown > 0) {
            const timer = setTimeout(() => setResendCooldown(resendCooldown - 1), 1000);
            return () => clearTimeout(timer);
        }
    }, [resendCooldown]);

    const handleChange = (index: number, value: string) => {
        // Only allow numbers
        if (value && !/^\d$/.test(value)) return;

        const newOtp = [...otp];
        newOtp[index] = value;
        setOtp(newOtp);

        // Auto-focus next input
        if (value && index < 5) {
            inputRefs.current[index + 1]?.focus();
        }
    };

    const handleKeyDown = (index: number, e: React.KeyboardEvent) => {
        // Handle backspace
        if (e.key === 'Backspace' && !otp[index] && index > 0) {
            inputRefs.current[index - 1]?.focus();
        }
    };

    const handlePaste = (e: React.ClipboardEvent) => {
        e.preventDefault();
        const pastedData = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6);
        const newOtp = [...otp];
        for (let i = 0; i < pastedData.length; i++) {
            newOtp[i] = pastedData[i];
        }
        setOtp(newOtp);

        // Focus on the next empty input or the last one
        const nextEmpty = newOtp.findIndex(v => !v);
        inputRefs.current[nextEmpty === -1 ? 5 : nextEmpty]?.focus();
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        const code = otp.join('');

        if (code.length !== 6) {
            return;
        }

        const success = await actions.verifyOTP({ email, code });

        if (success) {
            setVerificationSuccess(true);
            setTimeout(() => {
                navigate('/dashboard');
            }, 1500);
        }
    };

    const handleResend = async () => {
        if (resendCooldown > 0) return;

        const success = await actions.resendOTP(email);
        if (success) {
            setResendCooldown(60);
            setOtp(['', '', '', '', '', '']);
            inputRefs.current[0]?.focus();
        }
    };

    // Auto-submit when all digits are entered
    useEffect(() => {
        if (otp.every(digit => digit !== '') && !isLoading) {
            handleSubmit({ preventDefault: () => { } } as React.FormEvent);
        }
    }, [otp]);

    if (verificationSuccess) {
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
                            Email Verified!
                        </h1>
                        <p className="text-foreground/70">
                            Redirecting to your dashboard...
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
                <div className="max-w-[100rem] mx-auto">
                    <div className="max-w-md mx-auto">
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.6 }}
                            className="text-center mb-12"
                        >
                            <div className="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-6">
                                <Mail className="w-10 h-10 text-primary" />
                            </div>
                            <h1 className="font-heading text-4xl lg:text-5xl font-black text-foreground mb-4">
                                Verify Your <span className="text-primary">Email</span>
                            </h1>
                            <p className="font-paragraph text-lg text-foreground/70">
                                We've sent a 6-digit code to
                            </p>
                            <p className="font-paragraph text-lg text-primary font-semibold">
                                {email}
                            </p>
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, y: 30 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.6, delay: 0.2 }}
                            className="bg-gradient-to-br from-background to-gradient-start/10 border border-primary/30 rounded-lg p-8"
                        >
                            {error && (
                                <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-lg flex items-center gap-3">
                                    <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
                                    <p className="text-sm text-red-500">{error}</p>
                                </div>
                            )}

                            <form onSubmit={handleSubmit} className="space-y-6">
                                <div>
                                    <label className="block text-sm font-medium text-foreground/70 mb-4 text-center">
                                        Enter verification code
                                    </label>
                                    <div className="flex justify-center gap-3">
                                        {otp.map((digit, index) => (
                                            <input
                                                key={index}
                                                ref={el => inputRefs.current[index] = el}
                                                type="text"
                                                inputMode="numeric"
                                                maxLength={1}
                                                value={digit}
                                                onChange={e => handleChange(index, e.target.value)}
                                                onKeyDown={e => handleKeyDown(index, e)}
                                                onPaste={index === 0 ? handlePaste : undefined}
                                                className="w-12 h-14 text-center text-2xl font-bold bg-background border border-primary/30 rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all"
                                                autoFocus={index === 0}
                                            />
                                        ))}
                                    </div>
                                </div>

                                <Button
                                    type="submit"
                                    disabled={isLoading || otp.some(d => !d)}
                                    className="w-full bg-primary text-primary-foreground hover:bg-primary/90 rounded py-6 text-lg font-semibold"
                                >
                                    {isLoading ? 'Verifying...' : 'Verify Email'}
                                    <ArrowRight className="w-5 h-5 ml-2" />
                                </Button>
                            </form>

                            <div className="text-center mt-6">
                                <p className="font-paragraph text-sm text-foreground/70 mb-2">
                                    Didn't receive the code?
                                </p>
                                <button
                                    onClick={handleResend}
                                    disabled={resendCooldown > 0 || isLoading}
                                    className="text-primary hover:text-primary/80 transition-colors font-semibold inline-flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                                    {resendCooldown > 0 ? `Resend in ${resendCooldown}s` : 'Resend Code'}
                                </button>
                            </div>
                        </motion.div>

                        <p className="font-paragraph text-xs text-foreground/50 mt-4 text-center">
                            Check your spam folder if you don't see the email in your inbox
                        </p>
                    </div>
                </div>
            </div>

            <Footer />
        </div>
    );
}
