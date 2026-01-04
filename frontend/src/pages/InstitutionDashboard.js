import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Building2, Users, Stethoscope, LogOut, Plus, Shield } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useAuth } from '@/context/AuthContext';
import { useWeb3 } from '@/context/Web3Context';
import { getDoctors } from '@/lib/api';
import { toast } from 'sonner';

export default function InstitutionDashboard() {
  const navigate = useNavigate();
  const { state, logout } = useAuth();
  const { account, disconnectWallet } = useWeb3();
  const [doctors, setDoctors] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!state.authenticated || state.userType !== 'institution') {
      navigate('/login');
      return;
    }
    loadDoctors();
  }, [state]);

  const loadDoctors = async () => {
    try {
      const data = await getDoctors(state.userId);
      setDoctors(data);
    } catch (err) {
      toast.error('Failed to load doctors');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    disconnectWallet();
    logout();
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-[#0a0e17]">
      {/* Header */}
      <header className="border-b border-[#2d3748] px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#00d4aa] to-[#0ea5e9] flex items-center justify-center">
              <Shield className="w-6 h-6 text-[#0a0e17]" />
            </div>
            <span className="text-xl font-bold text-white">MedChain</span>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="text-[#94a3b8] text-xs">Institution</p>
              <p className="text-white font-medium">{state.userData?.name}</p>
            </div>
            <Button 
              onClick={handleLogout}
              variant="outline"
              className="border-[#2d3748] text-[#94a3b8] hover:text-white"
              data-testid="logout-btn"
            >
              <LogOut className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Stats */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <Card className="bg-[#1a1f2e] border-[#2d3748]">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm text-[#94a3b8]">Total Doctors</CardTitle>
              <Stethoscope className="w-5 h-5 text-[#0ea5e9]" />
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold text-white">{doctors.length}</p>
            </CardContent>
          </Card>
          <Card className="bg-[#1a1f2e] border-[#2d3748]">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm text-[#94a3b8]">Verified Doctors</CardTitle>
              <Shield className="w-5 h-5 text-[#00d4aa]" />
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold text-white">{doctors.filter(d => d.is_verified).length}</p>
            </CardContent>
          </Card>
          <Card className="bg-[#1a1f2e] border-[#2d3748]">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm text-[#94a3b8]">Wallet</CardTitle>
              <Building2 className="w-5 h-5 text-[#8b5cf6]" />
            </CardHeader>
            <CardContent>
              <p className="text-sm font-mono text-white">
                {account?.slice(0, 8)}...{account?.slice(-6)}
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Doctors List */}
        <Card className="bg-[#1a1f2e] border-[#2d3748]">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-white">Registered Doctors</CardTitle>
            <Button 
              className="bg-gradient-to-r from-[#00d4aa] to-[#0ea5e9] text-[#0a0e17]"
              onClick={() => navigate('/register/doctor')}
              data-testid="add-doctor-btn"
            >
              <Plus className="w-4 h-4 mr-2" /> Add Doctor
            </Button>
          </CardHeader>
          <CardContent>
            {loading ? (
              <p className="text-[#94a3b8] text-center py-8">Loading...</p>
            ) : doctors.length === 0 ? (
              <div className="text-center py-12">
                <Stethoscope className="w-12 h-12 mx-auto text-[#2d3748] mb-4" />
                <p className="text-[#94a3b8]">No doctors registered yet</p>
                <p className="text-[#94a3b8] text-sm">Share the registration link with doctors to join</p>
              </div>
            ) : (
              <div className="space-y-4">
                {doctors.map((doctor) => (
                  <div 
                    key={doctor.id}
                    className="p-4 bg-[#111827] rounded-xl flex items-center justify-between"
                  >
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 rounded-full bg-[#0ea5e9]/20 flex items-center justify-center">
                        <Stethoscope className="w-6 h-6 text-[#0ea5e9]" />
                      </div>
                      <div>
                        <p className="text-white font-medium">{doctor.name}</p>
                        <p className="text-[#94a3b8] text-sm">{doctor.specialization}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-[#94a3b8] text-xs">License: {doctor.license_number}</p>
                      <span className={`badge ${doctor.is_verified ? 'badge-success' : 'badge-warning'}`}>
                        {doctor.is_verified ? 'Verified' : 'Pending'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
