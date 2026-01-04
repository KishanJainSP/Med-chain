import { useNavigate } from 'react-router-dom';
import { Building2, Stethoscope, Users, Shield, Database, Bot } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function Landing() {
  const navigate = useNavigate();

  const features = [
    { icon: Shield, title: 'Blockchain Secured', desc: 'All records anchored on blockchain with MetaMask' },
    { icon: Database, title: 'IPFS Storage', desc: 'Decentralized file storage for medical records' },
    { icon: Bot, title: 'AI Medical Assistant', desc: 'Get instant medical insights from your records' },
  ];

  const roles = [
    { icon: Building2, title: 'Medical Institution', desc: 'Register your hospital or clinic', path: '/register/institution', color: '#00d4aa' },
    { icon: Stethoscope, title: 'Doctor', desc: 'Join under a medical institution', path: '/register/doctor', color: '#0ea5e9' },
    { icon: Users, title: 'Patient', desc: 'Manage your health records', path: '/register/patient', color: '#8b5cf6' },
  ];

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
          <Button 
            onClick={() => navigate('/login')} 
            className="bg-gradient-to-r from-[#00d4aa] to-[#0ea5e9] text-[#0a0e17] hover:opacity-90"
            data-testid="login-btn"
          >
            Connect Wallet
          </Button>
        </div>
      </header>

      {/* Hero */}
      <section className="px-6 py-20">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-5xl md:text-6xl font-bold mb-6">
            <span className="text-white">Secure Medical Records on </span>
            <span className="gradient-text">Blockchain</span>
          </h1>
          <p className="text-[#94a3b8] text-lg md:text-xl max-w-2xl mx-auto mb-12">
            Decentralized healthcare platform with AI-powered medical assistant, IPFS storage, and smart contract verification.
          </p>
          
          {/* Features */}
          <div className="grid md:grid-cols-3 gap-6 mb-16">
            {features.map((f, i) => (
              <div key={i} className="glass-card p-6 animate-fade-in" style={{ animationDelay: `${i * 0.1}s` }}>
                <f.icon className="w-10 h-10 mx-auto mb-4 text-[#00d4aa]" />
                <h3 className="text-white font-semibold mb-2">{f.title}</h3>
                <p className="text-[#94a3b8] text-sm">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Role Selection */}
      <section className="px-6 py-16 bg-[#111827]">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-white mb-4">Get Started</h2>
          <p className="text-[#94a3b8] text-center mb-12">Choose your role to register</p>
          
          <div className="grid md:grid-cols-3 gap-6">
            {roles.map((role, i) => (
              <Card 
                key={i} 
                className="bg-[#1a1f2e] border-[#2d3748] hover:border-[#00d4aa] transition-all cursor-pointer group"
                onClick={() => navigate(role.path)}
                data-testid={`role-${role.title.toLowerCase().replace(' ', '-')}`}
              >
                <CardHeader className="text-center">
                  <div 
                    className="w-16 h-16 mx-auto rounded-2xl flex items-center justify-center mb-4 transition-transform group-hover:scale-110"
                    style={{ background: `${role.color}20` }}
                  >
                    <role.icon className="w-8 h-8" style={{ color: role.color }} />
                  </div>
                  <CardTitle className="text-white">{role.title}</CardTitle>
                  <CardDescription className="text-[#94a3b8]">{role.desc}</CardDescription>
                </CardHeader>
                <CardContent>
                  <Button 
                    className="w-full" 
                    variant="outline"
                    style={{ borderColor: role.color, color: role.color }}
                  >
                    Register
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="px-6 py-8 border-t border-[#2d3748]">
        <div className="max-w-7xl mx-auto text-center text-[#94a3b8] text-sm">
          <p>MedChain - Decentralized Healthcare Platform</p>
        </div>
      </footer>
    </div>
  );
}
