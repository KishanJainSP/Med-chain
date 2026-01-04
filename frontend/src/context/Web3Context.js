import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { ethers } from 'ethers';

const Web3Context = createContext(undefined);

export const useWeb3 = () => {
  const context = useContext(Web3Context);
  if (!context) {
    throw new Error('useWeb3 must be used within Web3Provider');
  }
  return context;
};

// MedicalRecordRegistry ABI
const RECORD_REGISTRY_ABI = [
  {
    "inputs": [{"internalType": "bytes32", "name": "recordHash", "type": "bytes32"}],
    "name": "anchorRecord",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [{"internalType": "bytes32", "name": "recordHash", "type": "bytes32"}],
    "name": "isAnchored",
    "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "anonymous": false,
    "inputs": [
      {"indexed": true, "internalType": "bytes32", "name": "recordHash", "type": "bytes32"},
      {"indexed": true, "internalType": "address", "name": "submitter", "type": "address"},
      {"indexed": false, "internalType": "uint256", "name": "timestamp", "type": "uint256"}
    ],
    "name": "RecordAnchored",
    "type": "event"
  }
];

// Contract addresses (to be updated with deployed addresses)
const CONTRACTS = {
  recordRegistry: process.env.REACT_APP_RECORD_REGISTRY_ADDRESS || '0x0000000000000000000000000000000000000000'
};

export const Web3Provider = ({ children }) => {
  const [provider, setProvider] = useState(null);
  const [signer, setSigner] = useState(null);
  const [account, setAccount] = useState(null);
  const [chainId, setChainId] = useState(null);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState(null);

  // Get current MetaMask account without prompting
  const getCurrentAccount = useCallback(async () => {
    if (typeof window.ethereum === 'undefined') {
      return null;
    }
    try {
      const accounts = await window.ethereum.request({ method: 'eth_accounts' });
      return accounts.length > 0 ? accounts[0].toLowerCase() : null;
    } catch {
      return null;
    }
  }, []);

  // Force fresh wallet connection - always prompts MetaMask
  const connectWallet = useCallback(async (forceNew = false) => {
    if (typeof window.ethereum === 'undefined') {
      setError('MetaMask is not installed');
      return null;
    }

    setIsConnecting(true);
    setError(null);

    try {
      // Clear previous state if forcing new connection
      if (forceNew) {
        setProvider(null);
        setSigner(null);
        setAccount(null);
      }

      const provider = new ethers.providers.Web3Provider(window.ethereum);
      
      // Request accounts - this will prompt MetaMask if needed
      await provider.send('eth_requestAccounts', []);
      
      // Get the currently selected account in MetaMask
      const accounts = await window.ethereum.request({ method: 'eth_accounts' });
      if (accounts.length === 0) {
        throw new Error('No accounts found');
      }
      
      const currentAddress = accounts[0].toLowerCase();
      const signer = provider.getSigner();
      const network = await provider.getNetwork();

      setProvider(provider);
      setSigner(signer);
      setAccount(currentAddress);
      setChainId(network.chainId);

      return currentAddress;
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setIsConnecting(false);
    }
  }, []);

  // Refresh connection to get current MetaMask account
  const refreshAccount = useCallback(async () => {
    if (typeof window.ethereum === 'undefined') {
      return null;
    }

    try {
      const provider = new ethers.providers.Web3Provider(window.ethereum);
      const accounts = await window.ethereum.request({ method: 'eth_accounts' });
      
      if (accounts.length === 0) {
        disconnectWallet();
        return null;
      }
      
      const currentAddress = accounts[0].toLowerCase();
      const signer = provider.getSigner();
      const network = await provider.getNetwork();

      setProvider(provider);
      setSigner(signer);
      setAccount(currentAddress);
      setChainId(network.chainId);

      return currentAddress;
    } catch (err) {
      console.error('Failed to refresh account:', err);
      return null;
    }
  }, []);

  const disconnectWallet = useCallback(() => {
    setProvider(null);
    setSigner(null);
    setAccount(null);
    setChainId(null);
  }, []);

  const anchorRecord = useCallback(async (fileHash) => {
    if (!signer) {
      throw new Error('Wallet not connected');
    }

    // Convert hex string to bytes32
    const hashBytes = '0x' + fileHash;
    
    // For demo/local testing, we'll simulate the transaction
    // In production, connect to actual contract
    if (CONTRACTS.recordRegistry === '0x0000000000000000000000000000000000000000') {
      // Simulate transaction for demo
      console.log('Simulating record anchor transaction...');
      const txHash = '0x' + Array(64).fill(0).map(() => Math.floor(Math.random() * 16).toString(16)).join('');
      return {
        hash: txHash,
        wait: async () => ({ status: 1, transactionHash: txHash })
      };
    }

    const contract = new ethers.Contract(
      CONTRACTS.recordRegistry,
      RECORD_REGISTRY_ABI,
      signer
    );

    const tx = await contract.anchorRecord(hashBytes);
    return tx;
  }, [signer]);

  const signMessage = useCallback(async (message) => {
    if (!signer) {
      throw new Error('Wallet not connected');
    }
    return await signer.signMessage(message);
  }, [signer]);

  // Listen for account changes
  useEffect(() => {
    if (typeof window.ethereum !== 'undefined') {
      const handleAccountsChanged = (accounts) => {
        if (accounts.length === 0) {
          disconnectWallet();
        } else {
          setAccount(accounts[0].toLowerCase());
        }
      };

      const handleChainChanged = (chainId) => {
        setChainId(parseInt(chainId, 16));
      };

      window.ethereum.on('accountsChanged', handleAccountsChanged);
      window.ethereum.on('chainChanged', handleChainChanged);

      return () => {
        window.ethereum.removeListener('accountsChanged', handleAccountsChanged);
        window.ethereum.removeListener('chainChanged', handleChainChanged);
      };
    }
  }, [disconnectWallet]);

  // Don't auto-connect - let user explicitly connect
  // This prevents using stale/cached wallet address

  return (
    <Web3Context.Provider
      value={{
        provider,
        signer,
        account,
        chainId,
        isConnecting,
        error,
        connectWallet,
        disconnectWallet,
        refreshAccount,
        getCurrentAccount,
        anchorRecord,
        signMessage,
        isConnected: !!account,
      }}
    >
      {children}
    </Web3Context.Provider>
  );
};
