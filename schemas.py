"""
Database Schemas for Barbershop SaaS

Each Pydantic model = one MongoDB collection (lowercased class name)
Examples:
- Shop -> "shop"
- Client -> "client"
- Appointment -> "appointment"
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class Shop(BaseModel):
    name: str = Field(..., description="Barbershop name")
    address: Optional[str] = Field(None, description="Street address")
    phone: Optional[str] = Field(None, description="Contact phone")
    timezone: Optional[str] = Field("UTC", description="IANA timezone, e.g., America/New_York")

class Staff(BaseModel):
    shop_id: str = Field(..., description="Associated shop id")
    name: str
    role: str = Field("Barber", description="Role at shop")
    email: Optional[str] = None
    phone: Optional[str] = None
    active: bool = True

class Service(BaseModel):
    shop_id: str
    name: str
    duration_minutes: int = Field(..., ge=5, le=240)
    price: float = Field(..., ge=0)
    description: Optional[str] = None

class Client(BaseModel):
    shop_id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None

class Appointment(BaseModel):
    shop_id: str
    client_id: str
    staff_id: str
    service_id: str
    start_time: datetime
    end_time: datetime
    status: str = Field("scheduled", description="scheduled|completed|no_show|cancelled")
    notes: Optional[str] = None

class CRMWorkflow(BaseModel):
    shop_id: str
    name: str
    trigger: str = Field(..., description="e.g., 'no_visit_days>60', 'new_client', 'birthday' (YYYY-MM-DD)")
    channel: str = Field("sms", description="sms|email")
    message_template: str = Field(..., description="Template with {name}, {shop} placeholders")
    active: bool = True

# Backwards-compatible examples (kept if needed by tools)
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = None
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
