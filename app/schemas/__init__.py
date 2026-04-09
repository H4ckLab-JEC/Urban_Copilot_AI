from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EventBase(BaseModel):
    event_type: str
    location_lat: float
    location_lon: float
    severity: Optional[int] = None
    description: Optional[str] = None

class EventCreate(EventBase):
    pass

class Event(EventBase):
    id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

class TrafficPredictionBase(BaseModel):
    route_id: str
    predicted_congestion: float
    estimated_time: float
    confidence: float

class TrafficPredictionCreate(TrafficPredictionBase):
    pass

class TrafficPrediction(TrafficPredictionBase):
    id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

class RecommendationBase(BaseModel):
    user_id: str
    origin_lat: float
    origin_lon: float
    destination_lat: float
    destination_lon: float
    preferred_transport: Optional[str] = "auto"

class RecommendationCreate(RecommendationBase):
    pass

class Recommendation(RecommendationBase):
    id: int
    recommended_route: str
    estimated_time: float
    co2_savings: float
    timestamp: datetime
    
    class Config:
        from_attributes = True
