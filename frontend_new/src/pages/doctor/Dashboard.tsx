import React, { useEffect, useState } from 'react';
import { apiService } from '../../services/api';
import { Users, Bell, Activity, Wifi } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function DoctorDashboard() {
    const [patients, setPatients] = useState<any[]>([]);
    const [alerts, setAlerts] = useState<any[]>([]);
    const [activeHistoryPatient, setActiveHistoryPatient] = useState<string | null>(null);
    const [patientVitals, setPatientVitals] = useState<any[]>([]);
    const [iotData, setIotData] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();
    const [showHistory, setShowHistory] = useState(false);

    const handleAcknowledgeAlert = async (alertId: string) => {
        try {
            await apiService.acknowledgeAlert(alertId);
            loadData();
        } catch (err) {
            console.error("Failed to acknowledge alert", err);
        }
    };

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            const [patRes, alertRes] = await Promise.all([
                apiService.getMyPatients(),
                apiService.getAlerts().catch(() => ({ data: [] })) // Handle if endpoint not ready
            ]);
            setPatients(patRes.data);
            setAlerts(alertRes.data || []);
        } catch (err) {
            console.error("Failed to load dashboard data", err);
        } finally {
            setLoading(false);
        }
    };

    const viewPatientHistory = async (patientId: string) => {
        if (activeHistoryPatient === patientId) {
            setActiveHistoryPatient(null);
            setIotData(null);
            return;
        }
        setActiveHistoryPatient(patientId);
        try {
            const res = await fetch(`http://localhost:8000/api/v1/vitals/history?patient_id=${patientId}`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
            });
            const data = await res.json();
            setPatientVitals(data.sort((a: any, b: any) => new Date(b.ts).getTime() - new Date(a.ts).getTime()));
            
            // Fetch IoT Data
            try {
                const iotRes = await apiService.getLatestIoTVitals(patientId);
                if (iotRes.data?.status === 'success') {
                    setIotData(iotRes.data.data);
                } else {
                    setIotData(null);
                }
            } catch (e) {
                setIotData(null);
            }
        } catch (err) {
            console.error("Failed to load patient history", err);
        }
    };

    if (loading) return <div className="p-8">Loading Dashboard...</div>;

    const criticalAlerts = alerts.filter(a => a.status === 'new' && (a.severity === 'critical' || a.severity === 'warning'));

    return (
        <div className="min-h-screen bg-gray-50 p-6">
            <header className="mb-8 flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold text-gray-800">Doctor Portal</h1>
                    <p className="text-gray-500">Overview of assigned patients</p>
                </div>
                <button onClick={() => navigate('/doctor/messages')} className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700">
                    Messages
                </button>
            </header>

            {/* Stats Overview */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center">
                    <div className="p-3 bg-blue-100 rounded-full mr-4">
                        <Users className="text-blue-600" size={24} />
                    </div>
                    <div>
                        <p className="text-sm text-gray-500">Assigned Patients</p>
                        <p className="text-2xl font-bold text-gray-800">{patients.length}</p>
                    </div>
                </div>

                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center">
                    <div className={`p-3 rounded-full mr-4 ${criticalAlerts.length > 0 ? 'bg-red-100' : 'bg-green-100'}`}>
                        <Bell className={criticalAlerts.length > 0 ? 'text-red-600' : 'text-green-600'} size={24} />
                    </div>
                    <div>
                        <p className="text-sm text-gray-500">Active Alerts</p>
                        <p className="text-2xl font-bold text-gray-800">{criticalAlerts.length}</p>
                    </div>
                </div>

                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center">
                    <div className="p-3 bg-purple-100 rounded-full mr-4">
                        <Activity className="text-purple-600" size={24} />
                    </div>
                    <div>
                        <p className="text-sm text-gray-500">System Status</p>
                        <p className="text-2xl font-bold text-gray-800">Online</p>
                    </div>
                </div>
            </div>

            {/* Alerts Section (if any) */}
            {criticalAlerts.length > 0 && (
                <div className="mb-8 bg-red-50 border border-red-200 rounded-xl p-6">
                    <h2 className="text-xl font-semibold text-red-800 mb-4 flex items-center">
                        <Bell className="mr-2" /> Critical Attention Needed
                    </h2>
                    <div className="space-y-3">
                        {criticalAlerts.map(alert => (
                            <div key={alert.id} className="bg-white p-4 rounded-lg shadow-sm border border-red-100 flex justify-between items-center">
                                <div>
                                    <span className="font-bold text-gray-800">{alert.vital_type} Alert</span>
                                    <span className="text-gray-600 ml-2">- {alert.reason}</span>
                                    <p className="text-xs text-gray-500 mt-1">{new Date(alert.ts).toLocaleString()}</p>
                                </div>
                                <button onClick={() => handleAcknowledgeAlert(alert.id)} className="text-sm bg-red-100 text-red-700 px-3 py-1 rounded hover:bg-red-200 cursor-pointer">
                                    Acknowledge
                                </button>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Toggles */}
            <div className="mb-6 flex space-x-4 border-b border-gray-200">
                <button 
                    onClick={() => setShowHistory(false)} 
                    className={`py-2 px-4 font-semibold ${!showHistory ? 'border-b-2 border-indigo-600 text-indigo-600' : 'text-gray-500 hover:text-gray-700'}`}>
                    My Patients
                </button>
                <button 
                    onClick={() => setShowHistory(true)} 
                    className={`py-2 px-4 font-semibold ${showHistory ? 'border-b-2 border-indigo-600 text-indigo-600' : 'text-gray-500 hover:text-gray-700'}`}>
                    ALERT/ANOMALY HISTORY
                </button>
            </div>

            {!showHistory ? (
            <>
            {/* Patient List */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                <div className="p-6 border-b border-gray-100">
                    <h2 className="text-xl font-bold text-gray-800">My Patients</h2>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead className="bg-gray-50 text-gray-500">
                            <tr>
                                <th className="p-4 font-medium">Name</th>
                                <th className="p-4 font-medium">Email</th>
                                <th className="p-4 font-medium">Status</th>
                                <th className="p-4 font-medium">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100">
                            {patients.length === 0 ? (
                                <tr><td colSpan={4} className="p-8 text-center text-gray-500">No patients assigned.</td></tr>
                            ) : (
                                patients.map((patient) => (
                                    <tr key={patient.id} className="hover:bg-gray-50">
                                        <td className="p-4 font-medium text-gray-800">
                                            {patient.full_name || "Unknown"}
                                        </td>
                                        <td className="p-4 text-gray-600">{patient.email}</td>
                                        <td className="p-4">
                                            <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm">
                                                Active
                                            </span>
                                        </td>
                                        <td className="p-4 space-x-3">
                                            <button
                                                onClick={() => viewPatientHistory(patient.id)}
                                                className="text-teal-600 hover:text-teal-800 font-medium"
                                            >
                                                {activeHistoryPatient === patient.id ? 'Hide Vitals' : 'Vital History'}
                                            </button>
                                            <button
                                                onClick={() => navigate('/doctor/messages')}
                                                className="text-indigo-600 hover:text-indigo-800 font-medium"
                                            >
                                                Message
                                            </button>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {activeHistoryPatient && (
                <div className="mt-8 bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                    <div className="p-6 border-b border-gray-100 flex justify-between">
                        <h2 className="text-xl font-bold text-gray-800">Patient Vital History Overview</h2>
                        <button onClick={() => setActiveHistoryPatient(null)} className="text-gray-500 hover:text-red-500">Close</button>
                    </div>
                    
                    {/* Doctor Live IoT View */}
                    <div className="px-6 pt-6">
                        <div className={`p-4 rounded-lg flex justify-between items-center ${iotData ? 'bg-blue-50 border border-blue-200' : 'bg-gray-50 border border-gray-200'}`}>
                            <div className="flex items-center">
                                <Wifi className={`mr-2 ${iotData ? ((new Date().getTime() - new Date(iotData.timestamp).getTime() < 10000) ? 'text-green-600 animate-pulse' : ((new Date().getTime() - new Date(iotData.timestamp).getTime() > 30000) ? 'text-red-600' : 'text-yellow-600')) : 'text-gray-400'}`} size={20} />
                                <span className={`font-semibold ${iotData ? 'text-blue-900' : 'text-gray-600'}`}>
                                    {iotData ? ((new Date().getTime() - new Date(iotData.timestamp).getTime() < 10000) ? '🟢 Live Device Connected' : ((new Date().getTime() - new Date(iotData.timestamp).getTime() > 30000) ? '🔴 Device Disconnected' : '🟡 Unstable Connection')) : 'No Recent Device Data'}
                                </span>
                            </div>
                            {iotData && (
                                <div className="flex space-x-6">
                                    <div>
                                        <span className="text-xs text-blue-500 uppercase font-bold block">HR</span>
                                        <span className="text-lg font-bold text-blue-900">{iotData.heart_rate} bpm</span>
                                    </div>
                                    <div>
                                        <span className="text-xs text-blue-500 uppercase font-bold block">SpO2</span>
                                        <span className="text-lg font-bold text-blue-900">{iotData.spo2}%</span>
                                    </div>
                                    <div>
                                        <span className="text-xs text-blue-500 uppercase font-bold block">Temp</span>
                                        <span className="text-lg font-bold text-blue-900">{iotData.temperature}°C</span>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>

                    <div className="p-6 overflow-y-auto max-h-96">
                        <table className="w-full text-left">
                            <thead className="bg-gray-50 text-gray-500">
                                <tr>
                                    <th className="p-4 font-medium">Time Logged</th>
                                    <th className="p-4 font-medium">Vital Sign Data</th>
                                    <th className="p-4 font-medium">Recorded Value</th>
                                    <th className="p-4 font-medium">Source</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100">
                                {patientVitals.length === 0 ? (
                                   <tr><td colSpan={3} className="p-6 text-center text-gray-400">No history recorded.</td></tr> 
                                ) : (
                                    patientVitals.map(v => (
                                        <tr key={v.id} className="hover:bg-gray-50">
                                            <td className="p-4">{new Date(v.ts).toLocaleString()}</td>
                                            <td className="p-4 uppercase font-semibold text-gray-700">{v.vital_type.replace('_', ' ')}</td>
                                            <td className="p-4 font-bold text-indigo-700">{v.value} {v.unit}</td>
                                            <td className="p-4">
                                                <span className={`px-2 py-1 text-xs font-semibold rounded ${v.source?.toLowerCase().includes('iot') || v.source?.toLowerCase().includes('esp32') ? 'bg-blue-100 text-blue-800' : (v.source?.toLowerCase().includes('thingspeak') ? 'bg-teal-100 text-teal-800' : 'bg-gray-100 text-gray-800')}`}>
                                                    {v.source || 'Manual'}
                                                </span>
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
            </>
            ) : (
                <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                    <div className="p-6 border-b border-gray-100">
                        <h2 className="text-xl font-bold text-gray-800">Alert/Anomaly History</h2>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full text-left">
                            <thead className="bg-gray-50 text-gray-500">
                                <tr>
                                    <th className="p-4 font-medium">Time</th>
                                    <th className="p-4 font-medium">Patient Name</th>
                                    <th className="p-4 font-medium">Alert Type</th>
                                    <th className="p-4 font-medium">Severity</th>
                                    <th className="p-4 font-medium">Reason</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100">
                                {alerts.filter(a => a.status === 'acknowledged' || a.status === 'resolved').length === 0 ? (
                                    <tr><td colSpan={5} className="p-8 text-center text-gray-500">No previous alerts found.</td></tr>
                                ) : (
                                    alerts.filter(a => a.status === 'acknowledged' || a.status === 'resolved').map((alert) => {
                                        const p = patients.find(pat => pat.id === alert.patient_id);
                                        return (
                                            <tr key={alert.id} className="hover:bg-gray-50">
                                                <td className="p-4 text-gray-500">{new Date(alert.ts).toLocaleString()}</td>
                                                <td className="p-4 font-medium text-gray-800">{p ? p.full_name : 'Unknown'}</td>
                                                <td className="p-4 font-bold text-gray-800 uppercase">{alert.vital_type.replace('_', ' ')}</td>
                                                <td className="p-4">
                                                    <span className={`px-2 py-1 text-xs font-semibold rounded ${alert.severity === 'critical' ? 'bg-red-100 text-red-800' : (alert.severity === 'warning' ? 'bg-orange-100 text-orange-800' : 'bg-blue-100 text-blue-800')}`}>
                                                        {alert.severity.toUpperCase()}
                                                    </span>
                                                </td>
                                                <td className="p-4 text-gray-700 text-sm">{alert.reason}</td>
                                            </tr>
                                        );
                                    })
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
}
