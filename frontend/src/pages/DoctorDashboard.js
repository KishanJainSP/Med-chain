import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Stethoscope, Users, FileText, LogOut, Plus, Shield, Upload, MessageSquare } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useAuth } from '@/context/AuthContext';
import { useWeb3 } from '@/context/Web3Context';
import { getPatients, getConsents, getRecords } from '@/lib/api';
import { toast } from 'sonner';
import ChatSidebar from '@/components/ChatSidebar';
import UploadRecordModal from '@/components/UploadRecordModal';
import RecordsList from '@/components/RecordsList';

export default function DoctorDashboard() {
  const navigate = useNavigate();
  const { state, logout } = useAuth();
  const { account, disconnectWallet } = useWeb3();
  const [patients, setPatients] = useState([]);
  const [consents, setConsents] = useState([]);
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [chatOpen, setChatOpen] = useState(false);
  const [uploadOpen, setUploadOpen] = useState(false);
  const [selectedPatient, setSelectedPatient] = useState(null);

  useEffect(() => {
    if (!state.authenticated || state.userType !== 'doctor') {
      navigate('/login');
      return;
    }
    loadData();
  }, [state]);

  const loadData = async () => {
    try {
      const [patientsData, consentsData] = await Promise.all([
        getPatients(),
        getConsents(null, state.userId)
      ]);
      setPatients(patientsData);
      setConsents(consentsData.filter(c => c.active));
      
      // Get records for consented patients
      const patientIds = consentsData.filter(c => c.active).map(c => c.patient_id);
      if (patientIds.length > 0) {
        const allRecords = [];
        for (const pid of patientIds) {
          const recs = await getRecords(pid);
          allRecords.push(...recs);
        }
        setRecords(allRecords);
      }
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

  const consentedPatients = patients.filter(p => 
    consents.some(c => c.patient_id === p.id)
  );

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
              variant="outline"
              className="border-[#2d3748] text-[#00d4aa]"
              data-testid="open-chat-btn"
            >
              <MessageSquare className="w-4 h-4 mr-2" /> AI Assistant
            </Button>
            <div className="text-right">
              <p className="text-[#94a3b8] text-xs">Doctor</p>
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
              <CardTitle className="text-sm text-[#94a3b8]">Authorized Patients</CardTitle>
              <Users className="w-5 h-5 text-[#8b5cf6]" />
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold text-white">{consentedPatients.length}</p>
            </CardContent>
          </Card>
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
              <CardTitle className="text-sm text-[#94a3b8]">Specialization</CardTitle>
              <Stethoscope className="w-5 h-5 text-[#00d4aa]" />
            </CardHeader>
            <CardContent>
              <p className="text-white font-medium">{state.userData?.specialization}</p>
            </CardContent>
          </Card>
        </div>

        {/* Patients with Consent */}
        <Card className="bg-[#1a1f2e] border-[#2d3748] mb-8">
          <CardHeader>
            <CardTitle className="text-white">Patients with Consent</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <p className="text-[#94a3b8] text-center py-8">Loading...</p>
            ) : consentedPatients.length === 0 ? (
              <div className="text-center py-12">
                <Users className="w-12 h-12 mx-auto text-[#2d3748] mb-4" />
                <p className="text-[#94a3b8]">No patients have granted you access yet</p>
              </div>
            ) : (
              <div className="grid md:grid-cols-2 gap-4">
                {consentedPatients.map((patient) => (
                  <div 
                    key={patient.id}
                    className="p-4 bg-[#111827] rounded-xl"
                  >
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-[#8b5cf6]/20 flex items-center justify-center">
                          <Users className="w-5 h-5 text-[#8b5cf6]" />
                        </div>
                        <div>
                          <p className="text-white font-medium">{patient.name}</p>
                          <p className="text-[#94a3b8] text-sm">Blood: {patient.blood_group}</p>
                        </div>
                      </div>
                      <span className="badge badge-success">Active</span>
                    </div>
                    <div className="flex gap-2">
                      <Button 
                        size="sm"
                        variant="outline"
                        className="flex-1 border-[#2d3748] text-[#94a3b8]"
                        onClick={() => {
                          setSelectedPatient(patient);
                          setUploadOpen(true);
                        }}
                        data-testid={`upload-record-${patient.id}`}
                      >
                        <Upload className="w-4 h-4 mr-1" /> Upload
                      </Button>
                      <Button 
                        size="sm"
                        className="flex-1 bg-[#0ea5e9]/20 text-[#0ea5e9]"
                        data-testid={`view-records-${patient.id}`}
                      >
                        <FileText className="w-4 h-4 mr-1" /> Records
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Patient Records with Analyze Feature */}
        <Card className="bg-[#1a1f2e] border-[#2d3748]">
          <CardHeader>
            <CardTitle className="text-white">Patient Records</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <p className="text-[#94a3b8] text-center py-8">Loading...</p>
            ) : (
              <RecordsList 
                records={records} 
                userId={state.userId} 
                userRole="doctor"
                onRefresh={loadData}
              />
            )}
          </CardContent>
        </Card>
      </main>

      {/* Chat Sidebar */}
      <ChatSidebar 
        isOpen={chatOpen} 
        onClose={() => setChatOpen(false)} 
        userId={state.userId}
        userRole="doctor"
        records={records}
      />

      {/* Upload Modal */}
      <UploadRecordModal 
        isOpen={uploadOpen}
        onClose={() => {
          setUploadOpen(false);
          setSelectedPatient(null);
        }}
        patient={selectedPatient}
        uploaderId={state.userId}
        uploaderRole="doctor"
        onSuccess={loadData}
      />
    </div>
  );
}
