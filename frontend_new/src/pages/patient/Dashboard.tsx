import React, { useEffect, useState } from 'react';
import { apiService } from '../../services/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Activity, Heart, Thermometer, Wifi } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import AddVitalsForm from '../../components/AddVitalsForm';

export default function PatientDashboard() {
    const [vitals, setVitals] = useState<any[]>([]);
    const [alerts, setAlerts] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [iotData, setIotData] = useState<any>(null);
    const userDetails = JSON.parse(localStorage.getItem('user') || '{}');
    const navigate = useNavigate();
    const [activeTab, setActiveTab] = useState<'charts' | 'history' | 'alerts'>('charts');

    const handleAcknowledgeAlert = async (alertId: string) => {
        try {
            await apiService.acknowledgeAlert(alertId);
            loadVitals();
        } catch (err) {
            console.error("Failed to acknowledge alert", err);
        }
    };
    
    const handleAcknowledgeAllHeartRisks = async () => {
        const heartRisks = alerts.filter(a => a.status === 'new' && a.vital_type === 'HEART_RISK_ANOMALY');
        for (const alert of heartRisks) {
            await handleAcknowledgeAlert(alert.id);
        }
    };

    useEffect(() => {
        loadVitals();
        
        // Lightweight polling for IoT live data every 5 seconds
        const interval = setInterval(() => {
            if (userDetails?.id) {
                apiService.getLatestIoTVitals(userDetails.id)
                    .then(res => {
                        if (res.data?.status === 'success') {
                            setIotData(res.data.data);
                        }
                    })
                    .catch(err => console.error('IoT Polling Error:', err));
            }
        }, 5000);
        
        return () => clearInterval(interval);
    }, []);

    const loadVitals = async () => {
        try {
            const [res, alertRes] = await Promise.all([
                apiService.getVitalsHistory(),
                apiService.getAlerts().catch(() => ({ data: [] }))
            ]);
            // Sort by TS ascending for chart
            const sorted = res.data.sort((a: any, b: any) => new Date(a.ts).getTime() - new Date(b.ts).getTime());
            setVitals(sorted);
            setAlerts(alertRes.data || []);
        } catch (err) {
            console.error("Failed to load vitals", err);
        } finally {
            setLoading(false);
        }
    };

    // Filter for HR chart
    const hrData = vitals.filter(v => v.vital_type === 'heart_rate').map(v => ({
        time: new Date(v.ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        value: v.value
    }));

    const spo2Data = vitals.filter(v => v.vital_type === 'spo2').map(v => ({
        time: new Date(v.ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        value: v.value
    }));

    if (loading) return <div className="p-8 text-center">Loading Health Data...</div>;

    const latestHR = vitals.find(v => v.vital_type === 'heart_rate');
    const latestSpO2 = vitals.find(v => v.vital_type === 'spo2');
    const latestTemp = vitals.find(v => v.vital_type === 'temperature');

    return (
        <div className="min-h-screen bg-gray-50 p-6">
            <header className="mb-8 flex justify-between items-start">
                <div>
                    <h1 className="text-3xl font-bold text-gray-800">My Health Dashboard</h1>
                    <p className="text-gray-500">Real-time vital monitoring</p>
                </div>
                {/* Pass loadVitals to refresh data after submission */}
                <div className="flex gap-4">
                    <button
                        onClick={() => navigate('/patient/messages')}
                        className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 font-medium flex items-center"
                    >
                        Consult Doctor
                    </button>
                    <AddVitalsForm onVitalAdded={loadVitals} />
                </div>
            </header>

            {/* Live IoT Vitals Section */}
            {iotData && (
                <div className="mb-8 bg-blue-50 border border-blue-200 rounded-xl p-6 shadow-sm relative overflow-hidden">
                    <div className="flex justify-between items-center mb-4">
                        <h2 className="text-xl font-bold text-blue-900 flex items-center">
                            <Wifi className={`mr-2 ${(new Date().getTime() - new Date(iotData.timestamp).getTime() < 10000) ? 'text-green-600 animate-pulse' : ((new Date().getTime() - new Date(iotData.timestamp).getTime() > 30000) ? 'text-red-600' : 'text-yellow-600')}`} size={24} />
                            Live IoT Device Sync: {(new Date().getTime() - new Date(iotData.timestamp).getTime() < 10000) ? '🟢 Live' : ((new Date().getTime() - new Date(iotData.timestamp).getTime() > 30000) ? '🔴 Disconnected' : '🟡 Unstable')}
                        </h2>
                        <span className="bg-blue-600 text-white text-xs px-2 py-1 rounded font-semibold uppercase tracking-wider">
                            Source: {iotData.source}
                        </span>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="bg-white p-4 rounded-lg shadow-sm border border-blue-100">
                            <p className="text-sm text-blue-500 font-medium mb-1">Live Heart Rate</p>
                            <p className="text-2xl font-bold text-blue-900">{iotData.heart_rate} <span className="text-sm font-normal">bpm</span></p>
                        </div>
                        <div className="bg-white p-4 rounded-lg shadow-sm border border-blue-100">
                            <p className="text-sm text-blue-500 font-medium mb-1">Live SpO2</p>
                            <p className="text-2xl font-bold text-blue-900">{iotData.spo2} <span className="text-sm font-normal">%</span></p>
                        </div>
                        <div className="bg-white p-4 rounded-lg shadow-sm border border-blue-100">
                            <p className="text-sm text-blue-500 font-medium mb-1">Live Temp</p>
                            <p className="text-2xl font-bold text-blue-900">{iotData.temperature} <span className="text-sm font-normal">°C</span></p>
                        </div>
                        <div className="bg-white p-4 rounded-lg shadow-sm border border-blue-100">
                            <p className="text-sm text-blue-500 font-medium mb-1">Last Updated</p>
                            <p className="text-sm font-bold text-blue-900 mt-2">{new Date(iotData.timestamp).toLocaleTimeString()}</p>
                        </div>
                    </div>
                </div>
            )}

            {/* ML Anomaly / Heart Risk Alerts */}
            {alerts.some(a => a.status === 'new' && a.vital_type === 'HEART_RISK_ANOMALY') ? (
                <div className="mb-8 bg-gradient-to-r from-red-600 to-rose-600 rounded-2xl p-6 shadow-xl shadow-red-500/20 text-white relative overflow-hidden">
                    <div className="absolute -top-10 -right-10 w-40 h-40 bg-white/10 rounded-full blur-2xl"></div>
                    <div className="flex justify-between items-start mb-3 relative z-10">
                        <h2 className="text-xl font-bold flex items-center">
                            <Activity className="mr-3 animate-pulse text-red-200" size={28} /> 
                            CRITICAL HEART RISK WARNING
                        </h2>
                        <button 
                            onClick={handleAcknowledgeAllHeartRisks} 
                            className="bg-white/20 hover:bg-white/30 text-white font-bold py-1 px-4 rounded-lg text-sm border border-white/30 transition-colors cursor-pointer">
                            ACKNOWLEDGE
                        </button>
                    </div>
                    <div className="space-y-4 relative z-10">
                        {alerts.filter(a => a.status === 'new' && a.vital_type === 'HEART_RISK_ANOMALY').map(alert => {
                            const [reason, rec] = alert.reason.split(' | RECOMMENDATION: ');
                            return (
                                <div key={alert.id} className="bg-black/20 rounded-xl p-4 backdrop-blur-sm border border-white/10">
                                    <p className="font-medium text-red-50 text-sm mb-2">{reason}</p>
                                    {rec && (
                                        <div className="bg-white/10 rounded-lg p-3 text-sm font-bold border-l-4 border-red-300">
                                            💡 {rec}
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                </div>
            ) : (
                <div className="mb-8 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-2xl p-6 shadow-xl shadow-emerald-500/20 text-white relative overflow-hidden">
                    <div className="absolute -top-10 -right-10 w-40 h-40 bg-white/10 rounded-full blur-2xl"></div>
                    <h2 className="text-xl font-bold flex items-center mb-1 relative z-10">
                        <Heart className="mr-3 text-emerald-100" size={28} /> 
                        AI Engine: Healthy Status Verified ✅
                    </h2>
                    <p className="text-emerald-50 font-medium relative z-10 ml-10">
                        Your latest vitals have been successfully analyzed by the DAGMM & Isolation Forest anomaly models. No significant heart risks detected.
                    </p>
                </div>
            )}

            {/* Standard Alerts Section (Patient View) */}
            {alerts.some(a => a.status === 'new' && a.vital_type !== 'HEART_RISK_ANOMALY') && (
                <div className="mb-8 bg-orange-50 border border-orange-200 rounded-xl p-4">
                    <h2 className="text-lg font-bold text-orange-800 flex items-center">
                        <span className="mr-2">⚠️</span> General Health Alerts
                    </h2>
                    <ul className="mt-2 space-y-1">
                        {alerts.filter(a => a.status === 'new' && a.vital_type !== 'HEART_RISK_ANOMALY').map(alert => (
                            <li key={alert.id} className="text-orange-700 text-sm flex justify-between items-center bg-white/50 p-2 rounded">
                                <span><b>{alert.vital_type}:</b> {alert.reason} ({new Date(alert.ts).toLocaleTimeString()})</span>
                                <button onClick={() => handleAcknowledgeAlert(alert.id)} className="bg-orange-200 hover:bg-orange-300 text-orange-800 px-3 py-1 rounded text-xs font-bold cursor-pointer">ACKNOWLEDGE</button>
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center">
                    <div className="p-3 bg-red-100 rounded-full mr-4">
                        <Heart className="text-red-600" size={24} />
                    </div>
                    <div>
                        <p className="text-sm text-gray-500">Heart Rate</p>
                        <p className="text-2xl font-bold text-gray-800">{latestHR ? `${Math.round(latestHR.value)} bpm` : '--'}</p>
                    </div>
                </div>

                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center">
                    <div className="p-3 bg-blue-100 rounded-full mr-4">
                        <Activity className="text-blue-600" size={24} />
                    </div>
                    <div>
                        <p className="text-sm text-gray-500">SpO2</p>
                        <p className="text-2xl font-bold text-gray-800">{latestSpO2 ? `${latestSpO2.value.toFixed(1)} %` : '--'}</p>
                    </div>
                </div>

                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center">
                    <div className="p-3 bg-orange-100 rounded-full mr-4">
                        <Thermometer className="text-orange-600" size={24} />
                    </div>
                    <div>
                        <p className="text-sm text-gray-500">Temperature</p>
                        <p className="text-2xl font-bold text-gray-800">{latestTemp ? `${latestTemp.value.toFixed(1)} °C` : '--'}</p>
                    </div>
                </div>
            </div>



            {/* View Tabs */}
            <div className="mb-6 flex space-x-4 border-b border-gray-200">
                <button 
                    onClick={() => setActiveTab('charts')} 
                    className={`py-2 px-4 font-semibold ${activeTab === 'charts' ? 'border-b-2 border-indigo-600 text-indigo-600' : 'text-gray-500 hover:text-gray-700'}`}>
                    Trends & Charts
                </button>
                <button 
                    onClick={() => setActiveTab('history')} 
                    className={`py-2 px-4 font-semibold ${activeTab === 'history' ? 'border-b-2 border-indigo-600 text-indigo-600' : 'text-gray-500 hover:text-gray-700'}`}>
                    Patient Vital History
                </button>
                <button 
                    onClick={() => setActiveTab('alerts')} 
                    className={`py-2 px-4 font-semibold ${activeTab === 'alerts' ? 'border-b-2 border-indigo-600 text-indigo-600' : 'text-gray-500 hover:text-gray-700'}`}>
                    ALERT/ANOMALY HISTORY
                </button>
            </div>

            {activeTab === 'charts' ? (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                        <h3 className="text-lg font-semibold mb-4 text-gray-700">Heart Rate (24h)</h3>
                        <div className="h-64">
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={hrData}>
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                    <XAxis dataKey="time" />
                                    <YAxis domain={[40, 140]} />
                                    <Tooltip />
                                    <Line type="monotone" dataKey="value" stroke="#dc2626" strokeWidth={2} dot={false} />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                        <h3 className="text-lg font-semibold mb-4 text-gray-700">SpO2 (24h)</h3>
                        <div className="h-64">
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={spo2Data}>
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                    <XAxis dataKey="time" />
                                    <YAxis domain={[80, 100]} />
                                    <Tooltip />
                                    <Line type="monotone" dataKey="value" stroke="#2563eb" strokeWidth={2} dot={false} />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                </div>
            ) : activeTab === 'history' ? (
                <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="w-full text-left">
                            <thead className="bg-gray-50 text-gray-500">
                                <tr>
                                    <th className="p-4 font-medium">Time</th>
                                    <th className="p-4 font-medium">Vital Sign</th>
                                    <th className="p-4 font-medium">Value</th>
                                    <th className="p-4 font-medium">Source</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100">
                                {vitals.slice().reverse().slice(0, 50).map((v) => (
                                    <tr key={v.id} className="hover:bg-gray-50">
                                        <td className="p-4 text-gray-500">{new Date(v.ts).toLocaleString()}</td>
                                        <td className="p-4 font-medium text-gray-800 uppercase">{v.vital_type.replace('_', ' ')}</td>
                                        <td className="p-4">
                                            <span className="font-bold">{v.value}</span> {v.unit}
                                        </td>
                                        <td className="p-4">
                                            <span className={`px-2 py-1 text-xs font-semibold rounded ${v.source?.toLowerCase().includes('iot') || v.source?.toLowerCase().includes('esp32') ? 'bg-blue-100 text-blue-800' : (v.source?.toLowerCase().includes('thingspeak') ? 'bg-teal-100 text-teal-800' : 'bg-gray-100 text-gray-800')}`}>
                                                {v.source || 'Manual'}
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            ) : (
                <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="w-full text-left">
                            <thead className="bg-gray-50 text-gray-500">
                                <tr>
                                    <th className="p-4 font-medium">Time</th>
                                    <th className="p-4 font-medium">Alert Type</th>
                                    <th className="p-4 font-medium">Severity</th>
                                    <th className="p-4 font-medium">Reason</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100">
                                {alerts.filter(a => a.status === 'acknowledged' || a.status === 'resolved').length === 0 ? (
                                    <tr><td colSpan={4} className="p-8 text-center text-gray-500">No previous alerts found.</td></tr>
                                ) : (
                                    alerts.filter(a => a.status === 'acknowledged' || a.status === 'resolved').map((alert) => (
                                        <tr key={alert.id} className="hover:bg-gray-50">
                                            <td className="p-4 text-gray-500">{new Date(alert.ts).toLocaleString()}</td>
                                            <td className="p-4 font-bold text-gray-800 uppercase">{alert.vital_type.replace('_', ' ')}</td>
                                            <td className="p-4">
                                                <span className={`px-2 py-1 text-xs font-semibold rounded ${alert.severity === 'critical' ? 'bg-red-100 text-red-800' : (alert.severity === 'warning' ? 'bg-orange-100 text-orange-800' : 'bg-blue-100 text-blue-800')}`}>
                                                    {alert.severity.toUpperCase()}
                                                </span>
                                            </td>
                                            <td className="p-4 text-gray-700 text-sm">{alert.reason}</td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
}
