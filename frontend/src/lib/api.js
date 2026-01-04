import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const api = axios.create({
  baseURL: API,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Institution APIs
export const createInstitution = async (data) => {
  const response = await api.post('/institutions', data);
  return response.data;
};

export const getInstitutions = async () => {
  const response = await api.get('/institutions');
  return response.data;
};

export const getInstitution = async (id) => {
  const response = await api.get(`/institutions/${id}`);
  return response.data;
};

export const getInstitutionByWallet = async (wallet) => {
  const response = await api.get(`/institutions/wallet/${wallet}`);
  return response.data;
};

// Doctor APIs
export const createDoctor = async (data) => {
  const response = await api.post('/doctors', data);
  return response.data;
};

export const getDoctors = async (institutionId) => {
  const params = institutionId ? { institution_id: institutionId } : {};
  const response = await api.get('/doctors', { params });
  return response.data;
};

export const getDoctor = async (id) => {
  const response = await api.get(`/doctors/${id}`);
  return response.data;
};

export const getDoctorByWallet = async (wallet) => {
  const response = await api.get(`/doctors/wallet/${wallet}`);
  return response.data;
};

// Patient APIs
export const createPatient = async (data) => {
  const response = await api.post('/patients', data);
  return response.data;
};

export const getPatients = async () => {
  const response = await api.get('/patients');
  return response.data;
};

export const getPatient = async (id) => {
  const response = await api.get(`/patients/${id}`);
  return response.data;
};

export const getPatientByWallet = async (wallet) => {
  const response = await api.get(`/patients/wallet/${wallet}`);
  return response.data;
};

// Record APIs
export const uploadRecord = async (formData) => {
  const response = await api.post('/records', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getRecords = async (patientId, uploaderId) => {
  const params = {};
  if (patientId) params.patient_id = patientId;
  if (uploaderId) params.uploader_id = uploaderId;
  const response = await api.get('/records', { params });
  return response.data;
};

export const getRecord = async (id) => {
  const response = await api.get(`/records/${id}`);
  return response.data;
};

export const getRecordContent = async (id, requesterId) => {
  const response = await api.get(`/records/${id}/content`, {
    params: { requester_id: requesterId },
  });
  return response.data;
};

export const analyzeRecord = async (id, requesterId) => {
  const response = await api.post(`/records/${id}/analyze`, null, {
    params: { requester_id: requesterId },
  });
  return response.data;
};

export const getRecordAnalysis = async (id, requesterId) => {
  const response = await api.get(`/records/${id}/analysis`, {
    params: { requester_id: requesterId },
  });
  return response.data;
};

export const confirmRecord = async (id, blockchainTx) => {
  const response = await api.put(`/records/${id}/confirm`, null, {
    params: { blockchain_tx: blockchainTx },
  });
  return response.data;
};

// Consent APIs
export const createConsent = async (data) => {
  const response = await api.post('/consents', data);
  return response.data;
};

export const getConsents = async (patientId, doctorId) => {
  const params = {};
  if (patientId) params.patient_id = patientId;
  if (doctorId) params.doctor_id = doctorId;
  const response = await api.get('/consents', { params });
  return response.data;
};

export const revokeConsent = async (id) => {
  const response = await api.put(`/consents/${id}/revoke`);
  return response.data;
};

// Chat APIs
export const sendChatMessage = async (data) => {
  const response = await api.post('/chat', data);
  return response.data;
};

export const getChatHistory = async (userId, sessionId = null, limit = 50) => {
  const params = { user_id: userId, limit };
  if (sessionId) params.session_id = sessionId;
  const response = await api.get('/chat/history', { params });
  return response.data;
};

// Chat Session APIs
export const createChatSession = async (userId, title = 'New Chat') => {
  const response = await api.post('/chat/sessions', null, {
    params: { user_id: userId, title },
  });
  return response.data;
};

export const getChatSessions = async (userId) => {
  const response = await api.get('/chat/sessions', {
    params: { user_id: userId },
  });
  return response.data;
};

export const getChatSession = async (sessionId, userId) => {
  const response = await api.get(`/chat/sessions/${sessionId}`, {
    params: { user_id: userId },
  });
  return response.data;
};

export const updateChatSession = async (sessionId, userId, title) => {
  const response = await api.put(`/chat/sessions/${sessionId}`, null, {
    params: { user_id: userId, title },
  });
  return response.data;
};

export const deleteChatSession = async (sessionId, userId) => {
  const response = await api.delete(`/chat/sessions/${sessionId}`, {
    params: { user_id: userId },
  });
  return response.data;
};

export const clearChatSession = async (sessionId, userId) => {
  const response = await api.delete(`/chat/sessions/${sessionId}/messages`, {
    params: { user_id: userId },
  });
  return response.data;
};

export const getSessionMessages = async (sessionId, userId, limit = 50) => {
  const response = await api.get(`/chat/sessions/${sessionId}/messages`, {
    params: { user_id: userId, limit },
  });
  return response.data;
};

// User lookup
export const getUserByWallet = async (wallet) => {
  const response = await api.get(`/users/wallet/${wallet}`);
  return response.data;
};

// Health check
export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;
