from fastapi import APIRouter
from typing import Optional, List
from pydantic import BaseModel
from app.core.config import settings
from app.services.occupancy_service import model_engine

router = APIRouter(prefix=settings.API_V1_STR)

@router.get("/events", tags=["events"])
async def get_events():
    """Get traffic events"""
    return {"events": []}

@router.post("/events", tags=["events"])
async def create_event(event: dict):
    """Create new traffic event"""
    return {"status": "created"}

@router.get("/predictions", tags=["predictions"])
async def get_predictions():
    """Get traffic predictions"""
    return {"predictions": []}

from app.services.route_service import generate_route_recommendation

@router.post("/recommendations", tags=["recommendations"])
async def get_recommendation(data: dict):
    """Get route recommendation with AI"""
    origin = data.get("origin", "Origen")
    destination = data.get("destination", "Destino")
    
    recommendation = await generate_route_recommendation(origin, destination)
    
    return {"recommendation": recommendation}

class OccupancyResponse(BaseModel):
    prediction: dict

class Report(BaseModel):
    id: str
    category: str
    location: str
    description: str
    timestamp: str
    date: str
    time: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class ReportCreate(BaseModel):
    category: str
    location: str
    description: str
    system: Optional[str] = "Otro"
    station: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timestamp: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None

class ReportResponse(BaseModel):
    status: str
    report: Report

@router.post("/occupancy/predict", tags=["occupancy"])
async def predict_occupancy(data: dict):
    """Predict transport crowding/occupancy"""
    transport_type = data.get("transport_type", "metro")
    line = data.get("line", "1")
    station = data.get("station", "Pantitlán")
    time_str = data.get("time") # Optional
    
    prediction = model_engine.predict(transport_type, line, station, time_str)
    return {"prediction": prediction}

@router.post("/occupancy/train", tags=["occupancy"])
async def train_model():
    """Simulate training the occupancy AI model"""
    result = model_engine.train()
    return result

@router.post("/reports", response_model=ReportResponse, tags=["Reports"])
async def create_report(report_in: ReportCreate):
    from datetime import datetime
    import json
    import os
    import uuid

    now = datetime.now()
    # Generar el objeto final con metadatos
    new_report = {
        "id": str(uuid.uuid4()),
        "category": report_in.category,
        "location": report_in.location,
        "system": report_in.system,
        "station": report_in.station,
        "description": report_in.description,
        "latitude": report_in.latitude,
        "longitude": report_in.longitude,
        "timestamp": now.isoformat(),
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S")
    }

    # Persistence (Simple JSON for demo)
    REPORTS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "reports.json")
    os.makedirs(os.path.dirname(REPORTS_FILE), exist_ok=True)
    
    current_reports = []
    if os.path.exists(REPORTS_FILE):
        with open(REPORTS_FILE, "r") as f:
            try:
                current_reports = json.load(f)
            except:
                current_reports = []
    
    current_reports.append(new_report)
    
    with open(REPORTS_FILE, "w") as f:
        json.dump(current_reports, f, indent=2)

    return {"status": "success", "report": Report(**new_report)}

@router.get("/reports", tags=["Reports"])
async def list_reports():
    import json
    import os
    REPORTS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "reports.json")
    if os.path.exists(REPORTS_FILE):
        with open(REPORTS_FILE, "r") as f:
            return json.load(f)
    return []
