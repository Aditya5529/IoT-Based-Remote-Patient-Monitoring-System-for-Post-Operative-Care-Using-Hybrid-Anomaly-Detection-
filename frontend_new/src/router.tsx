import { createBrowserRouter } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import ForgotPassword from './pages/ForgotPassword';
import PatientDashboard from './pages/patient/Dashboard';
import DoctorDashboard from './pages/doctor/Dashboard';
import AdminDashboard from './pages/admin/Dashboard';
import MessageCenter from './pages/MessageCenter';
import { AuthProvider } from './context/AuthContext';
import { Outlet, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';

import RoleSelection from './pages/RoleSelection';

const ProtectedRoute = ({ roles }: { roles: string[] }) => {
    const { user, isLoading } = useAuth();
    if (isLoading) return <div>Loading...</div>;
    if (!user) return <Navigate to="/login" />;
    if (!roles.includes(user.role)) return <div>Unauthorized</div>;
    return <Outlet />;
};

const AppLayout = () => (
    <AuthProvider>
        <Outlet />
    </AuthProvider>
);

export const router = createBrowserRouter([
    {
        element: <AppLayout />,
        children: [
            { path: '/login', element: <Login /> }, // Generic
            { path: '/register', element: <Register /> }, // Registration
            { path: '/forgot-password', element: <ForgotPassword /> }, // Password Reset

            // Patient Routes
            { path: '/patient/login', element: <Login role="patient" /> },
            {
                element: <ProtectedRoute roles={['patient']} />,
                children: [
                    { path: '/patient/dashboard', element: <PatientDashboard /> },
                    { path: '/patient/messages', element: <MessageCenter /> },
                ],
            },

            // Doctor Routes
            { path: '/doctor/login', element: <Login role="doctor" /> },
            {
                element: <ProtectedRoute roles={['doctor']} />,
                children: [
                    { path: '/doctor/dashboard', element: <DoctorDashboard /> },
                    { path: '/doctor/messages', element: <MessageCenter /> },
                ],
            },

            // Admin Routes
            { path: '/admin/login', element: <Login role="admin" /> },
            {
                element: <ProtectedRoute roles={['admin']} />,
                children: [
                    { path: '/admin/dashboard', element: <AdminDashboard /> },
                ],
            },
            { path: '/', element: <RoleSelection /> },
        ],
    },
]);
