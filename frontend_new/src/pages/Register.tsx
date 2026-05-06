import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { UserPlus, Mail, Lock, User as UserIcon, ArrowRight } from 'lucide-react';
import { api } from '../services/api';

export default function Register() {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        confirmPassword: '',
        full_name: ''
    });
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        if (formData.password !== formData.confirmPassword) {
            setError("Passwords do not match");
            return;
        }

        setIsLoading(true);
        try {
            await api.post('/auth/register', {
                email: formData.email,
                password: formData.password,
                full_name: formData.full_name,
                role: 'patient' // Default role
            });

            // Redirect to login on success
            navigate('/patient/login', { state: { message: 'Registration successful! Please log in.' } });

        } catch (err: any) {
            console.error(err);
            if (err.response && err.response.data && err.response.data.detail) {
                setError(err.response.data.detail);
            } else {
                setError('Registration failed. Please try again.');
            }
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-red-400 via-orange-100 to-white flex items-center justify-center p-4">

            {/* Background Decorations */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <motion.div
                    initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 2 }}
                    className="absolute -bottom-24 -right-24 w-96 h-96 bg-red-300 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob"
                />
                <motion.div
                    initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 2, delay: 1 }}
                    className="absolute top-0 left-0 w-80 h-80 bg-orange-300 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob animation-delay-2000"
                />
            </div>

            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5 }}
                className="w-full max-w-lg relative"
            >
                <div className="bg-white/80 backdrop-blur-xl rounded-3xl shadow-2xl overflow-hidden border border-white/50">

                    {/* Header */}
                    <div className="relative bg-gradient-to-r from-red-600 to-orange-600 p-8 text-center text-white">
                        <motion.div
                            initial={{ scale: 0.8 }} animate={{ scale: 1 }} transition={{ type: "spring", stiffness: 200 }}
                            className="bg-white/20 w-16 h-16 rounded-2xl mx-auto flex items-center justify-center backdrop-blur-sm mb-4"
                        >
                            <UserPlus size={32} className="text-white" />
                        </motion.div>
                        <h1 className="text-2xl font-bold tracking-tight">Create Account</h1>
                        <p className="text-red-100 text-sm mt-1">Join RPM System today</p>
                    </div>

                    <div className="p-8">
                        {error && (
                            <motion.div
                                initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }}
                                className="mb-6 bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-xl text-sm flex items-center justify-center"
                            >
                                <span className="font-semibold mr-1">Error:</span> {error}
                            </motion.div>
                        )}

                        <form onSubmit={handleSubmit} className="space-y-4">

                            <div className="group">
                                <label className="block text-sm font-semibold text-gray-700 mb-1 ml-1">Full Name</label>
                                <div className="relative transition-all duration-300 group-focus-within:-translate-y-1">
                                    <UserIcon className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 group-focus-within:text-red-500 transition-colors" size={20} />
                                    <input
                                        type="text"
                                        name="full_name"
                                        value={formData.full_name}
                                        onChange={handleChange}
                                        className="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-4 focus:ring-red-100 focus:border-red-500 transition-all outline-none font-medium text-gray-900 placeholder-gray-400"
                                        placeholder="John Doe"
                                        required
                                    />
                                </div>
                            </div>

                            <div className="group">
                                <label className="block text-sm font-semibold text-gray-700 mb-1 ml-1">Email Address</label>
                                <div className="relative transition-all duration-300 group-focus-within:-translate-y-1">
                                    <Mail className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 group-focus-within:text-red-500 transition-colors" size={20} />
                                    <input
                                        type="email"
                                        name="email"
                                        value={formData.email}
                                        onChange={handleChange}
                                        className="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-4 focus:ring-red-100 focus:border-red-500 transition-all outline-none font-medium text-gray-900 placeholder-gray-400"
                                        placeholder="name@example.com"
                                        required
                                    />
                                </div>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div className="group">
                                    <label className="block text-sm font-semibold text-gray-700 mb-1 ml-1">Password</label>
                                    <div className="relative transition-all duration-300 group-focus-within:-translate-y-1">
                                        <Lock className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 group-focus-within:text-red-500 transition-colors" size={20} />
                                        <input
                                            type="password"
                                            name="password"
                                            value={formData.password}
                                            onChange={handleChange}
                                            className="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-4 focus:ring-red-100 focus:border-red-500 transition-all outline-none font-medium text-gray-900 placeholder-gray-400"
                                            placeholder="••••••••"
                                            required
                                        />
                                    </div>
                                </div>
                                <div className="group">
                                    <label className="block text-sm font-semibold text-gray-700 mb-1 ml-1">Confirm</label>
                                    <div className="relative transition-all duration-300 group-focus-within:-translate-y-1">
                                        <Lock className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 group-focus-within:text-red-500 transition-colors" size={20} />
                                        <input
                                            type="password"
                                            name="confirmPassword"
                                            value={formData.confirmPassword}
                                            onChange={handleChange}
                                            className="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-4 focus:ring-red-100 focus:border-red-500 transition-all outline-none font-medium text-gray-900 placeholder-gray-400"
                                            placeholder="••••••••"
                                            required
                                        />
                                    </div>
                                </div>
                            </div>

                            <motion.button
                                whileHover={{ scale: 1.01 }}
                                whileTap={{ scale: 0.99 }}
                                type="submit"
                                disabled={isLoading}
                                className="w-full bg-gradient-to-r from-red-600 to-orange-600 text-white font-bold py-4 rounded-xl shadow-lg hover:shadow-red-500/30 transition-all disabled:opacity-70 flex justify-center items-center group mt-6"
                            >
                                {isLoading ? (
                                    <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                    </svg>
                                ) : (
                                    <>
                                        Register Account
                                        <ArrowRight className="ml-2 group-hover:translate-x-1 transition-transform" size={20} />
                                    </>
                                )}
                            </motion.button>
                        </form>

                        <div className="mt-8 pt-6 border-t border-gray-100 text-center">
                            <p className="text-gray-500 text-sm mb-3">Already have an account?</p>
                            <Link to="/patient/login" className="text-red-600 font-bold hover:underline">Sign In Instead</Link>
                        </div>
                    </div>
                </div>
            </motion.div>
        </div>
    );
}
