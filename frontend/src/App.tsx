import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import { AppLayout } from './components/layout/AppLayout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Traffic from './pages/Traffic';
import Emergency from './pages/Emergency';
import Environment from './pages/Environment';
import FogNodes from './pages/FogNodes';
import Analytics from './pages/Analytics';
import Devices from './pages/Devices';
import AuditLogs from './pages/AuditLogs';
import SystemHealth from './pages/SystemHealth';
import AdminConfig from './pages/AdminConfig';

function App() {
  const { isAuthenticated } = useAuthStore();

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={!isAuthenticated ? <Login /> : <Navigate to="/" />} />
        
        {/* Protected Routes */}
        <Route element={isAuthenticated ? <AppLayout /> : <Navigate to="/login" />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/traffic" element={<Traffic />} />
          <Route path="/emergency" element={<Emergency />} />
          <Route path="/environment" element={<Environment />} />
          <Route path="/nodes" element={<FogNodes />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/devices" element={<Devices />} />
          <Route path="/audit" element={<AuditLogs />} />
          <Route path="/health" element={<SystemHealth />} />
          <Route path="/admin" element={<AdminConfig />} />
        </Route>

        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
