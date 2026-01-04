import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Stethoscope, Wallet, Loader2, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useWeb3 } from '@/context/Web3Context';
import { useAuth } from '@/context/AuthContext';
import { createDoctor, getInstitutions } from '@/lib/api';
import { toast } from 'sonner';

export default function DoctorRegister() {
  const navigate = useNavigate();
  const { connectWallet, account, isConnecting } = useWeb3();
  const { setAuth } = useAuth();
  const [loading, setLoading] = useState(false);
  const [institutions, setInstitutions] = useState([]);
  const [form, setForm] = useState({
    institution_id: '',
    name: '',
    specialization: '',
    license_number: '',
    phone: '',
    email: '',
  });

  useEffect(() => {
    loadInstitutions();
  }, []);

  const loadInstitutions = async () => {
    try {
      const data = await getInstitutions();
      setInstitutions(data);
    } catch (err) {
      toast.error('Failed to load institutions');
    }
  };

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!account) {
      toast.error('Please connect your wallet first');
      return;
    }
    if (!form.institution_id) {
      toast.error('Please select an institution');
      return;
    }
    
    setLoading(true);
    try {
      const result = await createDoctor({
        ...form,
        wallet_address: account,
      });
      
      setAuth({
        authenticated: true,
        userType: 'doctor',
        wallet: account,
        userId: result.id,
        userData: { ...form, id: result.id, wallet_address: account },
      });
      
      toast.success('Doctor registered successfully!');
      navigate('/dashboard/doctor');
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
            <div className="w-16 h-16 mx-auto rounded-2xl bg-[#0ea5e9]/20 flex items-center justify-center mb-4">
              <Stethoscope className="w-8 h-8 text-[#0ea5e9]" />
            </div>
            <CardTitle className="text-2xl text-white">Register as Doctor</CardTitle>
            <CardDescription className="text-[#94a3b8]">
              Join a medical institution to manage patient records
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Wallet Connection */}
              <div className="p-4 bg-[#111827] rounded-xl mb-6">
                {account ? (
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-[#0ea5e9]/20 flex items-center justify-center">
                      <Wallet className="w-5 h-5 text-[#0ea5e9]" />
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
                <Label className="text-[#94a3b8]">Select Institution</Label>
                <Select 
                  value={form.institution_id} 
                  onValueChange={(value) => setForm({ ...form, institution_id: value })}
                >
                  <SelectTrigger className="bg-[#111827] border-[#2d3748] text-white" data-testid="institution-select">
                    <SelectValue placeholder="Choose your institution" />
                  </SelectTrigger>
                  <SelectContent className="bg-[#1a1f2e] border-[#2d3748]">
                    {institutions.map((inst) => (
                      <SelectItem key={inst.id} value={inst.id} className="text-white hover:bg-[#2d3748]">
                        {inst.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {institutions.length === 0 && (
                  <p className="text-xs text-[#f59e0b]">No institutions registered yet. Please ask an institution to register first.</p>
                )}
              </div>

              <div className="space-y-2">
                <Label className="text-[#94a3b8]">Full Name</Label>
                <Input 
                  name="name" 
                  value={form.name} 
                  onChange={handleChange}
                  placeholder="Dr. John Smith"
                  className="bg-[#111827] border-[#2d3748] text-white"
                  required
                  data-testid="doctor-name-input"
                />
              </div>

              <div className="space-y-2">
                <Label className="text-[#94a3b8]">Specialization</Label>
                <Input 
                  name="specialization" 
                  value={form.specialization} 
                  onChange={handleChange}
                  placeholder="Cardiology, General Medicine, etc."
                  className="bg-[#111827] border-[#2d3748] text-white"
                  required
                  data-testid="specialization-input"
                />
              </div>

              <div className="space-y-2">
                <Label className="text-[#94a3b8]">Medical License Number</Label>
                <Input 
                  name="license_number" 
                  value={form.license_number} 
                  onChange={handleChange}
                  placeholder="MD-2024-XXXXX"
                  className="bg-[#111827] border-[#2d3748] text-white"
                  required
                  data-testid="license-input"
                />
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
                    placeholder="doctor@hospital.com"
                    className="bg-[#111827] border-[#2d3748] text-white"
                    required
                    data-testid="email-input"
                  />
                </div>
              </div>

              <Button 
                type="submit" 
                disabled={loading || !account || !form.institution_id}
                className="w-full bg-gradient-to-r from-[#00d4aa] to-[#0ea5e9] text-[#0a0e17] mt-6"
                data-testid="register-submit-btn"
              >
                {loading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
                Register as Doctor
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
