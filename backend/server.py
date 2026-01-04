from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Form
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import hashlib
import base64
import aiofiles
import threading

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="MedChain AI Chatbot")

# Add CORS middleware FIRST (before any routes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://localhost:3002",
        "http://localhost:3003",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "http://127.0.0.1:3003"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"],
    allow_headers=["*"],
    expose_headers=["*"],
)

api_router = APIRouter(prefix="/api")

# File storage
LOCAL_STORAGE_PATH = Path(__file__).parent / 'uploads'
LOCAL_STORAGE_PATH.mkdir(exist_ok=True)

# ============== MODELS ==============
class Institution(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    wallet_address: str
    license_number: str
    address: str
    phone: str
    email: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_verified: bool = False

class Doctor(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    institution_id: str
    name: str
    wallet_address: str
    specialization: str
    license_number: str
    email: str
    phone: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_verified: bool = False

class Patient(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    wallet_address: str
    date_of_birth: str
    gender: str
    blood_group: str
    phone: str
    email: str
    emergency_contact: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MedicalRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: str
    uploader_id: str
    uploader_role: str
    title: str
    description: str
    file_type: str
    content_type: str
    ipfs_hash: Optional[str] = None
    file_hash: str
    size_bytes: int
    blockchain_tx: Optional[str] = None
    is_confirmed: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ChatSession(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    message_count: int = 0

class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str  # Added session_id
    user_id: str
    user_role: str
    message: str
    response: str
    attached_records: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Consent(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: str
    doctor_id: str
    record_id: Optional[str] = None
    active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    revoked_at: Optional[datetime] = None

# Request Models
class InstitutionCreate(BaseModel):
    name: str
    wallet_address: str
    license_number: str
    address: str
    phone: str
    email: str

class DoctorCreate(BaseModel):
    institution_id: str
    name: str
    wallet_address: str
    specialization: str
    license_number: str
    email: str
    phone: str

class PatientCreate(BaseModel):
    name: str
    wallet_address: str
    date_of_birth: str
    gender: str
    blood_group: str
    phone: str
    email: str
    emergency_contact: str

class ChatRequest(BaseModel):
    message: str
    attached_record_ids: List[str] = Field(default_factory=list)
    user_id: str
    user_role: str
    session_id: Optional[str] = None  # Added optional session_id

class ConsentCreate(BaseModel):
    patient_id: str
    doctor_id: str
    record_id: Optional[str] = None

# ============== AI RESPONSE SYSTEM ==============
def generate_medical_response(text: str, context: str = "") -> str:
    """Generate medical response using rule-based system"""
    text_lower = text.lower()
    
    conditions = {
        "diabetes": "**Diabetes Management:**\n- Monitor blood sugar regularly\n- Maintain balanced diet with controlled carbs\n- Regular physical activity\n- Take medications as prescribed\n- Regular check-ups with healthcare provider",
        "hypertension": "**Hypertension (High Blood Pressure):**\n- Regular blood pressure monitoring\n- Low sodium diet\n- Regular exercise\n- Stress management\n- Medication adherence",
        "asthma": "**Asthma Management:**\n- Identify and avoid triggers\n- Use inhalers as prescribed\n- Keep rescue medication accessible\n- Regular check-ups",
        "heart": "**Heart Health:**\n- Regular cardiovascular exercise\n- Heart-healthy diet\n- Maintain healthy weight\n- Avoid smoking\n- Regular screenings",
        "headache": "**Headache Relief:**\n- Stay hydrated\n- Get adequate rest\n- Identify triggers\n- Seek medical attention for severe cases",
        "fever": "**Fever Management:**\n- Rest and hydration\n- Monitor temperature\n- Use fever reducers as directed\n- Seek care if fever exceeds 103°F",
        "pain": "**Pain Management:**\n- Identify pain source\n- Rest affected area\n- Apply ice/heat as appropriate\n- Consult provider for persistent pain",
        "cold": "**Common Cold:**\n- Rest and sleep\n- Stay hydrated\n- Use humidifier\n- Usually resolves in 7-10 days",
        "anxiety": "**Anxiety Management:**\n- Deep breathing exercises\n- Regular physical activity\n- Adequate sleep\n- Professional support if needed",
        "prescription": "**Prescription Information:**\nI can see prescription details in your uploaded records. Always follow your doctor's instructions for medication dosage and timing.",
        "report": "**Medical Report Analysis:**\nI've reviewed your uploaded medical report. For detailed interpretation, please consult with your healthcare provider.",
        "scan": "**Medical Imaging:**\nYour scan has been uploaded. Medical imaging requires professional interpretation by a radiologist or specialist.",
        "xray": "**X-Ray Analysis:**\nX-ray images require specialist interpretation. Please discuss results with your healthcare provider.",
    }
    
    # Check if context from records
    if context:
        return f"**Based on your uploaded records:**\n\nI've analyzed the attached medical records.\n\n{context}\n\n*Please consult your healthcare provider for personalized medical advice.*"
    
    for condition, response in conditions.items():
        if condition in text_lower:
            return f"{response}\n\n*Disclaimer: This is general information. Please consult a healthcare professional for personalized advice.*"
    
    if any(word in text_lower for word in ['symptom', 'feel', 'health', 'medical', 'doctor', 'medicine', 'help']):
        return "I'm here to help with medical information. Please:\n\n1. Describe your symptoms in detail\n2. Mention relevant medical history\n3. Upload medical records for analysis\n\n*Remember: Always consult healthcare professionals for medical decisions.*"
    
    return "**MedChain AI Assistant**\n\nI can help you with:\n- Understanding medical conditions\n- Analyzing uploaded medical records\n- General health information\n\n**To get started:**\n- Ask about a specific condition\n- Upload a medical record\n- Browse your stored records\n\n*Note: This is not a substitute for professional medical advice.*"

async def extract_pdf_text(file_bytes: bytes) -> str:
    """Extract text from PDF"""
    try:
        from PyPDF2 import PdfReader
        import io
        reader = PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in reader.pages[:5]:
            text += page.extract_text() or ""
        return text[:2000]
    except Exception:
        return ""

# ============== FILE STORAGE ==============
async def save_file(file_bytes: bytes, filename: str) -> str:
    """Save file to local storage (simulating IPFS)"""
    file_id = str(uuid.uuid4())
    safe_filename = f"{file_id}_{filename.replace('/', '_')}"
    file_path = LOCAL_STORAGE_PATH / safe_filename
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(file_bytes)
    return f"ipfs://{safe_filename}"

async def retrieve_file(ipfs_hash: str) -> Optional[bytes]:
    """Retrieve file from storage"""
    try:
        filename = ipfs_hash.replace("ipfs://", "")
        file_path = LOCAL_STORAGE_PATH / filename
        if file_path.exists():
            async with aiofiles.open(file_path, 'rb') as f:
                return await f.read()
    except Exception as e:
        logger.error(f"File retrieval error: {e}")
    return None

# ============== API ROUTES ==============

# Institution Routes
@api_router.post("/institutions")
async def create_institution(data: InstitutionCreate):
    data_dict = data.model_dump()
    data_dict['wallet_address'] = data_dict['wallet_address'].lower()
    existing = await db.institutions.find_one({"wallet_address": data_dict['wallet_address']}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=409, detail="Institution already exists")
    
    institution = Institution(**data_dict)
    doc = institution.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.institutions.insert_one(doc)
    return {"id": institution.id, "message": "Institution registered"}

@api_router.get("/institutions")
async def list_institutions():
    institutions = await db.institutions.find({}, {"_id": 0}).to_list(length=None)
    return institutions

@api_router.get("/institutions/{institution_id}")
async def get_institution(institution_id: str):
    inst = await db.institutions.find_one({"id": institution_id}, {"_id": 0})
    if not inst:
        raise HTTPException(status_code=404, detail="Not found")
    return inst

@api_router.get("/institutions/wallet/{wallet}")
async def get_institution_by_wallet(wallet: str):
    inst = await db.institutions.find_one({"wallet_address": wallet.lower()}, {"_id": 0})
    if not inst:
        raise HTTPException(status_code=404, detail="Not found")
    return inst

# Doctor Routes
@api_router.post("/doctors")
async def create_doctor(data: DoctorCreate):
    inst = await db.institutions.find_one({"id": data.institution_id}, {"_id": 0})
    if not inst:
        raise HTTPException(status_code=404, detail="Institution not found")
    
    data_dict = data.model_dump()
    data_dict['wallet_address'] = data_dict['wallet_address'].lower()
    existing = await db.doctors.find_one({"wallet_address": data_dict['wallet_address']}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=409, detail="Doctor already exists")
    
    doctor = Doctor(**data_dict)
    doc = doctor.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.doctors.insert_one(doc)
    return {"id": doctor.id, "message": "Doctor registered"}

@api_router.get("/doctors")
async def list_doctors(institution_id: Optional[str] = None):
    query = {"institution_id": institution_id} if institution_id else {}
    return await db.doctors.find(query, {"_id": 0}).to_list(100)

@api_router.get("/doctors/{doctor_id}")
async def get_doctor(doctor_id: str):
    doc = await db.doctors.find_one({"id": doctor_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    return doc

@api_router.get("/doctors/wallet/{wallet}")
async def get_doctor_by_wallet(wallet: str):
    doc = await db.doctors.find_one({"wallet_address": wallet.lower()}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    return doc

# Patient Routes
@api_router.post("/patients")
async def create_patient(data: PatientCreate):
    data_dict = data.model_dump()
    data_dict['wallet_address'] = data_dict['wallet_address'].lower()
    existing = await db.patients.find_one({"wallet_address": data_dict['wallet_address']}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=409, detail="Patient already exists")
    
    patient = Patient(**data_dict)
    doc = patient.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.patients.insert_one(doc)
    return {"id": patient.id, "message": "Patient registered"}

@api_router.get("/patients")
async def list_patients():
    return await db.patients.find({}, {"_id": 0}).to_list(100)

@api_router.get("/patients/{patient_id}")
async def get_patient(patient_id: str):
    patient = await db.patients.find_one({"id": patient_id}, {"_id": 0})
    if not patient:
        raise HTTPException(status_code=404, detail="Not found")
    return patient

@api_router.get("/patients/wallet/{wallet}")
async def get_patient_by_wallet(wallet: str):
    patient = await db.patients.find_one({"wallet_address": wallet.lower()}, {"_id": 0})
    if not patient:
        raise HTTPException(status_code=404, detail="Not found")
    return patient

# Record Routes
@api_router.post("/records")
async def upload_record(
    patient_id: str = Form(...),
    uploader_id: str = Form(...),
    uploader_role: str = Form(...),
    title: str = Form(...),
    description: str = Form(""),
    file: UploadFile = File(...),
    blockchain_tx: Optional[str] = Form(None)
):
    patient = await db.patients.find_one({"id": patient_id}, {"_id": 0})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    if uploader_role == "doctor":
        consent = await db.consents.find_one({"patient_id": patient_id, "doctor_id": uploader_id, "active": True}, {"_id": 0})
        if not consent:
            raise HTTPException(status_code=403, detail="Doctor not authorized")
    
    file_bytes = await file.read()
    file_hash = hashlib.sha256(file_bytes).hexdigest()
    
    content_type = file.content_type or "application/octet-stream"
    file_type = "pdf" if "pdf" in content_type else "image" if "image" in content_type else "document"
    
    ipfs_hash = await save_file(file_bytes, file.filename or "record")
    
    record = MedicalRecord(
        patient_id=patient_id,
        uploader_id=uploader_id,
        uploader_role=uploader_role,
        title=title,
        description=description,
        file_type=file_type,
        content_type=content_type,
        ipfs_hash=ipfs_hash,
        file_hash=file_hash,
        size_bytes=len(file_bytes),
        blockchain_tx=blockchain_tx,
        is_confirmed=blockchain_tx is not None
    )
    
    doc = record.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.records.insert_one(doc)
    
    return {"id": record.id, "ipfs_hash": ipfs_hash, "file_hash": file_hash, "message": "Record uploaded"}

@api_router.get("/records")
async def list_records(patient_id: Optional[str] = None, uploader_id: Optional[str] = None):
    query = {}
    if patient_id:
        query["patient_id"] = patient_id
    if uploader_id:
        query["uploader_id"] = uploader_id
    return await db.records.find(query, {"_id": 0}).to_list(100)

@api_router.get("/records/{record_id}")
async def get_record(record_id: str):
    record = await db.records.find_one({"id": record_id}, {"_id": 0})
    if not record:
        raise HTTPException(status_code=404, detail="Not found")
    return record

@api_router.get("/records/{record_id}/content")
async def get_record_content(record_id: str, requester_id: str):
    record = await db.records.find_one({"id": record_id}, {"_id": 0})
    if not record:
        raise HTTPException(status_code=404, detail="Not found")
    
    if record["patient_id"] != requester_id:
        consent = await db.consents.find_one({"patient_id": record["patient_id"], "doctor_id": requester_id, "active": True}, {"_id": 0})
        if not consent:
            raise HTTPException(status_code=403, detail="Not authorized")
    
    content = await retrieve_file(record["ipfs_hash"])
    if not content:
        raise HTTPException(status_code=500, detail="File not found")
    
    return {"content": base64.b64encode(content).decode(), "content_type": record["content_type"], "filename": record["title"]}

@api_router.put("/records/{record_id}/confirm")
async def confirm_record(record_id: str, blockchain_tx: str):
    result = await db.records.update_one({"id": record_id}, {"$set": {"blockchain_tx": blockchain_tx, "is_confirmed": True}})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"message": "Record confirmed"}

# Consent Routes
@api_router.post("/consents")
async def create_consent(data: ConsentCreate):
    patient = await db.patients.find_one({"id": data.patient_id}, {"_id": 0})
    doctor = await db.doctors.find_one({"id": data.doctor_id}, {"_id": 0})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    consent = Consent(**data.model_dump())
    doc = consent.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    if doc['revoked_at']:
        doc['revoked_at'] = doc['revoked_at'].isoformat()
    await db.consents.insert_one(doc)
    return {"id": consent.id, "message": "Consent granted"}

@api_router.get("/consents")
async def list_consents(patient_id: Optional[str] = None, doctor_id: Optional[str] = None):
    query = {}
    if patient_id:
        query["patient_id"] = patient_id
    if doctor_id:
        query["doctor_id"] = doctor_id
    return await db.consents.find(query, {"_id": 0}).to_list(100)

@api_router.put("/consents/{consent_id}/revoke")
async def revoke_consent(consent_id: str):
    result = await db.consents.update_one({"id": consent_id}, {"$set": {"active": False, "revoked_at": datetime.now(timezone.utc).isoformat()}})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"message": "Consent revoked"}

# Chat Routes
@api_router.post("/chat")
async def chat(request: ChatRequest):
    context = ""
    image_analysis = None
    text_analysis = None
    
    # Handle session management
    session_id = request.session_id
    if not session_id:
        # Create a new session if none provided
        session = ChatSession(
            user_id=request.user_id,
            title=f"Chat {datetime.now().strftime('%m/%d %H:%M')}"
        )
        session_doc = session.model_dump()
        session_doc['created_at'] = session_doc['created_at'].isoformat()
        session_doc['updated_at'] = session_doc['updated_at'].isoformat()
        await db.chat_sessions.insert_one(session_doc)
        session_id = session.id
    else:
        # Update existing session's updated_at timestamp
        await db.chat_sessions.update_one(
            {"id": session_id, "user_id": request.user_id},
            {"$set": {"updated_at": datetime.now(timezone.utc).isoformat()}}
        )
    
    # Try to import Ollama assistant - REQUIRED for chat
    try:
        from ollama_assistant import get_ollama_assistant
        ollama = get_ollama_assistant()
        ollama_available = ollama.available
    except Exception as e:
        logger.error(f"Ollama import error: {e}")
        ollama_available = False
    
    # If Ollama is not available, return error message
    if not ollama_available:
        error_response = """I apologize, but the AI assistant is currently unavailable. 

To enable the chat assistant:
1. Ensure Ollama is running
2. Check status: python backend/check_ollama.py
3. Install model if needed: python backend/install_ollama_model.py

Please contact your system administrator if the issue persists."""
        
        chat_msg = ChatMessage(
            session_id=session_id,
            user_id=request.user_id,
            user_role=request.user_role,
            message=request.message,
            response=error_response,
            attached_records=request.attached_record_ids
        )
        doc = chat_msg.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        await db.chat_messages.insert_one(doc)
        
        # Update session message count
        await db.chat_sessions.update_one(
            {"id": session_id},
            {"$inc": {"message_count": 1}}
        )
        
        return {
            "id": chat_msg.id,
            "session_id": session_id,
            "response": error_response,
            "attached_records_analyzed": 0,
            "ollama_powered": False,
            "error": "Ollama not available"
        }
    
    # Try to import AI models for analysis (without Ollama to avoid double processing)
    try:
        from ai_models_finetuned import analyze_medical_image, analyze_medical_text
        ai_available = True
    except ImportError:
        try:
            from ai_models import analyze_medical_image, analyze_medical_text
            ai_available = True
        except ImportError:
            ai_available = False
    
    # Analyze attached records
    for record_id in request.attached_record_ids:
        record = await db.records.find_one({"id": record_id}, {"_id": 0})
        if record and record["patient_id"] == request.user_id:
            content = await retrieve_file(record["ipfs_hash"])
            if content and record["file_type"] == "pdf":
                text = await extract_pdf_text(content)
                if text:
                    context += f"\n\n**{record['title']}:**\n{text[:1000]}"
            elif content and record["file_type"] == "image":
                if ai_available:
                    # Analyze without Ollama to avoid double processing
                    image_analysis = analyze_medical_image(content, use_ollama=False)
                    context += f"\n\n**{record['title']}:** Medical image analyzed with AI."
                else:
                    context += f"\n\n**{record['title']}:** Medical image uploaded for analysis."
    
    # Analyze the user's message text (without Ollama to avoid double processing)
    if ai_available:
        text_analysis = analyze_medical_text(request.message, use_ollama=False)
    
    # Generate response using Ollama ONLY
    try:
        response = ollama.answer_medical_question(
            question=request.message,
            context={
                "image_analysis": image_analysis,
                "text_analysis": text_analysis,
                "medical_records": context,
                "user_role": request.user_role
            }
        )
        
        # Add subtle model indicator at the end
        if not response.endswith("*"):
            response = f"{response}\n\n*Powered by Ollama AI*"
        
    except Exception as e:
        logger.error(f"Ollama chat error: {e}")
        response = f"""I apologize, but I encountered an error processing your question.

Error: {str(e)}

Please try:
1. Asking a simpler question
2. Rephrasing your question
3. Checking if Ollama is running properly

If the issue persists, contact your system administrator."""
    
    # Save chat message
    chat_msg = ChatMessage(
        session_id=session_id,
        user_id=request.user_id,
        user_role=request.user_role,
        message=request.message,
        response=response,
        attached_records=request.attached_record_ids
    )
    doc = chat_msg.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.chat_messages.insert_one(doc)
    
    # Update session message count
    await db.chat_sessions.update_one(
        {"id": session_id},
        {"$inc": {"message_count": 1}}
    )
    
    return {
        "id": chat_msg.id, 
        "session_id": session_id,
        "response": response, 
        "attached_records_analyzed": len(request.attached_record_ids),
        "ollama_powered": True
    }
    
    return {
        "id": chat_msg.id, 
        "response": response, 
        "attached_records_analyzed": len(request.attached_record_ids),
        "ollama_powered": True
    }

@api_router.get("/chat/history")
async def get_chat_history(user_id: str, session_id: Optional[str] = None, limit: int = 50):
    """Get chat history for a user, optionally filtered by session"""
    query = {"user_id": user_id}
    if session_id:
        query["session_id"] = session_id
    
    messages = await db.chat_messages.find(query, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
    return list(reversed(messages))

# Chat Session Management Endpoints
@api_router.post("/chat/sessions")
async def create_chat_session(user_id: str, title: str = "New Chat"):
    """Create a new chat session"""
    session = ChatSession(
        user_id=user_id,
        title=title
    )
    
    doc = session.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    await db.chat_sessions.insert_one(doc)
    
    return {"id": session.id, "title": session.title, "message": "Session created"}

@api_router.get("/chat/sessions")
async def get_chat_sessions(user_id: str):
    """Get all chat sessions for a user"""
    sessions = await db.chat_sessions.find(
        {"user_id": user_id}, 
        {"_id": 0}
    ).sort("updated_at", -1).to_list(100)
    
    return sessions

@api_router.get("/chat/sessions/{session_id}")
async def get_chat_session(session_id: str, user_id: str):
    """Get a specific chat session"""
    session = await db.chat_sessions.find_one(
        {"id": session_id, "user_id": user_id}, 
        {"_id": 0}
    )
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session

@api_router.put("/chat/sessions/{session_id}")
async def update_chat_session(session_id: str, user_id: str, title: str):
    """Update chat session title"""
    result = await db.chat_sessions.update_one(
        {"id": session_id, "user_id": user_id},
        {"$set": {
            "title": title,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"message": "Session updated"}

@api_router.delete("/chat/sessions/{session_id}")
async def delete_chat_session(session_id: str, user_id: str):
    """Delete a chat session and all its messages"""
    # Delete all messages in the session
    await db.chat_messages.delete_many({"session_id": session_id, "user_id": user_id})
    
    # Delete the session
    result = await db.chat_sessions.delete_one({"id": session_id, "user_id": user_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"message": "Session deleted"}

@api_router.delete("/chat/sessions/{session_id}/messages")
async def clear_chat_session(session_id: str, user_id: str):
    """Clear all messages in a chat session"""
    result = await db.chat_messages.delete_many({"session_id": session_id, "user_id": user_id})
    
    # Update session message count and updated_at
    await db.chat_sessions.update_one(
        {"id": session_id, "user_id": user_id},
        {"$set": {
            "message_count": 0,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {"message": f"Cleared {result.deleted_count} messages"}

@api_router.get("/chat/sessions/{session_id}/messages")
async def get_session_messages(session_id: str, user_id: str, limit: int = 50):
    """Get messages for a specific session"""
    messages = await db.chat_messages.find(
        {"session_id": session_id, "user_id": user_id}, 
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    return list(reversed(messages))

# Record Analysis endpoint
@api_router.post("/records/{record_id}/analyze")
async def analyze_record(record_id: str, requester_id: str):
    """Generate AI analysis/summary of a medical record using Ollama"""
    record = await db.records.find_one({"id": record_id}, {"_id": 0})
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    # Check authorization
    if record["patient_id"] != requester_id:
        consent = await db.consents.find_one({
            "patient_id": record["patient_id"], 
            "doctor_id": requester_id, 
            "active": True
        }, {"_id": 0})
        if not consent:
            raise HTTPException(status_code=403, detail="Not authorized")
    
    # Retrieve file content
    content = await retrieve_file(record["ipfs_hash"])
    if not content:
        raise HTTPException(status_code=500, detail="File not found")
    
    analysis_result = {
        "record_id": record_id,
        "title": record["title"],
        "file_type": record["file_type"],
        "analysis": None,
        "summary": None,
        "key_findings": [],
        "recommendations": [],
        "ollama_powered": False
    }
    
    # Try to get Ollama assistant for professional medical analysis
    try:
        from ollama_assistant import get_ollama_assistant
        ollama = get_ollama_assistant()
        ollama_available = ollama.available
    except Exception as e:
        logger.error(f"Ollama import error: {e}")
        ollama_available = False
    
    # Try to use AI models for initial processing
    try:
        from ai_models_finetuned import analyze_medical_image, analyze_medical_text, get_model_status
        ai_available = True
        model_status = get_model_status()
    except ImportError:
        try:
            from ai_models import analyze_medical_image, analyze_medical_text, get_model_status
            ai_available = True
            model_status = get_model_status()
        except ImportError:
            ai_available = False
            model_status = {}
    
    extracted_text = ""
    image_analysis = None
    
    if record["file_type"] == "pdf":
        # Extract text from PDF
        text = await extract_pdf_text(content)
        if text:
            extracted_text = text[:3000]  # Increased limit for better analysis
            analysis_result["extracted_text"] = text[:2000]  # Keep shorter version for display
        else:
            # If PDF text extraction fails, use raw content as text (for debugging)
            try:
                extracted_text = content.decode('utf-8')[:3000]
                analysis_result["extracted_text"] = extracted_text[:2000]
                logger.info("PDF text extraction failed, using raw content")
            except:
                extracted_text = f"PDF document: {record['title']} - {record.get('description', '')}"
                logger.info("Could not decode content, using document metadata")
            
        # Use ClinicalBERT if available for initial processing
        if ai_available and model_status.get("clinicalbert"):
            try:
                text_analysis = analyze_medical_text(extracted_text, use_ollama=False)
            except:
                text_analysis = None
                    
    elif record["file_type"] == "image":
        # Analyze medical image with EfficientNet if available
        if ai_available and model_status.get("efficientnet"):
            try:
                image_analysis = analyze_medical_image(content, use_ollama=False)
                extracted_text = f"Medical image analysis: {image_analysis.get('analysis', 'Image processed')}"
            except:
                image_analysis = None
                extracted_text = "Medical image uploaded for analysis"
        else:
            extracted_text = "Medical image uploaded for analysis"
    else:
        extracted_text = f"Medical document: {record['title']} - {record.get('description', '')}"
    
    # Use Ollama for professional medical analysis
    if ollama_available and extracted_text:
        try:
            logger.info(f"Starting Ollama analysis for record {record_id}")
            logger.info(f"Extracted text length: {len(extracted_text)}")
            
            # Create a more specific and detailed medical analysis prompt
            document_type = record['file_type'].upper()
            document_title = record['title']
            document_desc = record.get('description', 'Medical document')
            
            logger.info(f"Document type: {document_type}, Title: {document_title}")
            
            # Build context-specific prompt based on document type
            if document_type == "PDF" and any(term in extracted_text.lower() for term in ["blood", "lab", "test", "result"]):
                analysis_type = "laboratory report"
                specific_instructions = """
Focus on:
- Laboratory values and reference ranges
- Abnormal findings and their clinical significance
- Patterns indicating specific conditions
- Risk stratification and urgency of findings
- Specific follow-up testing recommendations"""
            elif document_type == "IMAGE" or any(term in extracted_text.lower() for term in ["xray", "ct", "mri", "ultrasound", "scan"]):
                analysis_type = "medical imaging study"
                specific_instructions = """
Focus on:
- Anatomical structures and abnormalities
- Radiological findings and their implications
- Comparison with normal anatomy
- Differential diagnoses based on imaging
- Need for additional imaging or correlation"""
            elif any(term in extracted_text.lower() for term in ["prescription", "medication", "drug", "dosage"]):
                analysis_type = "medication prescription"
                specific_instructions = """
Focus on:
- Medication appropriateness and indications
- Dosing accuracy and safety considerations
- Drug interactions and contraindications
- Monitoring requirements
- Patient education needs"""
            else:
                analysis_type = "medical document"
                specific_instructions = """
Focus on:
- Clinical significance of documented findings
- Diagnostic implications
- Treatment considerations
- Patient safety factors
- Care coordination needs"""
            
            logger.info(f"Analysis type determined: {analysis_type}")
            
            medical_prompt = f"""You are a medical specialist analyzing a {analysis_type}. Provide a comprehensive, professional medical analysis.

DOCUMENT INFORMATION:
- Type: {document_type}
- Title: {document_title}
- Description: {document_desc}

CLINICAL DATA:
{extracted_text}

{specific_instructions}

Provide your analysis in this EXACT format:

SUMMARY:
[Write 2-3 sentences summarizing the key medical findings and their overall clinical significance. Be specific about abnormalities, conditions, or concerns identified.]

KEY FINDINGS:
• [List 3-5 specific, clinically relevant findings]
• [Include abnormal values, concerning symptoms, or notable observations]
• [Prioritize findings by clinical importance]

CLINICAL INTERPRETATION:
[Explain what these findings mean medically. Discuss potential diagnoses, disease processes, or health implications. Be specific about medical significance.]

RECOMMENDATIONS:
• [Provide 3-5 specific, actionable medical recommendations]
• [Include follow-up care, additional testing, specialist referrals]
• [Prioritize by urgency and importance]

FOLLOW-UP CARE:
• [Suggest specific monitoring, timeline for reassessment]
• [Identify when to seek immediate medical attention]
• [Recommend preventive measures or lifestyle modifications]

Use professional medical terminology but ensure clarity. Focus on actionable insights and patient safety."""

            logger.info("Sending prompt to Ollama for medical analysis")
            
            # Get Ollama analysis with extended timeout for complex analysis
            ollama_response = ollama.answer_medical_question(
                question=medical_prompt,
                context={
                    "document_type": record["file_type"],
                    "document_title": record["title"],
                    "image_analysis": image_analysis,
                    "extracted_text": extracted_text,
                    "user_role": "medical_analysis"
                }
            )
            
            logger.info(f"Ollama analysis completed, response length: {len(ollama_response)}")
            
            # Store the full Ollama response
            analysis_result["analysis"] = ollama_response
            analysis_result["ollama_powered"] = True
            
            # Parse structured sections from Ollama response
            response_upper = ollama_response.upper()
            
            # Extract Summary
            if "SUMMARY:" in response_upper:
                try:
                    summary_start = ollama_response.upper().find("SUMMARY:") + 8
                    summary_end = min([
                        pos for pos in [
                            ollama_response.upper().find("KEY FINDINGS:", summary_start),
                            ollama_response.upper().find("CLINICAL INTERPRETATION:", summary_start),
                            len(ollama_response)
                        ] if pos > summary_start
                    ])
                    summary_text = ollama_response[summary_start:summary_end].strip()
                    analysis_result["summary"] = f"**Professional Medical Analysis**\n\n{summary_text}\n\n*Powered by Ollama Medical AI Specialist*"
                    logger.info("Summary extracted successfully")
                except Exception as e:
                    logger.error(f"Error extracting summary: {e}")
                    analysis_result["summary"] = f"**Professional Medical Analysis**\n\n{ollama_response[:400]}...\n\n*Powered by Ollama Medical AI Specialist*"
            
            # Extract Key Findings
            if "KEY FINDINGS:" in response_upper:
                try:
                    findings_start = ollama_response.upper().find("KEY FINDINGS:") + 13
                    findings_end = min([
                        pos for pos in [
                            ollama_response.upper().find("CLINICAL INTERPRETATION:", findings_start),
                            ollama_response.upper().find("RECOMMENDATIONS:", findings_start),
                            len(ollama_response)
                        ] if pos > findings_start
                    ])
                    findings_text = ollama_response[findings_start:findings_end].strip()
                    findings_lines = [
                        line.strip().lstrip("•-*").strip() 
                        for line in findings_text.split('\n') 
                        if line.strip() and not line.strip().startswith('[') and len(line.strip()) > 5
                    ]
                    analysis_result["key_findings"] = findings_lines[:6]  # Top 6 findings
                    logger.info(f"Key findings extracted: {len(analysis_result['key_findings'])} items")
                except Exception as e:
                    logger.error(f"Error extracting key findings: {e}")
                    analysis_result["key_findings"] = ["Professional medical analysis completed", "Detailed findings available in full report"]
            
            # Extract Recommendations
            if "RECOMMENDATIONS:" in response_upper:
                try:
                    rec_start = ollama_response.upper().find("RECOMMENDATIONS:") + 16
                    rec_end = min([
                        pos for pos in [
                            ollama_response.upper().find("FOLLOW-UP CARE:", rec_start),
                            len(ollama_response)
                        ] if pos > rec_start
                    ])
                    rec_text = ollama_response[rec_start:rec_end].strip()
                    rec_lines = [
                        line.strip().lstrip("•-*").strip() 
                        for line in rec_text.split('\n') 
                        if line.strip() and not line.strip().startswith('[') and len(line.strip()) > 5
                    ]
                    analysis_result["recommendations"] = rec_lines[:6]  # Top 6 recommendations
                    logger.info(f"Recommendations extracted: {len(analysis_result['recommendations'])} items")
                except Exception as e:
                    logger.error(f"Error extracting recommendations: {e}")
                    analysis_result["recommendations"] = ["Consult healthcare provider for detailed interpretation", "Follow medical professional guidance"]
            
            # If parsing failed, use fallback extraction
            if not analysis_result["key_findings"]:
                logger.warning("Key findings parsing failed, using fallback extraction")
                # Extract bullet points or numbered items as findings
                lines = ollama_response.split('\n')
                findings = []
                for line in lines:
                    line = line.strip()
                    if (line.startswith('•') or line.startswith('-') or line.startswith('*') or 
                        (len(line) > 0 and line[0].isdigit() and '.' in line[:3])):
                        clean_line = line.lstrip('•-*0123456789. ').strip()
                        if len(clean_line) > 10:
                            findings.append(clean_line)
                analysis_result["key_findings"] = findings[:5] if findings else ["Comprehensive medical analysis completed"]
            
            if not analysis_result["recommendations"]:
                logger.warning("Recommendations parsing failed, using fallback extraction")
                # Look for recommendation-like content
                rec_keywords = ["recommend", "suggest", "should", "consider", "follow", "monitor", "consult"]
                lines = ollama_response.split('\n')
                recommendations = []
                for line in lines:
                    if any(keyword in line.lower() for keyword in rec_keywords) and len(line.strip()) > 15:
                        clean_line = line.strip().lstrip('•-*0123456789. ').strip()
                        if clean_line:
                            recommendations.append(clean_line)
                analysis_result["recommendations"] = recommendations[:5] if recommendations else ["Follow up with healthcare provider", "Discuss findings with medical professional"]
            
            logger.info(f"Ollama analysis successfully processed for record {record_id}")
            
        except Exception as e:
            logger.error(f"Ollama analysis error for record {record_id}: {e}")
            logger.error(f"Error details: {type(e).__name__}: {str(e)}")
            # Set flag to use fallback
            ollama_available = False
    
    # Fallback to basic analysis if Ollama is not available
    if not ollama_available:
        if record["file_type"] == "pdf" and extracted_text:
            # Basic pattern matching for document type
            text_lower = extracted_text.lower()
            
            if any(term in text_lower for term in ["blood", "hemoglobin", "wbc", "rbc", "platelet", "cbc"]):
                analysis_result["summary"] = "**Blood Test Report**\n\nComplete Blood Count (CBC) or blood chemistry panel detected. This report contains important information about blood cell counts and biochemical markers."
                analysis_result["key_findings"] = ["Blood test parameters detected", "Requires professional interpretation"]
                analysis_result["recommendations"] = ["Review results with healthcare provider", "Follow up on any abnormal values"]
                
            elif any(term in text_lower for term in ["glucose", "sugar", "hba1c", "diabetes", "insulin"]):
                analysis_result["summary"] = "**Diabetes/Glucose Monitoring Report**\n\nDocument contains glucose or diabetes-related test results. Important for diabetes management and metabolic health assessment."
                analysis_result["key_findings"] = ["Glucose/diabetes markers present", "Metabolic health indicators"]
                analysis_result["recommendations"] = ["Discuss results with endocrinologist", "Monitor blood sugar levels", "Follow diabetes management plan"]
                
            elif any(term in text_lower for term in ["cholesterol", "ldl", "hdl", "triglyceride", "lipid"]):
                analysis_result["summary"] = "**Lipid Profile Report**\n\nCardiovascular risk assessment through cholesterol and lipid measurements. Important for heart health evaluation."
                analysis_result["key_findings"] = ["Cholesterol/lipid values present", "Cardiovascular risk markers"]
                analysis_result["recommendations"] = ["Review with cardiologist", "Consider dietary modifications", "Assess cardiovascular risk"]
                
            elif any(term in text_lower for term in ["prescription", "rx", "medication", "dosage", "tablet", "capsule"]):
                analysis_result["summary"] = "**Prescription Document**\n\nMedication prescription with dosage instructions. Critical for proper medication management and adherence."
                analysis_result["key_findings"] = ["Medication prescription detected", "Dosage instructions present"]
                analysis_result["recommendations"] = ["Follow prescribed dosage exactly", "Monitor for side effects", "Complete full course as directed"]
                
            elif any(term in text_lower for term in ["xray", "x-ray", "ct", "mri", "ultrasound", "imaging", "scan"]):
                analysis_result["summary"] = "**Medical Imaging Report**\n\nRadiological study results requiring professional interpretation. Important for diagnosis and treatment planning."
                analysis_result["key_findings"] = ["Medical imaging study", "Requires radiologist interpretation"]
                analysis_result["recommendations"] = ["Discuss findings with ordering physician", "Follow up as recommended", "Consider additional imaging if needed"]
                
            else:
                analysis_result["summary"] = "**Medical Document**\n\nGeneral medical document uploaded for review. Contains healthcare-related information requiring professional evaluation."
                analysis_result["key_findings"] = ["Medical document processed", "Professional review recommended"]
                analysis_result["recommendations"] = ["Review with healthcare provider", "Ensure proper medical record keeping"]
            
            analysis_result["analysis"] = "Document processed with basic medical pattern recognition"
            
        elif record["file_type"] == "image":
            if image_analysis:
                analysis_result["summary"] = f"**Medical Image Analysis**\n\n{image_analysis.get('analysis', 'Medical image processed with AI analysis.')}\n\n*Processed with EfficientNet medical imaging model*"
                analysis_result["key_findings"] = image_analysis.get("findings", ["Medical image processed"])
                analysis_result["recommendations"] = image_analysis.get("recommendations", ["Consult radiologist for detailed interpretation"])
                analysis_result["analysis"] = "Image analyzed with deep learning model"
            else:
                analysis_result["summary"] = "**Medical Image Uploaded**\n\nMedical image stored for professional review. Requires specialist interpretation for accurate diagnosis."
                analysis_result["key_findings"] = ["Medical image uploaded", "Awaiting professional interpretation"]
                analysis_result["recommendations"] = ["Consult radiologist or specialist", "Ensure image quality is adequate", "Correlate with clinical symptoms"]
                analysis_result["analysis"] = "Image stored for professional review"
        else:
            analysis_result["summary"] = "**Medical Document Uploaded**\n\nDocument successfully stored in secure medical records system."
            analysis_result["key_findings"] = ["Document uploaded successfully"]
            analysis_result["recommendations"] = ["Review with healthcare provider"]
            analysis_result["analysis"] = "Document stored successfully"
    
    # Add professional disclaimer
    analysis_result["disclaimer"] = "This AI analysis is for informational purposes only and should not replace professional medical advice. Always consult with qualified healthcare professionals for medical diagnosis, treatment decisions, and health management."
    
    # Save analysis to database
    await db.record_analyses.update_one(
        {"record_id": record_id},
        {"$set": {
            "record_id": record_id,
            "analysis": analysis_result,
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
            "requester_id": requester_id
        }},
        upsert=True
    )
    
    return analysis_result

@api_router.get("/records/{record_id}/analysis")
async def get_record_analysis(record_id: str, requester_id: str):
    """Get stored analysis for a record"""
    record = await db.records.find_one({"id": record_id}, {"_id": 0})
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    # Check authorization
    if record["patient_id"] != requester_id:
        consent = await db.consents.find_one({
            "patient_id": record["patient_id"], 
            "doctor_id": requester_id, 
            "active": True
        }, {"_id": 0})
        if not consent:
            raise HTTPException(status_code=403, detail="Not authorized")
    
    analysis = await db.record_analyses.find_one({"record_id": record_id}, {"_id": 0})
    if not analysis:
        raise HTTPException(status_code=404, detail="No analysis found. Click Analyze to generate.")
    
    return analysis["analysis"]

# User lookup
@api_router.get("/users/wallet/{wallet}")
async def get_user_by_wallet(wallet: str):
    """Look up user by wallet address across all user types"""
    wallet_lower = wallet.lower()
    
    try:
        # Check patients
        patient = await db.patients.find_one({"wallet_address": wallet_lower}, {"_id": 0})
        if patient:
            return {
                "user_type": "patient",
                "user_id": patient["id"],
                "name": patient["name"],
                "email": patient.get("email", ""),
                "wallet_address": patient["wallet_address"]
            }
        
        # Check doctors
        doctor = await db.doctors.find_one({"wallet_address": wallet_lower}, {"_id": 0})
        if doctor:
            return {
                "user_type": "doctor",
                "user_id": doctor["id"],
                "name": doctor["name"],
                "email": doctor.get("email", ""),
                "wallet_address": doctor["wallet_address"],
                "specialization": doctor.get("specialization", ""),
                "institution_id": doctor.get("institution_id", "")
            }
        
        # Check institutions
        institution = await db.institutions.find_one({"wallet_address": wallet_lower}, {"_id": 0})
        if institution:
            return {
                "user_type": "institution",
                "user_id": institution["id"],
                "name": institution["name"],
                "email": institution.get("email", ""),
                "wallet_address": institution["wallet_address"]
            }
        
        # User not found
        raise HTTPException(status_code=404, detail="User not found")
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log other errors and return 500
        logger.error(f"Error looking up user by wallet {wallet}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.get("/")
async def root():
    return {"message": "MedChain AI API", "status": "healthy"}

@api_router.get("/health")
async def health_check():
    try:
        from ai_models_finetuned import get_model_status
        model_status = get_model_status()
    except ImportError:
        try:
            from ai_models import get_model_status
            model_status = get_model_status()
        except ImportError:
            model_status = {"efficientnet": False, "clinicalbert": False, "models_loaded": False}
    
    # Check Ollama availability
    ollama_status = False
    try:
        from ollama_assistant import is_ollama_available
        ollama_status = is_ollama_available()
    except:
        pass
    
    return {
        "status": "healthy", 
        "ai_models": {
            "rule_based": True,
            "ollama_available": ollama_status,
            **model_status
        }
    }

app.include_router(api_router)

logger.info("CORS middleware configured for localhost and 127.0.0.1 ports 3000-3003")

@app.on_event("startup")
async def startup_event():
    """Load AI models on startup in background"""
    logger.info("Starting MedChain API server...")
    # Skip heavy AI model loading for faster startup
    # Models will be loaded on-demand when needed
    logger.info("Server started successfully - AI models will load on-demand")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
