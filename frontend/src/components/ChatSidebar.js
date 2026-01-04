import { useState, useEffect, useRef } from 'react';
import { X, Send, Paperclip, Bot, User, Loader2, FileText, Image, Plus, MessageSquare, Trash2, Edit2, MoreVertical } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { ScrollArea } from '@/components/ui/scroll-area';
import { 
  sendChatMessage, 
  getChatHistory, 
  createChatSession, 
  getChatSessions, 
  deleteChatSession, 
  clearChatSession,
  updateChatSession 
} from '@/lib/api';
import ReactMarkdown from 'react-markdown';

export default function ChatSidebar({ isOpen, onClose, userId, userRole, records = [] }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedRecords, setSelectedRecords] = useState([]);
  const [showRecordPicker, setShowRecordPicker] = useState(false);
  const [ollamaEnabled, setOllamaEnabled] = useState(false);
  
  // Session management state
  const [sessions, setSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [showSessions, setShowSessions] = useState(false);
  const [editingSessionId, setEditingSessionId] = useState(null);
  const [editingTitle, setEditingTitle] = useState('');
  
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (isOpen && userId) {
      loadSessions();
      checkOllamaStatus();
    }
  }, [isOpen, userId]);

  useEffect(() => {
    if (currentSessionId && userId) {
      loadHistory();
    }
  }, [currentSessionId, userId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const checkOllamaStatus = async () => {
    try {
      const response = await fetch('/api/health');
      const data = await response.json();
      setOllamaEnabled(data.ai_models?.ollama_available || false);
    } catch (err) {
      console.error('Failed to check Ollama status');
    }
  };

  const loadSessions = async () => {
    try {
      const sessionList = await getChatSessions(userId);
      setSessions(sessionList);
      
      // If no current session and sessions exist, select the most recent one
      if (!currentSessionId && sessionList.length > 0) {
        setCurrentSessionId(sessionList[0].id);
      }
    } catch (err) {
      console.error('Failed to load sessions');
    }
  };

  const loadHistory = async () => {
    if (!currentSessionId) return;
    
    try {
      const history = await getChatHistory(userId, currentSessionId, 20);
      setMessages(history.map(h => ([
        { type: 'user', content: h.message },
        { type: 'bot', content: h.response }
      ])).flat());
    } catch (err) {
      console.error('Failed to load chat history');
    }
  };

  const createNewSession = async () => {
    try {
      const newSession = await createChatSession(userId, `Chat ${new Date().toLocaleString()}`);
      await loadSessions();
      setCurrentSessionId(newSession.id);
      setMessages([]);
      setShowSessions(false);
    } catch (err) {
      console.error('Failed to create session');
    }
  };

  const switchSession = (sessionId) => {
    setCurrentSessionId(sessionId);
    setShowSessions(false);
  };

  const deleteSession = async (sessionId, e) => {
    e.stopPropagation();
    if (sessions.length <= 1) return; // Keep at least one session
    
    try {
      await deleteChatSession(sessionId, userId);
      await loadSessions();
      
      // If deleted session was current, switch to first available
      if (sessionId === currentSessionId) {
        const remainingSessions = sessions.filter(s => s.id !== sessionId);
        if (remainingSessions.length > 0) {
          setCurrentSessionId(remainingSessions[0].id);
        }
      }
    } catch (err) {
      console.error('Failed to delete session');
    }
  };

  const clearCurrentSession = async () => {
    if (!currentSessionId) return;
    
    try {
      await clearChatSession(currentSessionId, userId);
      setMessages([]);
    } catch (err) {
      console.error('Failed to clear session');
    }
  };

  const startEditingSession = (session, e) => {
    e.stopPropagation();
    setEditingSessionId(session.id);
    setEditingTitle(session.title);
  };

  const saveSessionTitle = async () => {
    if (!editingSessionId || !editingTitle.trim()) return;
    
    try {
      await updateChatSession(editingSessionId, userId, editingTitle.trim());
      await loadSessions();
      setEditingSessionId(null);
      setEditingTitle('');
    } catch (err) {
      console.error('Failed to update session title');
    }
  };

  const cancelEditingSession = () => {
    setEditingSessionId(null);
    setEditingTitle('');
  };

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { type: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const response = await sendChatMessage({
        message: userMessage,
        attached_record_ids: selectedRecords,
        user_id: userId,
        user_role: userRole,
        session_id: currentSessionId,
      });
      
      setMessages(prev => [...prev, { type: 'bot', content: response.response }]);
      setSelectedRecords([]);
      
      // Update current session ID if a new one was created
      if (response.session_id && response.session_id !== currentSessionId) {
        setCurrentSessionId(response.session_id);
        await loadSessions();
      }
      
      // Update Ollama status if returned
      if (response.ollama_powered !== undefined) {
        setOllamaEnabled(response.ollama_powered);
      }
    } catch (err) {
      setMessages(prev => [...prev, { 
        type: 'bot', 
        content: 'Sorry, I encountered an error. Please try again.' 
      }]);
    } finally {
      setLoading(false);
    }
  };

  const toggleRecord = (recordId) => {
    setSelectedRecords(prev => 
      prev.includes(recordId) 
        ? prev.filter(id => id !== recordId)
        : [...prev, recordId]
    );
  };

  return (
    <div className={`chat-sidebar ${isOpen ? 'open' : ''}`}>
      {/* Header */}
      <div className="p-4 border-b border-[#2d3748] flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#00d4aa] to-[#0ea5e9] flex items-center justify-center">
            <Bot className="w-5 h-5 text-[#0a0e17]" />
          </div>
          <div>
            <h3 className="text-white font-semibold">Medical AI Assistant</h3>
            <p className="text-[#94a3b8] text-xs flex items-center gap-1">
              {ollamaEnabled ? (
                <>
                  <span className="w-2 h-2 rounded-full bg-[#00d4aa] animate-pulse"></span>
                  Powered by Ollama AI
                </>
              ) : (
                'Ask about health conditions'
              )}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={() => setShowSessions(!showSessions)}
            className="text-[#94a3b8] hover:text-white"
            title="Chat Sessions"
          >
            <MessageSquare className="w-4 h-4" />
          </Button>
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={onClose}
            className="text-[#94a3b8] hover:text-white"
            data-testid="close-chat-btn"
          >
            <X className="w-5 h-5" />
          </Button>
        </div>
      </div>

      {/* Sessions Panel */}
      {showSessions && (
        <div className="p-4 border-b border-[#2d3748] bg-[#111827]">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-white font-medium text-sm">Chat Sessions</h4>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={createNewSession}
              className="text-[#00d4aa] hover:text-white h-6 px-2"
            >
              <Plus className="w-3 h-3 mr-1" />
              New
            </Button>
          </div>
          <ScrollArea className="max-h-48">
            <div className="space-y-1">
              {sessions.map((session) => (
                <div
                  key={session.id}
                  className={`flex items-center gap-2 p-2 rounded-lg cursor-pointer transition-colors ${
                    session.id === currentSessionId 
                      ? 'bg-[#00d4aa]/20 border border-[#00d4aa]/30' 
                      : 'hover:bg-[#2d3748]'
                  }`}
                  onClick={() => switchSession(session.id)}
                >
                  {editingSessionId === session.id ? (
                    <div className="flex-1 flex items-center gap-2">
                      <input
                        type="text"
                        value={editingTitle}
                        onChange={(e) => setEditingTitle(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && saveSessionTitle()}
                        onBlur={saveSessionTitle}
                        className="flex-1 bg-[#0a0e17] border border-[#2d3748] rounded px-2 py-1 text-xs text-white"
                        autoFocus
                      />
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={cancelEditingSession}
                        className="h-6 w-6 p-0 text-[#94a3b8]"
                      >
                        <X className="w-3 h-3" />
                      </Button>
                    </div>
                  ) : (
                    <>
                      <div className="flex-1 min-w-0">
                        <p className="text-white text-sm truncate">{session.title}</p>
                        <p className="text-[#94a3b8] text-xs">
                          {session.message_count || 0} messages
                        </p>
                      </div>
                      <div className="flex items-center gap-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => startEditingSession(session, e)}
                          className="h-6 w-6 p-0 text-[#94a3b8] hover:text-white opacity-0 group-hover:opacity-100"
                        >
                          <Edit2 className="w-3 h-3" />
                        </Button>
                        {sessions.length > 1 && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={(e) => deleteSession(session.id, e)}
                            className="h-6 w-6 p-0 text-[#ef4444] hover:text-[#dc2626] opacity-0 group-hover:opacity-100"
                          >
                            <Trash2 className="w-3 h-3" />
                          </Button>
                        )}
                      </div>
                    </>
                  )}
                </div>
              ))}
            </div>
          </ScrollArea>
          {currentSessionId && messages.length > 0 && (
            <div className="mt-3 pt-3 border-t border-[#2d3748]">
              <Button
                variant="outline"
                size="sm"
                onClick={clearCurrentSession}
                className="w-full text-[#ef4444] border-[#ef4444]/30 hover:bg-[#ef4444]/10"
              >
                <Trash2 className="w-3 h-3 mr-2" />
                Clear Current Session
              </Button>
            </div>
          )}
        </div>
      )}

      {/* Messages */}
      <ScrollArea className="flex-1 p-4">
        {messages.length === 0 ? (
          <div className="text-center py-12">
            <Bot className="w-16 h-16 mx-auto text-[#2d3748] mb-4" />
            <p className="text-[#94a3b8]">Start a conversation</p>
            <p className="text-[#94a3b8] text-sm mt-2">
              {ollamaEnabled 
                ? 'Chat with Ollama AI about medical conditions or attach records for analysis'
                : 'Ask about medical conditions or attach records for analysis'
              }
            </p>
            {ollamaEnabled && (
              <div className="mt-4 p-3 bg-[#00d4aa]/10 rounded-lg border border-[#00d4aa]/20">
                <p className="text-[#00d4aa] text-xs font-medium">✨ Ollama AI Active</p>
                <p className="text-[#94a3b8] text-xs mt-1">
                  Get natural language responses powered by local AI
                </p>
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map((msg, i) => (
              <div key={i} className={`message message-${msg.type}`}>
                <div className="flex items-start gap-2">
                  {msg.type === 'bot' && (
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#00d4aa] to-[#0ea5e9] flex items-center justify-center flex-shrink-0">
                      <Bot className="w-4 h-4 text-[#0a0e17]" />
                    </div>
                  )}
                  <div className="message-content">
                    {msg.type === 'bot' ? (
                      <div className="prose prose-invert prose-sm max-w-none">
                        <ReactMarkdown>
                          {msg.content}
                        </ReactMarkdown>
                      </div>
                    ) : (
                      <p>{msg.content}</p>
                    )}
                  </div>
                  {msg.type === 'user' && (
                    <div className="w-8 h-8 rounded-full bg-[#8b5cf6]/20 flex items-center justify-center flex-shrink-0">
                      <User className="w-4 h-4 text-[#8b5cf6]" />
                    </div>
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div className="message message-bot">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#00d4aa] to-[#0ea5e9] flex items-center justify-center">
                    <Bot className="w-4 h-4 text-[#0a0e17]" />
                  </div>
                  <div className="message-content">
                    <Loader2 className="w-5 h-5 animate-spin text-[#00d4aa]" />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </ScrollArea>

      {/* Record Picker */}
      {showRecordPicker && records.length > 0 && (
        <div className="p-4 border-t border-[#2d3748] bg-[#111827]">
          <p className="text-[#94a3b8] text-sm mb-2">Attach records for analysis:</p>
          <div className="space-y-2 max-h-32 overflow-y-auto">
            {records.map((record) => (
              <label key={record.id} className="flex items-center gap-2 cursor-pointer">
                <Checkbox 
                  checked={selectedRecords.includes(record.id)}
                  onCheckedChange={() => toggleRecord(record.id)}
                />
                <span className="text-white text-sm truncate flex-1">{record.title}</span>
                {record.file_type === 'image' ? (
                  <Image className="w-4 h-4 text-[#94a3b8]" />
                ) : (
                  <FileText className="w-4 h-4 text-[#94a3b8]" />
                )}
              </label>
            ))}
          </div>
        </div>
      )}

      {/* Selected Records Indicator */}
      {selectedRecords.length > 0 && (
        <div className="px-4 py-2 bg-[#00d4aa]/10 border-t border-[#2d3748]">
          <p className="text-[#00d4aa] text-xs">
            {selectedRecords.length} record(s) attached for analysis
          </p>
        </div>
      )}

      {/* Input */}
      <div className="p-4 border-t border-[#2d3748]">
        <div className="flex gap-2">
          {records.length > 0 && (
            <Button 
              variant="outline"
              size="icon"
              onClick={() => setShowRecordPicker(!showRecordPicker)}
              className={`border-[#2d3748] ${showRecordPicker ? 'text-[#00d4aa] border-[#00d4aa]' : 'text-[#94a3b8]'}`}
              data-testid="attach-records-btn"
            >
              <Paperclip className="w-4 h-4" />
            </Button>
          )}
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask about health conditions..."
            className="flex-1 bg-[#111827] border border-[#2d3748] rounded-lg px-4 py-2 text-white text-sm focus:outline-none focus:border-[#00d4aa]"
            disabled={loading}
            data-testid="chat-input"
          />
          <Button 
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="bg-gradient-to-r from-[#00d4aa] to-[#0ea5e9] text-[#0a0e17]"
            data-testid="send-message-btn"
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
