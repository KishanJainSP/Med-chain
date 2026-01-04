import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Building2, Wallet, Loader2, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useWeb3 } from '@/context/Web3Context';
import { useAuth } from '@/context/AuthContext';
import { createInstitution } from '@/lib/api';
import { toast } from 'sonner';

export default function InstitutionRegister() {
  const navigate = useNavigate();
  const { connectWallet, account, isConnecting } = useWeb3();
  const { setAuth } = useAuth();
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    name: '',
    license_number: '',
    address: '',
    phone: '',
    email: '',
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
      const result = await createInstitution({
        ...form,
        wallet_address: account,
      });
      
      setAuth({
        authenticated: true,
        userType: 'institution',
        wallet: account,
        userId: result.id,
        userData: { ...form, id: result.id, wallet_address: account },
      });
      
      toast.success('Institution registered successfully!');
      navigate('/dashboard/institution');
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
            <div className="w-16 h-16 mx-auto rounded-2xl bg-[#00d4aa]/20 flex items-center justify-center mb-4">
              <Building2 className="w-8 h-8 text-[#00d4aa]" />
            </div>
            <CardTitle className="text-2xl text-white">Register Institution</CardTitle>
            <CardDescription className="text-[#94a3b8]">
              Register your hospital or clinic on the blockchain
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Wallet Connection */}
              <div className="p-4 bg-[#111827] rounded-xl mb-6">
                {account ? (
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-[#00d4aa]/20 flex items-center justify-center">
                      <Wallet className="w-5 h-5 text-[#00d4aa]" />
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
                <Label className="text-[#94a3b8]">Institution Name</Label>
                <Input 
                  name="name" 
                  value={form.name} 
                  onChange={handleChange}
                  placeholder="City General Hospital"
                  className="bg-[#111827] border-[#2d3748] text-white"
                  required
                  data-testid="institution-name-input"
                />
              </div>

              <div className="space-y-2">
                <Label className="text-[#94a3b8]">License Number</Label>
                <Input 
                  name="license_number" 
                  value={form.license_number} 
                  onChange={handleChange}
                  placeholder="MED-2024-XXXXX"
                  className="bg-[#111827] border-[#2d3748] text-white"
                  required
                  data-testid="license-input"
                />
              </div>

              <div className="space-y-2">
                <Label className="text-[#94a3b8]">Address</Label>
                <Input 
                  name="address" 
                  value={form.address} 
                  onChange={handleChange}
                  placeholder="123 Medical Drive, City, State"
                  className="bg-[#111827] border-[#2d3748] text-white"
                  required
                  data-testid="address-input"
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
                    placeholder="admin@hospital.com"
                    className="bg-[#111827] border-[#2d3748] text-white"
                    required
                    data-testid="email-input"
                  />
                </div>
              </div>

              <Button 
                type="submit" 
                disabled={loading || !account}
                className="w-full bg-gradient-to-r from-[#00d4aa] to-[#0ea5e9] text-[#0a0e17] mt-6"
                data-testid="register-submit-btn"
              >
                {loading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
                Register Institution
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
