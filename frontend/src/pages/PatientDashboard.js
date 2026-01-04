import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Users, FileText, LogOut, Plus, Shield, Upload, MessageSquare, UserPlus, Check, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useAuth } from '@/context/AuthContext';
import { useWeb3 } from '@/context/Web3Context';
import { getRecords, getDoctors, getConsents, createConsent, revokeConsent } from '@/lib/api';
import { toast } from 'sonner';
import ChatSidebar from '@/components/ChatSidebar';
import UploadRecordModal from '@/components/UploadRecordModal';
import RecordsList from '@/components/RecordsList';

export default function PatientDashboard() {
  const navigate = useNavigate();
  const { state, logout } = useAuth();
  const { account, disconnectWallet } = useWeb3();
  const [records, setRecords] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [consents, setConsents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [chatOpen, setChatOpen] = useState(false);
  const [uploadOpen, setUploadOpen] = useState(false);

  useEffect(() => {
    if (!state.authenticated || state.userType !== 'patient') {
      navigate('/login');
      return;
    }
    loadData();
  }, [state]);

  const loadData = async () => {
    try {
      const [recordsData, doctorsData, consentsData] = await Promise.all([
        getRecords(state.userId),
        getDoctors(),
        getConsents(state.userId)
      ]);
      setRecords(recordsData);
      setDoctors(doctorsData);
      setConsents(consentsData);
    } catch (err) {
      toast.error('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    disconnectWallet();
    logout();
    navigate('/');
  };

  const handleGrantConsent = async (doctorId) => {
    try {
      await createConsent({
        patient_id: state.userId,
        doctor_id: doctorId,
      });
      toast.success('Access granted to doctor');
      loadData();
    } catch (err) {
      toast.error('Failed to grant access');
    }
  };

  const handleRevokeConsent = async (consentId) => {
    try {
      await revokeConsent(consentId);
      toast.success('Access revoked');
      loadData();
    } catch (err) {
      toast.error('Failed to revoke access');
    }
  };

  const getConsentForDoctor = (doctorId) => {
    return consents.find(c => c.doctor_id === doctorId && c.active);
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
            <Button 
              onClick={() => setChatOpen(true)}
              className="bg-gradient-to-r from-[#00d4aa] to-[#0ea5e9] text-[#0a0e17]"
              data-testid="open-chat-btn"
            >
              <MessageSquare className="w-4 h-4 mr-2" /> AI Assistant
            </Button>
            <div className="text-right">
              <p className="text-[#94a3b8] text-xs">Patient</p>
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
        {/* Profile Summary */}
        <div className="glass-card p-6 mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-2xl bg-[#8b5cf6]/20 flex items-center justify-center">
                <Users className="w-8 h-8 text-[#8b5cf6]" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white">{state.userData?.name}</h2>
                <p className="text-[#94a3b8]">
                  Blood Group: {state.userData?.blood_group} • 
                  Gender: {state.userData?.gender} • 
                  DOB: {state.userData?.date_of_birth}
                </p>
              </div>
            </div>
            <Button 
              onClick={() => setUploadOpen(true)}
              className="bg-gradient-to-r from-[#00d4aa] to-[#0ea5e9] text-[#0a0e17]"
              data-testid="upload-record-btn"
            >
              <Upload className="w-4 h-4 mr-2" /> Upload Record
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <Card className="bg-[#1a1f2e] border-[#2d3748]">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm text-[#94a3b8]">Medical Records</CardTitle>
              <FileText className="w-5 h-5 text-[#0ea5e9]" />
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold text-white">{records.length}</p>
            </CardContent>
          </Card>
          <Card className="bg-[#1a1f2e] border-[#2d3748]">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm text-[#94a3b8]">On Blockchain</CardTitle>
              <Shield className="w-5 h-5 text-[#00d4aa]" />
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold text-white">{records.filter(r => r.is_confirmed).length}</p>
            </CardContent>
          </Card>
          <Card className="bg-[#1a1f2e] border-[#2d3748]">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm text-[#94a3b8]">Authorized Doctors</CardTitle>
              <UserPlus className="w-5 h-5 text-[#8b5cf6]" />
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold text-white">{consents.filter(c => c.active).length}</p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content Tabs */}
        <Tabs defaultValue="records" className="space-y-6">
          <TabsList className="bg-[#111827] border border-[#2d3748]">
            <TabsTrigger value="records" className="data-[state=active]:bg-[#00d4aa] data-[state=active]:text-[#0a0e17]">
              <FileText className="w-4 h-4 mr-2" /> Medical Records
            </TabsTrigger>
            <TabsTrigger value="doctors" className="data-[state=active]:bg-[#00d4aa] data-[state=active]:text-[#0a0e17]">
              <UserPlus className="w-4 h-4 mr-2" /> Doctor Access
            </TabsTrigger>
          </TabsList>

          {/* Records Tab */}
          <TabsContent value="records">
            <Card className="bg-[#1a1f2e] border-[#2d3748]">
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle className="text-white">My Medical Records</CardTitle>
                <Button 
                  onClick={() => setUploadOpen(true)}
                  size="sm"
                  className="bg-gradient-to-r from-[#00d4aa] to-[#0ea5e9] text-[#0a0e17]"
                >
                  <Plus className="w-4 h-4 mr-1" /> Upload
                </Button>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <p className="text-[#94a3b8] text-center py-8">Loading...</p>
                ) : (
                  <RecordsList 
                    records={records} 
                    userId={state.userId} 
                    userRole="patient"
                    onRefresh={loadData}
                  />
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Doctor Access Tab */}
          <TabsContent value="doctors">
            <Card className="bg-[#1a1f2e] border-[#2d3748]">
              <CardHeader>
                <CardTitle className="text-white">Manage Doctor Access</CardTitle>
              </CardHeader>
              <CardContent>
                {doctors.length === 0 ? (
                  <div className="text-center py-12">
                    <UserPlus className="w-12 h-12 mx-auto text-[#2d3748] mb-4" />
                    <p className="text-[#94a3b8]">No doctors registered in the system</p>
                  </div>
              ) : (
                <div className="space-y-3">
                  {doctors.map((doctor) => {
                    const consent = getConsentForDoctor(doctor.id);
                    return (
                      <div 
                        key={doctor.id}
                        className="p-4 bg-[#111827] rounded-xl flex items-center justify-between"
                      >
                        <div>
                          <p className="text-white font-medium">{doctor.name}</p>
                          <p className="text-[#94a3b8] text-sm">{doctor.specialization}</p>
                        </div>
                        {consent ? (
                          <Button 
                            size="sm"
                            variant="outline"
                            onClick={() => handleRevokeConsent(consent.id)}
                            className="border-red-500/50 text-red-400 hover:bg-red-500/10"
                            data-testid={`revoke-${doctor.id}`}
                          >
                            <X className="w-4 h-4 mr-1" /> Revoke
                          </Button>
                        ) : (
                          <Button 
                            size="sm"
                            onClick={() => handleGrantConsent(doctor.id)}
                            className="bg-[#00d4aa]/20 text-[#00d4aa] hover:bg-[#00d4aa]/30"
                            data-testid={`grant-${doctor.id}`}
                          >
                            <Check className="w-4 h-4 mr-1" /> Grant Access
                          </Button>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>

      {/* Chat Sidebar */}
      <ChatSidebar 
        isOpen={chatOpen} 
        onClose={() => setChatOpen(false)} 
        userId={state.userId}
        userRole="patient"
        records={records}
      />

      {/* Upload Modal */}
      <UploadRecordModal 
        isOpen={uploadOpen}
        onClose={() => setUploadOpen(false)}
        patient={{ id: state.userId, name: state.userData?.name }}
        uploaderId={state.userId}
        uploaderRole="patient"
        onSuccess={loadData}
      />
    </div>
  );
}
