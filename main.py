import os
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import db, create_document, get_documents

app = FastAPI(title="Barbershop SaaS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CreateShop(BaseModel):
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    timezone: Optional[str] = "UTC"

class CreateClient(BaseModel):
    shop_id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None

class CreateAppointment(BaseModel):
    shop_id: str
    client_id: str
    staff_id: str
    service_id: str
    start_time: datetime
    duration_minutes: int
    notes: Optional[str] = None

@app.get("/")
def root():
    return {"message": "Barbershop SaaS Backend is running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"

    return response

@app.post("/api/shops")
def create_shop(payload: CreateShop):
    shop_id = create_document("shop", payload.model_dump())
    return {"id": shop_id, **payload.model_dump()}

@app.get("/api/shops")
def list_shops(limit: int = 50):
    items = get_documents("shop", {}, limit)
    for it in items:
        it["id"] = str(it.pop("_id", ""))
    return items

@app.post("/api/clients")
def create_client(payload: CreateClient):
    # Optionally verify shop exists
    shop = db["shop"].find_one({"_id": {"$exists": True}})
    client_id = create_document("client", payload.model_dump())
    return {"id": client_id, **payload.model_dump()}

@app.get("/api/clients")
def list_clients(shop_id: Optional[str] = None, limit: int = 100):
    filt = {"shop_id": shop_id} if shop_id else {}
    items = get_documents("client", filt, limit)
    for it in items:
        it["id"] = str(it.pop("_id", ""))
    return items

@app.post("/api/appointments")
def create_appointment(payload: CreateAppointment):
    end_time = payload.start_time + timedelta(minutes=payload.duration_minutes)
    data = payload.model_dump()
    data["end_time"] = end_time
    appt_id = create_document("appointment", data)
    return {"id": appt_id, **data}

@app.get("/api/appointments")
def list_appointments(shop_id: Optional[str] = None, upcoming_only: bool = True, limit: int = 100):
    now = datetime.utcnow()
    filt = {"shop_id": shop_id} if shop_id else {}
    if upcoming_only:
        filt["end_time"] = {"$gte": now}
    items = get_documents("appointment", filt, limit)
    for it in items:
        it["id"] = str(it.pop("_id", ""))
    return items

# Simple AI-powered CRM message generator (placeholder logic)
class CRMMessageRequest(BaseModel):
    client_name: str
    shop_name: str
    context: str  # e.g., "no_show", "overdue", "welcome", "birthday"

@app.post("/api/crm/generate-message")
def generate_crm_message(payload: CRMMessageRequest):
    tone_map = {
        "welcome": "Warm and friendly",
        "overdue": "Helpful reminder",
        "no_show": "Understanding yet firm",
        "birthday": "Celebratory and appreciative",
    }
    tone = tone_map.get(payload.context, "Friendly")
    message = (
        f"Hi {payload.client_name}, this is {payload.shop_name}. "
        f"{tone} note to let you know we'd love to see you again. "
        f"Reply to book or use the link to schedule at your convenience."
    )
    return {"message": message, "tone": tone}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
