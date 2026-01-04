import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Users, Wallet, Loader2, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useWeb3 } from '@/context/Web3Context';
import { useAuth } from '@/context/AuthContext';
import { createPatient } from '@/lib/api';
import { toast } from 'sonner';

export default function PatientRegister() {
  const navigate = useNavigate();
  const { connectWallet, account, isConnecting } = useWeb3();
  const { setAuth } = useAuth();
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    name: '',
    date_of_birth: '',
    gender: '',
    blood_group: '',
    phone: '',
    email: '',
    emergency_contact: '',
  });

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!account) {
      toast.error('Please connect your wallet first');
      return;
    }
    
    setLoading(true);
    try {
      const result = await createPatient({
        ...form,
        wallet_address: account,
      });
      
      setAuth({
        authenticated: true,
        userType: 'patient',
        wallet: account,
        userId: result.id,
        userData: { ...form, id: result.id, wallet_address: account },
      });
      
      toast.success('Patient registered successfully!');
      navigate('/dashboard/patient');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0e17] py-12 px-4">
      <div className="max-w-xl mx-auto">
        <button 
          onClick={() => navigate('/')}
          className="flex items-center gap-2 text-[#94a3b8] hover:text-white mb-8 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Home
        </button>
        
        <Card className="bg-[#1a1f2e] border-[#2d3748]">
          <CardHeader className="text-center">
            <div className="w-16 h-16 mx-auto rounded-2xl bg-[#8b5cf6]/20 flex items-center justify-center mb-4">
              <Users className="w-8 h-8 text-[#8b5cf6]" />
            </div>
            <CardTitle className="text-2xl text-white">Register as Patient</CardTitle>
            <CardDescription className="text-[#94a3b8]">
              Create your health profile and manage medical records
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Wallet Connection */}
              <div className="p-4 bg-[#111827] rounded-xl mb-6">
                {account ? (
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-[#8b5cf6]/20 flex items-center justify-center">
                      <Wallet className="w-5 h-5 text-[#8b5cf6]" />
                    </div>
                    <div>
                      <p className="text-[#94a3b8] text-xs">Connected Wallet</p>
                      <p className="text-white font-mono text-sm">{account.slice(0, 8)}...{account.slice(-6)}</p>
                    </div>
                  </div>
                ) : (
                  <Button 
                    type="button"
                    onClick={connectWallet}
                    disabled={isConnecting}
                    className="w-full bg-gradient-to-r from-[#00d4aa] to-[#0ea5e9] text-[#0a0e17]"
                    data-testid="connect-wallet-btn"
                  >
                    {isConnecting ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Wallet className="w-4 h-4 mr-2" />}
                    Connect MetaMask
                  </Button>
                )}
              </div>

              <div className="space-y-2">
                <Label className="text-[#94a3b8]">Full Name</Label>
                <Input 
                  name="name" 
                  value={form.name} 
                  onChange={handleChange}
                  placeholder="John Doe"
                  className="bg-[#111827] border-[#2d3748] text-white"
                  required
                  data-testid="patient-name-input"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label className="text-[#94a3b8]">Date of Birth</Label>
                  <Input 
                    name="date_of_birth" 
                    type="date"
                    value={form.date_of_birth} 
                    onChange={handleChange}
                    className="bg-[#111827] border-[#2d3748] text-white"
                    required
                    data-testid="dob-input"
                  />
                </div>
                <div className="space-y-2">
                  <Label className="text-[#94a3b8]">Gender</Label>
                  <Select 
                    value={form.gender} 
                    onValueChange={(value) => setForm({ ...form, gender: value })}
                  >
                    <SelectTrigger className="bg-[#111827] border-[#2d3748] text-white" data-testid="gender-select">
                      <SelectValue placeholder="Select gender" />
                    </SelectTrigger>
                    <SelectContent className="bg-[#1a1f2e] border-[#2d3748]">
                      <SelectItem value="male" className="text-white">Male</SelectItem>
                      <SelectItem value="female" className="text-white">Female</SelectItem>
                      <SelectItem value="other" className="text-white">Other</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label className="text-[#94a3b8]">Blood Group</Label>
                <Select 
                  value={form.blood_group} 
                  onValueChange={(value) => setForm({ ...form, blood_group: value })}
                >
                  <SelectTrigger className="bg-[#111827] border-[#2d3748] text-white" data-testid="blood-group-select">
                    <SelectValue placeholder="Select blood group" />
                  </SelectTrigger>
                  <SelectContent className="bg-[#1a1f2e] border-[#2d3748]">
                    {['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'].map((bg) => (
                      <SelectItem key={bg} value={bg} className="text-white">{bg}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label className="text-[#94a3b8]">Phone</Label>
                  <Input 
                    name="phone" 
                    value={form.phone} 
                    onChange={handleChange}
                    placeholder="+1 234 567 8900"
                    className="bg-[#111827] border-[#2d3748] text-white"
                    required
                    data-testid="phone-input"
                  />
                </div>
                <div className="space-y-2">
                  <Label className="text-[#94a3b8]">Email</Label>
                  <Input 
                    name="email" 
                    type="email"
                    value={form.email} 
                    onChange={handleChange}
                    placeholder="patient@email.com"
                    className="bg-[#111827] border-[#2d3748] text-white"
                    required
                    data-testid="email-input"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label className="text-[#94a3b8]">Emergency Contact</Label>
                <Input 
                  name="emergency_contact" 
                  value={form.emergency_contact} 
                  onChange={handleChange}
                  placeholder="+1 234 567 8901 (Relative/Friend)"
                  className="bg-[#111827] border-[#2d3748] text-white"
                  required
                  data-testid="emergency-input"
                />
              </div>

              <Button 
                type="submit" 
                disabled={loading || !account}
                className="w-full bg-gradient-to-r from-[#00d4aa] to-[#0ea5e9] text-[#0a0e17] mt-6"
                data-testid="register-submit-btn"
              >
                {loading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
                Register as Patient
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
