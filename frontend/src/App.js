import '@/App.css';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from '@/context/AuthContext';
import { Web3Provider } from '@/context/Web3Context';
import { Toaster } from '@/components/ui/sonner';
import Landing from '@/pages/Landing';
import InstitutionRegister from '@/pages/InstitutionRegister';
import DoctorRegister from '@/pages/DoctorRegister';
import PatientRegister from '@/pages/PatientRegister';
import InstitutionDashboard from '@/pages/InstitutionDashboard';
import DoctorDashboard from '@/pages/DoctorDashboard';
import PatientDashboard from '@/pages/PatientDashboard';
import Login from '@/pages/Login';

function App() {
  return (
    <Web3Provider>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register/institution" element={<InstitutionRegister />} />
            <Route path="/register/doctor" element={<DoctorRegister />} />
            <Route path="/register/patient" element={<PatientRegister />} />
            <Route path="/dashboard/institution" element={<InstitutionDashboard />} />
            <Route path="/dashboard/doctor" element={<DoctorDashboard />} />
            <Route path="/dashboard/patient" element={<PatientDashboard />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
        <Toaster position="top-right" />
      </AuthProvider>
    </Web3Provider>
  );
}

export default App;
