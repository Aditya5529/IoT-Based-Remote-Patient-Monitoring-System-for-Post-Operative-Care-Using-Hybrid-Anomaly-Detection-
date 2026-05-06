import React, { useEffect, useState } from 'react';
import { apiService } from '../../services/api';
import { Shield, Activity, Users, UserPlus, Wifi } from 'lucide-react';

export default function AdminDashboard() {
    const [health, setHealth] = useState<any>(null);
    const [doctors, setDoctors] = useState<any[]>([]);
    const [patients, setPatients] = useState<any[]>([]);
    const [selectedDoctor, setSelectedDoctor] = useState('');
    const [selectedPatient, setSelectedPatient] = useState('');
    const [message, setMessage] = useState('');
    const [devices, setDevices] = useState<any[]>([]);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            const [h, d, p, dev] = await Promise.all([
                apiService.getSystemHealth(),
                apiService.getDoctors(),
                apiService.getPatients(),
                apiService.getIoTDevices().catch(() => ({ data: [] }))
            ]);
            setHealth(h.data);
            setDoctors(d.data);
            setPatients(p.data);
            setDevices(dev.data || []);
        } catch (err) {
            console.error("Failed to load admin data", err);
        }
    };

    const handleAssign = async () => {
        if (!selectedDoctor || !selectedPatient) return;
        try {
            await apiService.assignDoctor({ doctor_id: selectedDoctor, patient_id: selectedPatient });
            setMessage('✅ Assignment Successful');
            setTimeout(() => setMessage(''), 3000);
        } catch (err) {
            setMessage('❌ Assignment Failed');
        }
    };

    if (!health) return <div className="p-8">Loading Admin Portal...</div>;

    return (
        <div className="min-h-screen bg-gray-100 p-8">
            <header className="mb-8 flex items-center">
                <Shield className="text-indigo-600 mr-4" size={32} />
                <h1 className="text-3xl font-bold text-gray-800">Admin Portal</h1>
            </header>

            {/* System Health */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                    <h3 className="text-gray-500 text-sm font-semibold uppercase tracking-wider mb-2">DB Status</h3>
                    <div className="flex items-center">
                        <div className={`w-3 h-3 rounded-full mr-2 ${health.db_status === 'connected' ? 'bg-green-500' : 'bg-red-500'}`}></div>
                        <span className="text-xl font-bold">{health.db_status}</span>
                    </div>
                </div>
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                    <h3 className="text-gray-500 text-sm font-semibold uppercase tracking-wider mb-2">ML Engine</h3>
                    <div className="flex items-center">
                        <div className={`w-3 h-3 rounded-full mr-2 ${health.ml_engine_status === 'loaded' ? 'bg-green-500' : 'bg-yellow-500'}`}></div>
                        <span className="text-xl font-bold">{health.ml_engine_status}</span>
                    </div>
                </div>
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                    <h3 className="text-gray-500 text-sm font-semibold uppercase tracking-wider mb-2">Total Users</h3>
                    <div className="flex justify-between">
                        <span>Patients: <b>{health.counts.patients}</b></span>
                        <span>Doctors: <b>{health.counts.doctors}</b></span>
                    </div>
                </div>
            </div>

            {/* Assignment Section */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
                <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
                    <UserPlus className="mr-3" /> Doctor-Patient Assignment
                </h2>

                <div className="flex flex-col md:flex-row gap-4 items-end">
                    <div className="flex-1 w-full">
                        <label className="block text-sm font-medium text-gray-700 mb-2">Select Patient</label>
                        <select
                            className="w-full p-2 border border-gray-300 rounded-lg"
                            value={selectedPatient}
                            onChange={e => setSelectedPatient(e.target.value)}
                        >
                            <option value="">-- Choose Patient --</option>
                            {patients.map(p => (
                                <option key={p.id} value={p.id}>{p.full_name} ({p.email})</option>
                            ))}
                        </select>
                    </div>

                    <div className="flex-1 w-full">
                        <label className="block text-sm font-medium text-gray-700 mb-2">Assign Doctor</label>
                        <select
                            className="w-full p-2 border border-gray-300 rounded-lg"
                            value={selectedDoctor}
                            onChange={e => setSelectedDoctor(e.target.value)}
                        >
                            <option value="">-- Choose Doctor --</option>
                            {doctors.map(d => (
                                <option key={d.id} value={d.id}>{d.full_name} ({d.email})</option>
                            ))}
                        </select>
                    </div>

                    <button
                        onClick={handleAssign}
                        disabled={!selectedDoctor || !selectedPatient}
                        className="bg-indigo-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-indigo-700 disabled:bg-gray-400"
                    >
                        Assign
                    </button>
                </div>
                {message && <p className="mt-4 text-center font-bold">{message}</p>}
            </div>
            {/* IoT Devices Section */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 mt-8">
                <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
                    <Wifi className="mr-3 text-indigo-600" /> Active IoT Devices
                </h2>
                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead className="bg-gray-50 text-gray-500">
                            <tr>
                                <th className="p-4 font-medium">Device ID</th>
                                <th className="p-4 font-medium">Assigned Patient</th>
                                <th className="p-4 font-medium">Last Seen</th>
                                <th className="p-4 font-medium">Status</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100">
                            {devices.length === 0 ? (
                                <tr><td colSpan={3} className="p-8 text-center text-gray-500">No IoT devices detected.</td></tr>
                            ) : (
                                devices.map((d: any) => {
                                    const pat = patients.find(p => p.id === d.patient_id);
                                    return (
                                        <tr key={d.device_id} className="hover:bg-gray-50">
                                            <td className="p-4 font-mono font-medium text-gray-800">{d.device_id}</td>
                                            <td className="p-4 text-indigo-600">{pat ? `${pat.full_name} (${pat.email})` : d.patient_id}</td>
                                            <td className="p-4 text-gray-600">{new Date(d.last_seen).toLocaleString()}</td>
                                            <td className="p-4">
                                                <span className={`px-2 py-1 text-xs font-semibold rounded-full ${(new Date().getTime() - new Date(d.last_seen).getTime() < 10000) ? 'bg-green-100 text-green-800' : ((new Date().getTime() - new Date(d.last_seen).getTime() > 30000) ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800')}`}>
                                                    {(new Date().getTime() - new Date(d.last_seen).getTime() < 10000) ? '🟢 Live' : ((new Date().getTime() - new Date(d.last_seen).getTime() > 30000) ? '🔴 Disconnected' : '🟡 Unstable')}
                                                </span>
                                            </td>
                                        </tr>
                                    );
                                })
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
