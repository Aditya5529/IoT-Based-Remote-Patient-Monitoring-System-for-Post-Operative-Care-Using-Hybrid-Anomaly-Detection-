import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const api = axios.create({
    baseURL: API_URL,
    timeout: 15000, // 15s timeout to prevent infinite hanging
    headers: {
        'Content-Type': 'application/json',
    },
});

api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export const apiService = {
    // Auth
    login: (params: URLSearchParams) => api.post('/auth/login', params, { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }),
    getMe: () => api.get('/users/me'),
    requestPasswordReset: (data: { email: string }) => api.post('/auth/request-password-reset', data),
    resetPassword: (data: { email: string; token: string; new_password: string }) => api.post('/auth/reset-password', data),
    getMyDoctors: () => api.get('/users/my-doctors'),

    // Users
    getDoctors: () => api.get('/admin/doctors'),
    getPatients: () => api.get('/admin/patients'),
    getMyPatients: () => api.get('/doctor/my-patients'),

    // Vitals
    getVitals: (userId: string) => api.get(`/vitals/${userId}`),
    getVitalsHistory: (patientId?: string) => api.get('/vitals/history', { params: { patient_id: patientId } }),
    createVital: (data: any) => api.post('/vitals/', data),

    // Alerts
    getAlerts: () => api.get('/alerts/'),
    updateAlert: (id: string, data: any) => api.patch(`/alerts/${id}`, data),
    acknowledgeAlert: (id: string) => api.put(`/alerts/${id}/acknowledge`),

    // Admin
    getSystemHealth: () => api.get('/admin/system-health'),
    assignDoctor: (data: { doctor_id: string, patient_id: string }) => api.post('/admin/assign-doctor', data),

    // Messages
    getMessages: (otherId?: string) => api.get(`/messages/${otherId || ''}`), // Updated to support direct chat history fetching
    sendMessage: (data: { recipient_id: string, content: string }) => api.post('/messages/', data),

    // IoT Data
    getLatestIoTVitals: (patientId: string) => api.get(`/iot/latest/${patientId}`),
    getThingSpeakLatest: () => api.get('/iot/thingspeak/latest'),
    getIoTDevices: () => api.get('/iot/devices'),
};
