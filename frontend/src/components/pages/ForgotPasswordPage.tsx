import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { KeyRound, ArrowRight, Mail, Lock, RefreshCw, CheckCircle, AlertCircle, ArrowLeft } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useMember } from '@/integrations';
import Header from '@/components/Header';
import Footer from '@/components/Footer';

type Step = 'email' | 'otp' | 'newPassword' | 'success';

export default function ForgotPasswordPage() {
    const { actions, error, isLoading } = useMember();
    const navigate = useNavigate();
    const [step, setStep] = useState<Step>('email');
    const [email, setEmail] = useState('');
    const [otp, setOtp] = useState(['', '', '', '', '', '']);
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [formError, setFormError] = useState('');
    const [resendCooldown, setResendCooldown] = useState(0);
    const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

    // Resend cooldown timer
    useEffect(() => {
        if (resendCooldown > 0) {
            const timer = setTimeout(() => setResendCooldown(resendCooldown - 1), 1000);
            return () => clearTimeout(timer);
        }
    }, [resendCooldown]);

    const handleEmailSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setFormError('');

        if (!email) {
            setFormError('Please enter your email address');
            return;
        }

        const success = await actions.forgotPassword(email);
        if (success) {
            setStep('otp');
            setResendCooldown(60);
        }
    };

    const handleOtpChange = (index: number, value: string) => {
        if (value && !/^\d$/.test(value)) return;

        const newOtp = [...otp];
        newOtp[index] = value;
        setOtp(newOtp);

        if (value && index < 5) {
            inputRefs.current[index + 1]?.focus();
        }
    };

    const handleOtpKeyDown = (index: number, e: React.KeyboardEvent) => {
        if (e.key === 'Backspace' && !otp[index] && index > 0) {
            inputRefs.current[index - 1]?.focus();
        }
    };

    const handleOtpSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        const code = otp.join('');

        if (code.length !== 6) {
            setFormError('Please enter the complete 6-digit code');
            return;
        }

        setStep('newPassword');
    };

    const handlePasswordSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setFormError('');

        if (newPassword.length < 8) {
            setFormError('Password must be at least 8 characters');
            return;
        }

        if (newPassword !== confirmPassword) {
            setFormError('Passwords do not match');
            return;
        }

        const code = otp.join('');
        const success = await actions.resetPassword(email, code, newPassword);

        if (success) {
            setStep('success');
        }
    };

    const handleResend = async () => {
        if (resendCooldown > 0) return;

        const success = await actions.forgotPassword(email);
        if (success) {
            setResendCooldown(60);
            setOtp(['', '', '', '', '', '']);
            inputRefs.current[0]?.focus();
        }
    };

    if (step === 'success') {
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
                            Password Reset Successful!
                        </h1>
                        <p className="text-foreground/70 mb-8">
                            Your password has been updated. You can now log in with your new password.
                        </p>
                        <Button
                            onClick={() => navigate('/login')}
                            className="bg-primary text-primary-foreground hover:bg-primary/90 rounded py-6 px-8 text-lg font-semibold"
                        >
                            Go to Login
                            <ArrowRight className="w-5 h-5 ml-2" />
                        </Button>
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
                                <KeyRound className="w-10 h-10 text-primary" />
                            </div>
                            <h1 className="font-heading text-4xl lg:text-5xl font-black text-foreground mb-4">
                                Reset <span className="text-primary">Password</span>
                            </h1>
                            <p className="font-paragraph text-lg text-foreground/70">
                                {step === 'email' && "Enter your email to receive a reset code"}
                                {step === 'otp' && "Enter the code sent to your email"}
                                {step === 'newPassword' && "Create your new password"}
                            </p>
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, y: 30 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.6, delay: 0.2 }}
                            className="bg-gradient-to-br from-background to-gradient-start/10 border border-primary/30 rounded-lg p-8"
                        >
                            {(error || formError) && (
                                <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-lg flex items-center gap-3">
                                    <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
                                    <p className="text-sm text-red-500">{error || formError}</p>
                                </div>
                            )}

                            {/* Step 1: Email */}
                            {step === 'email' && (
                                <form onSubmit={handleEmailSubmit} className="space-y-4">
                                    <div>
                                        <label className="block text-sm font-medium text-foreground/70 mb-2">
                                            Email Address
                                        </label>
                                        <div className="relative">
                                            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-foreground/40" />
                                            <Input
                                                type="email"
                                                value={email}
                                                onChange={e => setEmail(e.target.value)}
                                                placeholder="Enter your email"
                                                className="pl-10 py-6"
                                            />
                                        </div>
                                    </div>

                                    <Button
                                        type="submit"
                                        disabled={isLoading}
                                        className="w-full bg-primary text-primary-foreground hover:bg-primary/90 rounded py-6 text-lg font-semibold"
                                    >
                                        {isLoading ? 'Sending...' : 'Send Reset Code'}
                                        <ArrowRight className="w-5 h-5 ml-2" />
                                    </Button>
                                </form>
                            )}

                            {/* Step 2: OTP */}
                            {step === 'otp' && (
                                <form onSubmit={handleOtpSubmit} className="space-y-6">
                                    <div>
                                        <label className="block text-sm font-medium text-foreground/70 mb-4 text-center">
                                            Enter reset code
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
                                                    onChange={e => handleOtpChange(index, e.target.value)}
                                                    onKeyDown={e => handleOtpKeyDown(index, e)}
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
                                        Verify Code
                                        <ArrowRight className="w-5 h-5 ml-2" />
                                    </Button>

                                    <div className="text-center">
                                        <button
                                            type="button"
                                            onClick={handleResend}
                                            disabled={resendCooldown > 0 || isLoading}
                                            className="text-primary hover:text-primary/80 transition-colors font-semibold inline-flex items-center gap-2 disabled:opacity-50"
                                        >
                                            <RefreshCw className="w-4 h-4" />
                                            {resendCooldown > 0 ? `Resend in ${resendCooldown}s` : 'Resend Code'}
                                        </button>
                                    </div>

                                    <button
                                        type="button"
                                        onClick={() => setStep('email')}
                                        className="w-full text-foreground/70 hover:text-foreground transition-colors text-sm flex items-center justify-center gap-2"
                                    >
                                        <ArrowLeft className="w-4 h-4" />
                                        Change email address
                                    </button>
                                </form>
                            )}

                            {/* Step 3: New Password */}
                            {step === 'newPassword' && (
                                <form onSubmit={handlePasswordSubmit} className="space-y-4">
                                    <div>
                                        <label className="block text-sm font-medium text-foreground/70 mb-2">
                                            New Password
                                        </label>
                                        <div className="relative">
                                            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-foreground/40" />
                                            <Input
                                                type="password"
                                                value={newPassword}
                                                onChange={e => setNewPassword(e.target.value)}
                                                placeholder="Min 8 characters"
                                                className="pl-10 py-6"
                                            />
                                        </div>
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-foreground/70 mb-2">
                                            Confirm Password
                                        </label>
                                        <div className="relative">
                                            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-foreground/40" />
                                            <Input
                                                type="password"
                                                value={confirmPassword}
                                                onChange={e => setConfirmPassword(e.target.value)}
                                                placeholder="Confirm your password"
                                                className="pl-10 py-6"
                                            />
                                        </div>
                                    </div>

                                    <Button
                                        type="submit"
                                        disabled={isLoading}
                                        className="w-full bg-primary text-primary-foreground hover:bg-primary/90 rounded py-6 text-lg font-semibold"
                                    >
                                        {isLoading ? 'Resetting...' : 'Reset Password'}
                                        <ArrowRight className="w-5 h-5 ml-2" />
                                    </Button>
                                </form>
                            )}

                            <div className="text-center mt-6">
                                <Link to="/login" className="text-primary hover:text-primary/80 transition-colors font-semibold text-sm">
                                    Back to Login
                                </Link>
                            </div>
                        </motion.div>
                    </div>
                </div>
            </div>

            <Footer />
        </div>
    );
}
