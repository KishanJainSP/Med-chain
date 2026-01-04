#!/usr/bin/env python3
from fastapi import FastAPI, HTTPException
from starlette.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Test CORS Server")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/api/test")
async def test():
    return {"message": "Test endpoint working", "status": "ok"}

@app.get("/api/institutions")
async def test_institutions():
    return []

@app.get("/api/users/wallet/{wallet}")
async def test_user_lookup(wallet: str):
    raise HTTPException(status_code=404, detail="User not found")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)