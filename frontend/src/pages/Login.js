import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Wallet, Loader2, AlertCircle, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useWeb3 } from '@/context/Web3Context';
import { useAuth } from '@/context/AuthContext';
import { getUserByWallet } from '@/lib/api';

export default function Login() {
  const navigate = useNavigate();
  const { connectWallet, account, isConnecting, error: web3Error, getCurrentAccount, refreshAccount } = useWeb3();
  const { setAuth, state } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [metamaskAccount, setMetamaskAccount] = useState(null);

  // Check current MetaMask account on page load
  useEffect(() => {
    checkMetaMaskAccount();
  }, []);

  // When account changes, verify it matches MetaMask
  useEffect(() => {
    if (account && metamaskAccount && account !== metamaskAccount) {
      // Account mismatch - refresh to get correct account
      refreshAccount();
    }
  }, [account, metamaskAccount]);

  const checkMetaMaskAccount = async () => {
    const currentAccount = await getCurrentAccount();
    setMetamaskAccount(currentAccount);
  };

  const checkUser = async (walletAddress) => {
    const addressToCheck = walletAddress || account;
    if (!addressToCheck) return;
    
    setLoading(true);
    setError('');
    
    try {
      const result = await getUserByWallet(addressToCheck);
      
      // Our API returns: { user_type, user_id, name, email, wallet_address }
      setAuth({
        authenticated: true,
        userType: result.user_type,  // Changed from result.type
        wallet: addressToCheck,
        userId: result.user_id,      // Changed from result.user.id
        userData: result,            // Changed from result.user
      });
      
      navigate(`/dashboard/${result.user_type}`);  // Changed from result.type
    } catch (err) {
      console.error('User check error:', err);
      if (err.response?.status === 404) {
        setError('Wallet not registered. Please register first.');
      } else {
        setError('Failed to check user. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleConnect = async () => {
    setError('');
    // Force fresh connection to MetaMask
    const connectedAddress = await connectWallet(true);
    if (connectedAddress) {
      setMetamaskAccount(connectedAddress);
      // Automatically check user after connecting
      await checkUser(connectedAddress);
    }
  };

  const handleSwitchWallet = async () => {
    setError('');
    // Request wallet_requestPermissions to allow user to select different account
    if (typeof window.ethereum !== 'undefined') {
      try {
        await window.ethereum.request({
          method: 'wallet_requestPermissions',
          params: [{ eth_accounts: {} }],
        });
        // After permission granted, connect again
        const connectedAddress = await connectWallet(true);
        if (connectedAddress) {
          setMetamaskAccount(connectedAddress);
        }
      } catch (err) {
        console.error('Failed to switch wallet:', err);
      }
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0e17] flex items-center justify-center px-4">
      <Card className="w-full max-w-md bg-[#1a1f2e] border-[#2d3748]">
        <CardHeader className="text-center">
          <div className="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-[#00d4aa] to-[#0ea5e9] flex items-center justify-center mb-4">
            <Wallet className="w-8 h-8 text-[#0a0e17]" />
          </div>
          <CardTitle className="text-2xl text-white">Connect Wallet</CardTitle>
          <CardDescription className="text-[#94a3b8]">
            Connect your MetaMask wallet to access your dashboard
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {(error || web3Error) && (
            <Alert variant="destructive" className="bg-red-500/10 border-red-500/50">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error || web3Error}</AlertDescription>
            </Alert>
          )}
          
          {account ? (
            <div className="space-y-4">
              <div className="p-4 bg-[#111827] rounded-xl">
                <p className="text-[#94a3b8] text-sm mb-1">Connected Wallet</p>
                <p className="text-white font-mono text-sm">
                  {account.slice(0, 6)}...{account.slice(-4)}
                </p>
              </div>
              
              {loading ? (
                <div className="flex items-center justify-center gap-2 text-[#94a3b8]">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Checking account...</span>
                </div>
              ) : (
                <div className="space-y-2">
                  <Button 
                    onClick={() => checkUser()}
                    className="w-full bg-gradient-to-r from-[#00d4aa] to-[#0ea5e9] text-[#0a0e17]"
                    data-testid="login-submit-btn"
                  >
                    Continue to Dashboard
                  </Button>
                  <Button 
                    onClick={handleSwitchWallet}
                    variant="outline"
                    className="w-full border-[#2d3748] text-[#94a3b8] hover:text-white"
                    data-testid="switch-wallet-btn"
                  >
                    <RefreshCw className="w-4 h-4 mr-2" /> Switch Wallet
                  </Button>
                </div>
              )}
            </div>
          ) : (
            <Button 
              onClick={handleConnect}
              disabled={isConnecting}
              className="w-full bg-gradient-to-r from-[#00d4aa] to-[#0ea5e9] text-[#0a0e17]"
              data-testid="connect-wallet-btn"
            >
              {isConnecting ? (
                <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Connecting...</>
              ) : (
                <><Wallet className="w-4 h-4 mr-2" /> Connect MetaMask</>
              )}
            </Button>
          )}
          
          <div className="text-center">
            <button 
              onClick={() => navigate('/')}
              className="text-[#94a3b8] text-sm hover:text-[#00d4aa] transition-colors"
            >
              ← Back to Home
            </button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
