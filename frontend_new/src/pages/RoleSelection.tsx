import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { User, Stethoscope, Shield } from 'lucide-react';

export default function RoleSelection() {
    const navigate = useNavigate();

    return (
        <div className="min-h-screen bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-100 via-white to-white flex items-center justify-center p-4">
            {/* Background Decorations */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <motion.div
                    initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 2 }}
                    className="absolute -top-24 -left-24 w-96 h-96 bg-blue-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob"
                />
                <motion.div
                    initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 2, delay: 1 }}
                    className="absolute top-0 right-0 w-96 h-96 bg-purple-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob animation-delay-2000"
                />
            </div>

            <div className="w-full max-w-4xl z-10">
                <div className="text-center mb-12">
                    <h1 className="text-4xl font-extrabold text-gray-900 mb-4 tracking-tight">RPM Vitals System</h1>
                    <p className="text-lg text-gray-600">Select your portal to continue</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-8 px-4">
                    {/* Patient Card */}
                    <motion.div
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => navigate('/patient/login')}
                        className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl border border-white/50 p-8 cursor-pointer hover:shadow-2xl transition-all group"
                    >
                        <div className="h-full flex flex-col items-center justify-center space-y-4">
                            <div className="bg-red-50 p-6 rounded-full group-hover:bg-red-100 transition-colors">
                                <User size={48} className="text-red-500" />
                            </div>
                            <h2 className="text-2xl font-bold text-gray-800">I am a Patient</h2>
                            <p className="text-gray-500 text-center">Login to track your vitals and health history.</p>
                            <span className="mt-4 px-6 py-2 bg-red-600 text-white font-semibold rounded-lg group-hover:bg-red-700 transition-colors">
                                Patient Portal &rarr;
                            </span>
                        </div>
                    </motion.div>

                    {/* Doctor Card */}
                    <motion.div
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => navigate('/doctor/login')}
                        className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl border border-white/50 p-8 cursor-pointer hover:shadow-2xl transition-all group"
                    >
                        <div className="h-full flex flex-col items-center justify-center space-y-4">
                            <div className="bg-blue-50 p-6 rounded-full group-hover:bg-blue-100 transition-colors">
                                <Stethoscope size={48} className="text-blue-600" />
                            </div>
                            <h2 className="text-2xl font-bold text-gray-800">I am a Doctor</h2>
                            <p className="text-gray-500 text-center">Login to monitor patient status and alerts.</p>
                            <span className="mt-4 px-6 py-2 bg-blue-600 text-white font-semibold rounded-lg group-hover:bg-blue-700 transition-colors">
                                Doctor Portal &rarr;
                            </span>
                        </div>
                    </motion.div>

                    {/* Admin Card */}
                    <motion.div
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => navigate('/admin/login')}
                        className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl border border-white/50 p-8 cursor-pointer hover:shadow-2xl transition-all group"
                    >
                        <div className="h-full flex flex-col items-center justify-center space-y-4">
                            <div className="bg-purple-50 p-6 rounded-full group-hover:bg-purple-100 transition-colors">
                                <Shield size={48} className="text-purple-600" />
                            </div>
                            <h2 className="text-2xl font-bold text-gray-800">I am an Admin</h2>
                            <p className="text-gray-500 text-center">Manage users, assignments, and system health.</p>
                            <span className="mt-4 px-6 py-2 bg-purple-600 text-white font-semibold rounded-lg group-hover:bg-purple-700 transition-colors">
                                Admin Portal &rarr;
                            </span>
                        </div>
                    </motion.div>
                </div>
            </div>
        </div>
    );
}
