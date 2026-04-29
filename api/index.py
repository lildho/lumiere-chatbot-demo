import os
import uuid
import json
from datetime import datetime, time
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage

load_dotenv()

app = FastAPI()

# Izinkan CORS agar frontend bisa memanggil backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Database & History (In-Memory) ---
# CATATAN: Di Vercel, data ini akan reset jika tidak ada aktivitas.
appointments_db = {}
session_histories = {}

class ChatRequest(BaseModel):
    session_id: str
    message: str

OPERATING_HOURS = {
    0: (time(9, 0), time(20, 0)),
    1: (time(9, 0), time(20, 0)),
    2: (time(9, 0), time(20, 0)),
    3: (time(9, 0), time(20, 0)),
    4: (time(9, 0), time(20, 0)),
    5: (time(9, 0), time(17, 0)),
}

@tool
def check_availability(date: str, time_slot: str) -> str:
    """Mengecek ketersediaan slot tanggal (YYYY-MM-DD) dan jam (HH:MM)."""
    try:
        req_date = datetime.strptime(date, "%Y-%m-%d").date()
        req_time = datetime.strptime(time_slot, "%H:%M").time()
    except ValueError:
        return json.dumps({"available": False, "message": "Format salah."})

    day = req_date.weekday()
    if day not in OPERATING_HOURS:
        return json.dumps({"available": False, "message": "Klinik tutup pada hari tersebut."})

    booked = [f"{v['date']}_{v['time']}" for v in appointments_db.values()]
    if f"{date}_{time_slot}" in booked:
        return json.dumps({"available": False, "message": "Slot sudah penuh."})

    return json.dumps({"available": True, "message": "Slot tersedia!"})

@tool
def create_appointment(customer_name: str, service: str, date: str, time_slot: str, phone: str, notes: str = "") -> str:
    """Membuat booking baru setelah konfirmasi data."""
    booking_id = f"LMR-{str(uuid.uuid4())[:6].upper()}"
    appointments_db[booking_id] = {
        "booking_id": booking_id, "customer_name": customer_name,
        "service": service, "date": date, "time": time_slot, "phone": phone
    }
    return json.dumps({"success": True, "booking_id": booking_id, "message": "Berhasil!"})

TOOLS = [check_availability, create_appointment]
TOOL_EXECUTOR = {"check_availability": check_availability, "create_appointment": create_appointment}

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.7,
    api_key=os.getenv("GROQ_API_KEY")
)
llm_with_tools = llm.bind_tools(TOOLS)

SYSTEM_PROMPT = "Kamu adalah Ara, AI Asisten Lumière Clinic. Hangat, elegan, profesional."

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    session_id = request.session_id
    user_msg = request.message
    
    if session_id not in session_histories:
        session_histories[session_id] = []
    
    history = session_histories[session_id]
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + history + [HumanMessage(content=user_msg)]
    
    response = llm_with_tools.invoke(messages)
    
    if response.tool_calls:
        history.append(HumanMessage(content=user_msg))
        history.append(response)
        for tc in response.tool_calls:
            executor = TOOL_EXECUTOR.get(tc["name"])
            res = executor.invoke(tc["args"])
            tool_msg = ToolMessage(content=str(res), tool_call_id=tc["id"])
            messages.append(response)
            messages.append(tool_msg)
            history.append(tool_msg)
        
        final_response = llm_with_tools.invoke(messages)
        final_text = final_response.content
        history.append(AIMessage(content=final_text))
    else:
        final_text = response.content
        history.append(HumanMessage(content=user_msg))
        history.append(AIMessage(content=final_text))

    return {"response": final_text}

@app.delete("/api/conversations/{session_id}")
def clear_chat(session_id: str):
    session_histories.pop(session_id, None)
    return {"success": True}
