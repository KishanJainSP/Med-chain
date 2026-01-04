import { useState } from 'react';
import { FileText, Image, Download, Sparkles, Loader2, X, CheckCircle, AlertCircle, Eye } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { ScrollArea } from '@/components/ui/scroll-area';
import { analyzeRecord, getRecordContent } from '@/lib/api';
import { toast } from 'sonner';

export default function RecordsList({ records, userId, userRole, onRefresh }) {
  const [analyzing, setAnalyzing] = useState(null);
  const [analysisModal, setAnalysisModal] = useState(null);
  const [viewModal, setViewModal] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async (record) => {
    setAnalyzing(record.id);
    try {
      const result = await analyzeRecord(record.id, userId);
      setAnalysisModal({ record, analysis: result });
      toast.success('Analysis complete!');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Analysis failed');
    } finally {
      setAnalyzing(null);
    }
  };

  const handleView = async (record) => {
    setLoading(true);
    try {
      const content = await getRecordContent(record.id, userId);
      setViewModal({ record, content });
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to load file');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatSize = (bytes) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <>
      <div className="space-y-3">
        {records.length === 0 ? (
          <div className="text-center py-12 bg-[#111827] rounded-xl">
            <FileText className="w-12 h-12 mx-auto text-[#2d3748] mb-4" />
            <p className="text-[#94a3b8]">No medical records found</p>
          </div>
        ) : (
          records.map((record) => (
            <div 
              key={record.id}
              className="p-4 bg-[#111827] rounded-xl border border-[#2d3748] hover:border-[#00d4aa]/50 transition-all"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-start gap-3 flex-1">
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                    record.file_type === 'image' 
                      ? 'bg-[#8b5cf6]/20' 
                      : 'bg-[#0ea5e9]/20'
                  }`}>
                    {record.file_type === 'image' ? (
                      <Image className="w-6 h-6 text-[#8b5cf6]" />
                    ) : (
                      <FileText className="w-6 h-6 text-[#0ea5e9]" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="text-white font-medium truncate">{record.title}</h4>
                    <p className="text-[#94a3b8] text-sm mt-1">
                      {record.file_type.toUpperCase()} • {formatSize(record.size_bytes)}
                    </p>
                    <p className="text-[#94a3b8] text-xs mt-1">
                      Uploaded: {formatDate(record.created_at)}
                    </p>
                    {record.description && (
                      <p className="text-[#94a3b8] text-xs mt-1 truncate">
                        {record.description}
                      </p>
                    )}
                  </div>
                </div>
                
                <div className="flex flex-col gap-2">
                  {/* Status Badge */}
                  <span className={`badge text-xs ${record.is_confirmed ? 'badge-success' : 'badge-warning'}`}>
                    {record.is_confirmed ? (
                      <><CheckCircle className="w-3 h-3" /> On Chain</>
                    ) : (
                      <><AlertCircle className="w-3 h-3" /> Pending</>
                    )}
                  </span>
                  
                  {/* Action Buttons */}
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleView(record)}
                      disabled={loading}
                      className="border-[#2d3748] text-[#94a3b8] hover:text-white"
                      data-testid={`view-${record.id}`}
                    >
                      <Eye className="w-4 h-4" />
                    </Button>
                    <Button
                      size="sm"
                      onClick={() => handleAnalyze(record)}
                      disabled={analyzing === record.id}
                      className="bg-gradient-to-r from-[#00d4aa] to-[#0ea5e9] text-[#0a0e17]"
                      data-testid={`analyze-${record.id}`}
                    >
                      {analyzing === record.id ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <><Sparkles className="w-4 h-4 mr-1" /> Analyze</>
                      )}
                    </Button>
                  </div>
                </div>
              </div>
              
              {/* IPFS Hash */}
              <div className="mt-3 pt-3 border-t border-[#2d3748]">
                <p className="text-[#94a3b8] text-xs font-mono truncate">
                  IPFS: {record.ipfs_hash}
                </p>
                {record.blockchain_tx && (
                  <p className="text-[#00d4aa] text-xs font-mono truncate mt-1">
                    TX: {record.blockchain_tx}
                  </p>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Analysis Modal */}
      <Dialog open={!!analysisModal} onOpenChange={() => setAnalysisModal(null)}>
        <DialogContent className="bg-[#1a1f2e] border-[#2d3748] text-white max-w-2xl max-h-[80vh]">
          <DialogHeader>
            <DialogTitle className="text-white flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-[#00d4aa]" />
              AI Analysis: {analysisModal?.record?.title}
            </DialogTitle>
          </DialogHeader>
          
          <ScrollArea className="max-h-[60vh]">
            {analysisModal?.analysis && (
              <div className="space-y-4 pr-4">
                {/* Summary */}
                <div className="p-4 bg-[#111827] rounded-xl">
                  <h4 className="text-[#00d4aa] font-semibold mb-2">Summary</h4>
                  <div className="text-[#94a3b8] text-sm whitespace-pre-wrap">
                    {analysisModal.analysis.summary}
                  </div>
                </div>
                
                {/* Key Findings */}
                {analysisModal.analysis.key_findings?.length > 0 && (
                  <div className="p-4 bg-[#111827] rounded-xl">
                    <h4 className="text-[#0ea5e9] font-semibold mb-2">Key Findings</h4>
                    <ul className="space-y-2">
                      {analysisModal.analysis.key_findings.map((finding, i) => (
                        <li key={i} className="text-[#94a3b8] text-sm flex items-start gap-2">
                          <CheckCircle className="w-4 h-4 text-[#00d4aa] flex-shrink-0 mt-0.5" />
                          {finding}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {/* Recommendations */}
                {analysisModal.analysis.recommendations?.length > 0 && (
                  <div className="p-4 bg-[#111827] rounded-xl">
                    <h4 className="text-[#8b5cf6] font-semibold mb-2">Recommendations</h4>
                    <ul className="space-y-2">
                      {analysisModal.analysis.recommendations.map((rec, i) => (
                        <li key={i} className="text-[#94a3b8] text-sm flex items-start gap-2">
                          <AlertCircle className="w-4 h-4 text-[#f59e0b] flex-shrink-0 mt-0.5" />
                          {rec}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {/* Extracted Text Preview */}
                {analysisModal.analysis.extracted_text && (
                  <div className="p-4 bg-[#111827] rounded-xl">
                    <h4 className="text-white font-semibold mb-2">Extracted Text Preview</h4>
                    <div className="text-[#94a3b8] text-xs font-mono bg-[#0a0e17] p-3 rounded-lg max-h-32 overflow-y-auto whitespace-pre-wrap">
                      {analysisModal.analysis.extracted_text.substring(0, 500)}
                      {analysisModal.analysis.extracted_text.length > 500 && '...'}
                    </div>
                  </div>
                )}
                
                {/* Disclaimer */}
                {analysisModal.analysis.disclaimer && (
                  <div className="p-3 bg-[#f59e0b]/10 border border-[#f59e0b]/30 rounded-xl">
                    <p className="text-[#f59e0b] text-xs">
                      ⚠️ {analysisModal.analysis.disclaimer}
                    </p>
                  </div>
                )}
              </div>
            )}
          </ScrollArea>
          
          <div className="flex justify-end pt-4 border-t border-[#2d3748]">
            <Button 
              onClick={() => setAnalysisModal(null)}
              className="bg-gradient-to-r from-[#00d4aa] to-[#0ea5e9] text-[#0a0e17]"
            >
              Close
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* View File Modal */}
      <Dialog open={!!viewModal} onOpenChange={() => setViewModal(null)}>
        <DialogContent className="bg-[#1a1f2e] border-[#2d3748] text-white max-w-4xl max-h-[90vh]">
          <DialogHeader>
            <DialogTitle className="text-white flex items-center gap-2">
              <Eye className="w-5 h-5 text-[#0ea5e9]" />
              View: {viewModal?.record?.title}
            </DialogTitle>
          </DialogHeader>
          
          <div className="flex-1 overflow-auto bg-[#111827] rounded-xl p-4">
            {viewModal?.content && (
              viewModal.record.file_type === 'image' ? (
                <img 
                  src={`data:${viewModal.content.content_type};base64,${viewModal.content.content}`}
                  alt={viewModal.record.title}
                  className="max-w-full h-auto mx-auto rounded-lg"
                />
              ) : viewModal.record.file_type === 'pdf' ? (
                <div className="text-center">
                  <FileText className="w-16 h-16 mx-auto text-[#0ea5e9] mb-4" />
                  <p className="text-white mb-4">PDF Document</p>
                  <a
                    href={`data:${viewModal.content.content_type};base64,${viewModal.content.content}`}
                    download={viewModal.content.filename || 'document.pdf'}
                    className="inline-flex items-center gap-2 px-4 py-2 bg-[#0ea5e9] text-white rounded-lg hover:bg-[#0ea5e9]/80"
                  >
                    <Download className="w-4 h-4" /> Download PDF
                  </a>
                </div>
              ) : (
                <div className="text-center text-[#94a3b8]">
                  <FileText className="w-16 h-16 mx-auto mb-4" />
                  <p>File preview not available</p>
                </div>
              )
            )}
          </div>
          
          <div className="flex justify-end pt-4 border-t border-[#2d3748]">
            <Button 
              onClick={() => setViewModal(null)}
              variant="outline"
              className="border-[#2d3748] text-[#94a3b8]"
            >
              Close
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}
