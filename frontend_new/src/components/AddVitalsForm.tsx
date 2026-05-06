import React, { useState } from 'react';
import { apiService } from '../services/api';
import { Activity, Heart, Thermometer, Droplet, Send } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function AddVitalsForm({ onVitalAdded }: { onVitalAdded: () => void }) {
    const { user } = useAuth();
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState<{type: 'info' | 'success' | 'error', text: string} | null>(null);

    // Form State
    const [hr, setHr] = useState('');
    const [spo2, setSpo2] = useState('');
    const [temp, setTemp] = useState('');
    const [sys, setSys] = useState('');
    const [dia, setDia] = useState('');
    const [glucose, setGlucose] = useState('');
    const [resp, setResp] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);

        const vitals = [];
        const timestamp = new Date().toISOString();

        if (hr) vitals.push({ vital_type: 'heart_rate', value: parseFloat(hr), unit: 'bpm', patient_id: user?.id, ts: timestamp });
        if (spo2) vitals.push({ vital_type: 'spo2', value: parseFloat(spo2), unit: '%', patient_id: user?.id, ts: timestamp });
        if (temp) vitals.push({ vital_type: 'temperature', value: parseFloat(temp), unit: '°C', patient_id: user?.id, ts: timestamp });
        if (sys) vitals.push({ vital_type: 'bp_sys', value: parseFloat(sys), unit: 'mmHg', patient_id: user?.id, ts: timestamp });
        if (dia) vitals.push({ vital_type: 'bp_dia', value: parseFloat(dia), unit: 'mmHg', patient_id: user?.id, ts: timestamp });
        if (glucose) vitals.push({ vital_type: 'glucose', value: parseFloat(glucose), unit: 'mg/dL', patient_id: user?.id, ts: timestamp });
        if (resp) vitals.push({ vital_type: 'resp_rate', value: parseFloat(resp), unit: 'breaths/min', patient_id: user?.id, ts: timestamp });

        try {
            setMessage({ type: 'info', text: 'Vitals Submitted! ML Engine analyzing data...' });
            // Send sequentially or parallel (Parallel better)
            await Promise.all(vitals.map(v => apiService.createVital(v)));

            // Clear Form
            setHr(''); setSpo2(''); setTemp(''); setSys(''); setDia(''); setGlucose(''); setResp('');

            if (onVitalAdded) onVitalAdded();
            
            setMessage({ type: 'success', text: 'Analysis complete! Check dashboard above for ML Engine results.' });
            setTimeout(() => setMessage(null), 5000);
        } catch (err) {
            console.error(err);
            setMessage({ type: 'error', text: 'Failed to submit vitals' });
            setTimeout(() => setMessage(null), 5000);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 mb-8">
            <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
                <Activity className="mr-2 text-indigo-600" />
                Manual Vital Entry
            </h2>
            <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4 items-end">

                {/* Heart Rate */}
                <div>
                    <label className="block text-sm font-medium text-gray-600 mb-1">Heart Rate (bpm)</label>
                    <div className="relative">
                        <Heart className="absolute left-3 top-2.5 text-pink-500" size={16} />
                        <input
                            type="number"
                            step="0.1"
                            value={hr}
                            onChange={e => setHr(e.target.value)}
                            className="w-full pl-10 pr-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                            placeholder="e.g. 75"
                        />
                    </div>
                </div>

                {/* SpO2 */}
                <div>
                    <label className="block text-sm font-medium text-gray-600 mb-1">SpO2 (%)</label>
                    <div className="relative">
                        <Droplet className="absolute left-3 top-2.5 text-blue-500" size={16} />
                        <input
                            type="number"
                            step="0.1"
                            value={spo2}
                            onChange={e => setSpo2(e.target.value)}
                            className="w-full pl-10 pr-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                            placeholder="e.g. 98"
                        />
                    </div>
                </div>

                {/* Temp */}
                <div>
                    <label className="block text-sm font-medium text-gray-600 mb-1">Temperature (°C)</label>
                    <div className="relative">
                        <Thermometer className="absolute left-3 top-2.5 text-orange-500" size={16} />
                        <input
                            type="number"
                            step="0.1"
                            value={temp}
                            onChange={e => setTemp(e.target.value)}
                            className="w-full pl-10 pr-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                            placeholder="e.g. 36.6"
                        />
                    </div>
                </div>

                {/* Glucose */}
                <div>
                    <label className="block text-sm font-medium text-gray-600 mb-1">Glucose (mg/dL)</label>
                    <div className="relative">
                        <div className="absolute left-3 top-2.5 text-yellow-600 font-bold text-xs">GL</div>
                        <input
                            type="number"
                            step="0.1"
                            value={glucose}
                            onChange={e => setGlucose(e.target.value)}
                            className="w-full pl-10 pr-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                            placeholder="e.g. 100"
                        />
                    </div>
                </div>

                {/* Respiratory Rate */}
                <div>
                    <label className="block text-sm font-medium text-gray-600 mb-1">Resp. Rate (bpm)</label>
                    <div className="relative">
                        <Activity className="absolute left-3 top-2.5 text-teal-500" size={16} />
                        <input
                            type="number"
                            step="1"
                            value={resp}
                            onChange={e => setResp(e.target.value)}
                            className="w-full pl-10 pr-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                            placeholder="e.g. 16"
                        />
                    </div>
                </div>

                {/* Submit */}
                <button
                    type="submit"
                    disabled={loading}
                    className="h-10 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 transition-colors flex items-center justify-center disabled:opacity-50"
                >
                    {loading ? 'Sending...' : <><Send size={18} className="mr-2" /> Submit</>}
                </button>
            </form>
            
            {message && (
                <div className={`mt-4 p-3 rounded-lg text-sm flex items-center ${
                    message.type === 'info' ? 'bg-blue-50 text-blue-700 border border-blue-200' : 
                    message.type === 'success' ? 'bg-green-50 text-green-700 border border-green-200' : 
                    'bg-red-50 text-red-700 border border-red-200'
                }`}>
                    <Activity size={16} className="mr-2 animate-pulse" />
                    <b>{message.text}</b>
                </div>
            )}
        </div>
    );
}
