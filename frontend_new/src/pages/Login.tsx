import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Activity, Lock, Mail, ArrowRight } from 'lucide-react';
import { api } from '../services/api';

export default function Login({ role = 'patient' }: { role?: 'patient' | 'doctor' | 'admin' }) {
    const { login } = useAuth();
    const navigate = useNavigate();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const isPatient = role === 'patient';
    const isAdmin = role === 'admin';

    // Theme Config
    let theme = {
        bgColor: "from-blue-400 via-indigo-100",
        headerFrom: "from-blue-500",
        headerTo: "to-indigo-500",
        iconColor: "text-blue-500",
        subTextColor: "text-blue-100",
        ringColor: "focus:ring-blue-100 focus:border-blue-500",
        buttonGradient: "from-blue-600 to-indigo-600",
        buttonShadow: "hover:shadow-blue-500/30",
        bgBlob1: "bg-blue-300",
        bgBlob2: "bg-purple-300"
    };

    if (isPatient) {
        theme = {
            bgColor: "from-red-400 via-orange-100",
            headerFrom: "from-red-500",
            headerTo: "to-orange-500",
            iconColor: "text-red-500",
            subTextColor: "text-red-100",
            ringColor: "focus:ring-red-100 focus:border-red-500",
            buttonGradient: "from-red-600 to-orange-600",
            buttonShadow: "hover:shadow-red-500/30",
            bgBlob1: "bg-red-300",
            bgBlob2: "bg-orange-300"
        };
    } else if (isAdmin) {
        theme = {
            bgColor: "from-purple-400 via-fuchsia-100",
            headerFrom: "from-purple-500",
            headerTo: "to-fuchsia-500",
            iconColor: "text-purple-500",
            subTextColor: "text-purple-100",
            ringColor: "focus:ring-purple-100 focus:border-purple-500",
            buttonGradient: "from-purple-600 to-fuchsia-600",
            buttonShadow: "hover:shadow-purple-500/30",
            bgBlob1: "bg-purple-300",
            bgBlob2: "bg-pink-300"
        };
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);
        try {
            // First exchange credentials for token
            const params = new URLSearchParams();
            params.append('username', email);
            params.append('password', password);

            const response = await api.post('/auth/login', params, {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            });

            // Then update context
            await login(response.data.access_token);

            // Redirect based on role
            // Hardcoded logic as requested in prompt A, B, C, D
            if (role === 'doctor') {
                navigate('/doctor/dashboard');
            } else if (role === 'admin') {
                navigate('/admin/dashboard');
            } else {
                navigate('/patient/dashboard');
            }

        } catch (err: any) {
            console.error(err);
            if (err.response?.status === 401 || err.response?.status === 400) {
                setError('Invalid credentials. Please check your email and password.');
            } else {
                setError('Login failed. Please try again later.');
            }
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className={`min-h-screen bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] ${theme.bgColor} to-white flex items-center justify-center p-4`}>

            {/* Background Decorations */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <motion.div
                    initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 2 }}
                    className={`absolute -top-24 -left-24 w-96 h-96 ${theme.bgBlob1} rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob`}
                />
                <motion.div
                    initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 2, delay: 1 }}
                    className={`absolute top-0 right-0 w-96 h-96 ${theme.bgBlob2} rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob animation-delay-2000`}
                />
            </div>

            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="w-full max-w-lg relative"
            >
                <div className="bg-white/80 backdrop-blur-xl rounded-3xl shadow-2xl overflow-hidden border border-white/50">

                    {/* Header Section */}
                    <div className={`relative bg-gradient-to-r ${theme.headerFrom} ${theme.headerTo} p-8 text-center text-white overflow-hidden`}>
                        <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-10"></div>
                        <motion.div
                            initial={{ scale: 0.8 }} animate={{ scale: 1 }} transition={{ type: "spring", stiffness: 200 }}
                            className="bg-white/20 w-20 h-20 rounded-2xl mx-auto flex items-center justify-center backdrop-blur-sm mb-4"
                        >
                            <Activity size={40} className="text-white" />
                        </motion.div>
                        <h1 className="text-3xl font-extrabold tracking-tight mb-2">RPM System</h1>
                        <p className={`${theme.subTextColor} font-medium text-sm uppercase tracking-wider`}>
                            {role === 'patient' ? 'Patient Portal' : role === 'admin' ? 'Admin Portal' : 'Doctor Portal'}
                        </p>
                    </div>

                    <div className="p-8 md:p-10">
                        <div className="text-center mb-8">
                            <h2 className="text-2xl font-bold text-gray-800">Welcome Back</h2>
                            <p className="text-gray-500 mt-1">Sign in to access your dashboard</p>
                        </div>

                        {error && (
                            <motion.div
                                initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }}
                                className="mb-6 bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-xl text-sm flex items-center justify-center"
                            >
                                <span className="font-semibold mr-1">Error:</span> {error}
                            </motion.div>
                        )}

                        <form onSubmit={handleSubmit} className="space-y-5">
                            <div className="group">
                                <label className="block text-sm font-semibold text-gray-700 mb-1 ml-1">Email Address</label>
                                <div className="relative transition-all duration-300 group-focus-within:-translate-y-1">
                                    <Mail className={`absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 group-focus-within:${theme.iconColor} transition-colors`} size={20} />
                                    <input
                                        type="email"
                                        value={email}
                                        onChange={e => setEmail(e.target.value)}
                                        className={`w-full pl-12 pr-4 py-3.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-4 ${theme.ringColor} transition-all outline-none font-medium text-gray-900 placeholder-gray-400`}
                                        placeholder="name@example.com"
                                        required
                                    />
                                </div>
                            </div>

                            <div className="group">
                                <label className="block text-sm font-semibold text-gray-700 mb-1 ml-1">Password</label>
                                <div className="relative transition-all duration-300 group-focus-within:-translate-y-1">
                                    <Lock className={`absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 group-focus-within:${theme.iconColor} transition-colors`} size={20} />
                                    <input
                                        type="password"
                                        value={password}
                                        onChange={e => setPassword(e.target.value)}
                                        className={`w-full pl-12 pr-4 py-3.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-4 ${theme.ringColor} transition-all outline-none font-medium text-gray-900 placeholder-gray-400`}
                                        placeholder="••••••••"
                                        required
                                    />
                                </div>
                            </div>

                            <div className="flex items-center justify-between text-sm">
                                <label className="flex items-center text-gray-600 cursor-pointer">
                                    <input type="checkbox" className={`w-4 h-4 rounded border-gray-300 ${isPatient ? 'text-red-500 focus:ring-red-500' : 'text-blue-500 focus:ring-blue-500'} mr-2`} />
                                    Remember me
                                </label>
                                <Link to="/forgot-password" className={`font-semibold ${isPatient ? 'text-red-600 hover:text-red-700' : 'text-blue-600 hover:text-blue-700'} hover:underline`}>Forgot password?</Link>
                            </div>

                            <motion.button
                                whileHover={{ scale: 1.01 }}
                                whileTap={{ scale: 0.99 }}
                                type="submit"
                                disabled={isLoading}
                                className={`w-full bg-gradient-to-r ${theme.buttonGradient} text-white font-bold py-4 rounded-xl shadow-lg ${theme.buttonShadow} transition-all disabled:opacity-70 flex justify-center items-center group`}
                            >
                                {isLoading ? (
                                    <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                    </svg>
                                ) : (
                                    <>
                                        Sign In
                                        <ArrowRight className="ml-2 group-hover:translate-x-1 transition-transform" size={20} />
                                    </>
                                )}
                            </motion.button>
                        </form>

                        {isPatient && (
                            <div className="mt-8 pt-6 border-t border-gray-100 text-center">
                                <p className="text-gray-500 text-sm mb-3">Don't have an account?</p>
                                <Link to="/register" className="inline-block px-6 py-2 bg-red-50 text-red-600 font-bold rounded-lg border border-red-100 hover:bg-red-100 transition-colors">Create Patient Account</Link>
                            </div>
                        )}

                        {/* Demo Credentials Panel - Ideally only in DEV */}
                        <div className="mt-6 bg-gray-50 rounded-lg p-3 text-xs text-gray-500 text-center font-mono border border-gray-100">
                            <span className="block mb-1 text-xs uppercase font-bold text-gray-400">Demo Credentials</span>
                            {isPatient ? (
                                <span className="font-bold cursor-pointer hover:text-red-600 transition-colors" onClick={() => { setEmail('patient@rpm.com'); setPassword('pat123'); }}>patient@rpm.com / pat123</span>
                            ) : isAdmin ? (
                                <span className="font-bold cursor-pointer hover:text-purple-600 transition-colors" onClick={() => { setEmail('admin@rpm.com'); setPassword('admin123'); }}>admin@rpm.com / admin123</span>
                            ) : (
                                <span className="font-bold cursor-pointer hover:text-blue-600 transition-colors" onClick={() => { setEmail('doctor@rpm.com'); setPassword('doc123'); }}>doctor@rpm.com / doc123</span>
                            )}
                        </div>
                    </div>
                </div>
            </motion.div>
        </div>
    );
}
