import { useState } from 'react';
import { X, Upload, Loader2, FileText, Image, AlertCircle, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { uploadRecord, confirmRecord } from '@/lib/api';
import { useWeb3 } from '@/context/Web3Context';
import { toast } from 'sonner';

export default function UploadRecordModal({ isOpen, onClose, patient, uploaderId, uploaderRole, onSuccess }) {
  const { anchorRecord, isConnected } = useWeb3();
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState('upload'); // 'upload', 'confirm', 'done'
  const [file, setFile] = useState(null);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [uploadResult, setUploadResult] = useState(null);
  const [txHash, setTxHash] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      if (!title) {
        setTitle(selectedFile.name.split('.')[0]);
      }
    }
  };

  const handleUpload = async () => {
    if (!file || !title) {
      toast.error('Please select a file and enter a title');
      return;
    }

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('patient_id', patient.id);
      formData.append('uploader_id', uploaderId);
      formData.append('uploader_role', uploaderRole);
      formData.append('title', title);
      formData.append('description', description);

      const result = await uploadRecord(formData);
      setUploadResult(result);
      setStep('confirm');
      toast.success('File uploaded to IPFS!');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  const handleBlockchainConfirm = async () => {
    if (!uploadResult?.file_hash) return;

    setLoading(true);
    try {
      // Anchor on blockchain
      const tx = await anchorRecord(uploadResult.file_hash);
      toast.info('Transaction submitted. Waiting for confirmation...');
      
      const receipt = await tx.wait();
      setTxHash(receipt.transactionHash);

      // Update record with tx hash
      await confirmRecord(uploadResult.id, receipt.transactionHash);
      
      setStep('done');
      toast.success('Record anchored on blockchain!');
    } catch (err) {
      console.error('Blockchain error:', err);
      toast.error('Blockchain transaction failed. Record saved without anchoring.');
      setStep('done');
    } finally {
      setLoading(false);
    }
  };

  const handleSkipBlockchain = () => {
    setStep('done');
    toast.info('Record saved without blockchain anchoring');
  };

  const handleClose = () => {
    setFile(null);
    setTitle('');
    setDescription('');
    setUploadResult(null);
    setTxHash(null);
    setStep('upload');
    onClose();
    if (step === 'done') {
      onSuccess?.();
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="bg-[#1a1f2e] border-[#2d3748] text-white max-w-md">
        <DialogHeader>
          <DialogTitle className="text-white flex items-center gap-2">
            <Upload className="w-5 h-5 text-[#00d4aa]" />
            Upload Medical Record
          </DialogTitle>
        </DialogHeader>

        {step === 'upload' && (
          <div className="space-y-4">
            <div className="p-3 bg-[#111827] rounded-lg">
              <p className="text-[#94a3b8] text-sm">Patient: <span className="text-white">{patient?.name}</span></p>
            </div>

            {/* File Drop Zone */}
            <div 
              className="file-drop-zone"
              onClick={() => document.getElementById('file-input').click()}
            >
              <input 
                id="file-input"
                type="file" 
                onChange={handleFileChange}
                accept=".pdf,.png,.jpg,.jpeg,.dcm"
                className="hidden"
                data-testid="file-input"
              />
              {file ? (
                <div className="flex items-center gap-3">
                  {file.type.includes('image') ? (
                    <Image className="w-10 h-10 text-[#0ea5e9]" />
                  ) : (
                    <FileText className="w-10 h-10 text-[#0ea5e9]" />
                  )}
                  <div className="text-left">
                    <p className="text-white font-medium">{file.name}</p>
                    <p className="text-[#94a3b8] text-sm">{(file.size / 1024).toFixed(1)} KB</p>
                  </div>
                </div>
              ) : (
                <>
                  <Upload className="w-10 h-10 mx-auto text-[#94a3b8] mb-2" />
                  <p className="text-[#94a3b8]">Click to select file</p>
                  <p className="text-[#94a3b8] text-xs mt-1">PDF, Images, DICOM</p>
                </>
              )}
            </div>

            <div className="space-y-2">
              <Label className="text-[#94a3b8]">Title</Label>
              <Input 
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Blood Test Report"
                className="bg-[#111827] border-[#2d3748] text-white"
                data-testid="record-title-input"
              />
            </div>

            <div className="space-y-2">
              <Label className="text-[#94a3b8]">Description (Optional)</Label>
              <Textarea 
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Additional notes about this record..."
                className="bg-[#111827] border-[#2d3748] text-white resize-none"
                rows={3}
                data-testid="record-description-input"
              />
            </div>

            <Button 
              onClick={handleUpload}
              disabled={loading || !file || !title}
              className="w-full bg-gradient-to-r from-[#00d4aa] to-[#0ea5e9] text-[#0a0e17]"
              data-testid="upload-submit-btn"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Upload className="w-4 h-4 mr-2" />}
              Upload to IPFS
            </Button>
          </div>
        )}

        {step === 'confirm' && (
          <div className="space-y-4">
            <Alert className="bg-[#00d4aa]/10 border-[#00d4aa]/50">
              <Check className="h-4 w-4 text-[#00d4aa]" />
              <AlertDescription className="text-[#00d4aa]">
                File uploaded to IPFS successfully!
              </AlertDescription>
            </Alert>

            <div className="p-4 bg-[#111827] rounded-lg space-y-2">
              <p className="text-[#94a3b8] text-sm">IPFS Hash:</p>
              <p className="text-white font-mono text-xs break-all">{uploadResult?.ipfs_hash}</p>
              <p className="text-[#94a3b8] text-sm mt-3">File Hash (SHA256):</p>
              <p className="text-white font-mono text-xs break-all">{uploadResult?.file_hash}</p>
            </div>

            <Alert className="bg-[#f59e0b]/10 border-[#f59e0b]/50">
              <AlertCircle className="h-4 w-4 text-[#f59e0b]" />
              <AlertDescription className="text-[#f59e0b]">
                Anchor this record on blockchain for immutable proof. This will open MetaMask for confirmation.
              </AlertDescription>
            </Alert>

            <div className="flex gap-3">
              <Button 
                variant="outline"
                onClick={handleSkipBlockchain}
                className="flex-1 border-[#2d3748] text-[#94a3b8]"
                disabled={loading}
                data-testid="skip-blockchain-btn"
              >
                Skip
              </Button>
              <Button 
                onClick={handleBlockchainConfirm}
                disabled={loading || !isConnected}
                className="flex-1 bg-gradient-to-r from-[#00d4aa] to-[#0ea5e9] text-[#0a0e17]"
                data-testid="confirm-blockchain-btn"
              >
                {loading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
                Confirm on Chain
              </Button>
            </div>
          </div>
        )}

        {step === 'done' && (
          <div className="space-y-4 text-center py-4">
            <div className="w-16 h-16 mx-auto rounded-full bg-[#00d4aa]/20 flex items-center justify-center">
              <Check className="w-8 h-8 text-[#00d4aa]" />
            </div>
            <h3 className="text-xl font-bold text-white">Record Saved!</h3>
            <p className="text-[#94a3b8]">
              {txHash ? 'Your record is now anchored on the blockchain.' : 'Your record has been saved to IPFS.'}
            </p>
            
            {txHash && (
              <div className="p-3 bg-[#111827] rounded-lg">
                <p className="text-[#94a3b8] text-xs">Transaction Hash:</p>
                <p className="text-white font-mono text-xs break-all">{txHash}</p>
              </div>
            )}

            <Button 
              onClick={handleClose}
              className="w-full bg-gradient-to-r from-[#00d4aa] to-[#0ea5e9] text-[#0a0e17]"
              data-testid="done-btn"
            >
              Done
            </Button>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
