import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Mail, Lock, KeyRound, ArrowRight, ShieldCheck } from 'lucide-react';
import { apiService } from '../services/api';

export default function ForgotPassword() {
    const navigate = useNavigate();
    
    // Steps: 1 = Enter Email, 2 = Enter Token & New Password
    const [step, setStep] = useState<1 | 2>(1);
    
    // Form State
    const [email, setEmail] = useState('');
    const [token, setToken] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    
    // UI State
    const [error, setError] = useState('');
    const [successMsg, setSuccessMsg] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleRequestReset = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);
        try {
            const res = await apiService.requestPasswordReset({ email });
            // For Demo: Show the code returned by the backend
            setSuccessMsg(`Simulated Email Sent! Your reset code is: ${res.data.demo_code}`);
            setStep(2);
        } catch (err: any) {
            setError(err.response?.data?.detail || "Failed to request reset. Please check your email.");
        } finally {
            setIsLoading(false);
        }
    };

    const handleConfirmReset = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        
        if (newPassword !== confirmPassword) {
            setError("New passwords do not match");
            return;
        }
        
        setIsLoading(true);
        try {
            await apiService.resetPassword({
                email,
                token,
                new_password: newPassword
            });
            
            // Redirect back to login with success message
            navigate('/patient/login', { state: { message: "Password reset successfully! Please log in." } });
        } catch (err: any) {
            setError(err.response?.data?.detail || "Invalid code or failed to reset password.");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-400 via-purple-100 to-white flex items-center justify-center p-4">
            
            {/* Background Decorations */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <motion.div
                    initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 2 }}
                    className="absolute top-10 left-10 w-80 h-80 bg-blue-300 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob"
                />
                <motion.div
                    initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 2, delay: 1 }}
                    className="absolute bottom-10 right-10 w-96 h-96 bg-purple-300 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob animation-delay-2000"
                />
            </div>

            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5 }}
                className="w-full max-w-md relative"
            >
                <div className="bg-white/90 backdrop-blur-xl rounded-3xl shadow-2xl overflow-hidden border border-white/50">
                    
                    {/* Header */}
                    <div className="bg-gradient-to-r from-indigo-600 to-purple-600 p-8 text-center text-white">
                        <motion.div
                            initial={{ scale: 0.8 }} animate={{ scale: 1 }} transition={{ type: "spring", stiffness: 200 }}
                            className="bg-white/20 w-16 h-16 rounded-2xl mx-auto flex items-center justify-center backdrop-blur-sm mb-4"
                        >
                            <ShieldCheck size={32} className="text-white" />
                        </motion.div>
                        <h1 className="text-2xl font-bold tracking-tight">Password Recovery</h1>
                        <p className="text-indigo-100 text-sm mt-1">
                            {step === 1 ? "Enter your email to receive a reset code" : "Enter your reset code and new password"}
                        </p>
                    </div>

                    <div className="p-8">
                        {error && (
                            <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="mb-6 bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-xl text-sm font-medium">
                                {error}
                            </motion.div>
                        )}
                        
                        {successMsg && (
                            <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="mb-6 bg-emerald-50 border border-emerald-200 text-emerald-700 px-4 py-3 rounded-xl text-sm font-bold shadow-sm">
                                {successMsg}
                            </motion.div>
                        )}

                        <AnimatePresence mode="wait">
                            {step === 1 ? (
                                <motion.form
                                    key="step1"
                                    initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 20 }}
                                    onSubmit={handleRequestReset}
                                    className="space-y-4"
                                >
                                    <div className="group">
                                        <label className="block text-sm font-semibold text-gray-700 mb-1 ml-1">Email Address</label>
                                        <div className="relative transition-all duration-300 group-focus-within:-translate-y-1">
                                            <Mail className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 group-focus-within:text-purple-500 transition-colors" size={20} />
                                            <input
                                                type="email"
                                                value={email}
                                                onChange={e => setEmail(e.target.value)}
                                                className="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-4 focus:ring-purple-100 focus:border-purple-500 transition-all outline-none font-medium text-gray-900 placeholder-gray-400"
                                                placeholder="name@example.com"
                                                required
                                            />
                                        </div>
                                    </div>

                                    <button
                                        type="submit"
                                        disabled={isLoading || !email}
                                        className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-bold py-3.5 rounded-xl shadow-lg hover:shadow-purple-500/30 transition-all disabled:opacity-70 mt-4 flex justify-center items-center"
                                    >
                                        {isLoading ? "Sending..." : "Send Reset Code"}
                                    </button>
                                </motion.form>
                            ) : (
                                <motion.form
                                    key="step2"
                                    initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}
                                    onSubmit={handleConfirmReset}
                                    className="space-y-4"
                                >
                                    <div className="group">
                                        <label className="block text-sm font-semibold text-gray-700 mb-1 ml-1">6-Digit Reset Code</label>
                                        <div className="relative transition-all duration-300 group-focus-within:-translate-y-1">
                                            <KeyRound className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 group-focus-within:text-purple-500 transition-colors" size={20} />
                                            <input
                                                type="text"
                                                maxLength={6}
                                                value={token}
                                                onChange={e => setToken(e.target.value.replace(/\D/g, ''))}
                                                className="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-4 focus:ring-purple-100 focus:border-purple-500 transition-all outline-none font-bold text-center text-gray-900 tracking-widest text-lg"
                                                placeholder="000000"
                                                required
                                            />
                                        </div>
                                    </div>

                                    <div className="group">
                                        <label className="block text-sm font-semibold text-gray-700 mb-1 ml-1">New Password</label>
                                        <div className="relative transition-all duration-300 group-focus-within:-translate-y-1">
                                            <Lock className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 group-focus-within:text-purple-500 transition-colors" size={20} />
                                            <input
                                                type="password"
                                                value={newPassword}
                                                onChange={e => setNewPassword(e.target.value)}
                                                className="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-4 focus:ring-purple-100 focus:border-purple-500 transition-all outline-none font-medium text-gray-900"
                                                placeholder="••••••••"
                                                required
                                            />
                                        </div>
                                    </div>

                                    <div className="group">
                                        <label className="block text-sm font-semibold text-gray-700 mb-1 ml-1">Confirm New Password</label>
                                        <div className="relative transition-all duration-300 group-focus-within:-translate-y-1">
                                            <Lock className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 group-focus-within:text-purple-500 transition-colors" size={20} />
                                            <input
                                                type="password"
                                                value={confirmPassword}
                                                onChange={e => setConfirmPassword(e.target.value)}
                                                className="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-4 focus:ring-purple-100 focus:border-purple-500 transition-all outline-none font-medium text-gray-900"
                                                placeholder="••••••••"
                                                required
                                            />
                                        </div>
                                    </div>

                                    <button
                                        type="submit"
                                        disabled={isLoading || !token || !newPassword || !confirmPassword}
                                        className="w-full bg-gradient-to-r from-emerald-500 to-teal-500 text-white font-bold py-3.5 rounded-xl shadow-lg hover:shadow-emerald-500/30 transition-all disabled:opacity-70 mt-2 flex justify-center items-center"
                                    >
                                        {isLoading ? "Saving..." : "Verify & Reset Password"}
                                    </button>
                                </motion.form>
                            )}
                        </AnimatePresence>

                        <div className="mt-8 pt-6 border-t border-gray-100 text-center">
                            <Link to="/patient/login" className="text-gray-500 text-sm hover:text-purple-600 font-medium transition-colors">
                                &larr; Back to Login
                            </Link>
                        </div>
                    </div>
                </div>
            </motion.div>
        </div>
    );
}
