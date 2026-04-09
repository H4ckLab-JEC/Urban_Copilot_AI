from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class EventType(str, enum.Enum):
    ACCIDENT = "accident"
    CONGESTION = "congestion"
    WEATHER = "weather"
    ROADWORK = "roadwork"
    PUBLIC_EVENT = "public_event"

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(Enum(EventType), index=True)
    location_lat = Column(Float)
    location_lon = Column(Float)
    severity = Column(Integer, nullable=True)
    description = Column(String, nullable=True)
    timestamp = Column(DateTime, server_default=func.now(), index=True)

class TrafficPrediction(Base):
    __tablename__ = "traffic_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(String, index=True)
    predicted_congestion = Column(Float)
    estimated_time = Column(Float)
    confidence = Column(Float)
    timestamp = Column(DateTime, server_default=func.now(), index=True)

class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    origin_lat = Column(Float)
    origin_lon = Column(Float)
    destination_lat = Column(Float)
    destination_lon = Column(Float)
    recommended_route = Column(String)
    estimated_time = Column(Float)
    co2_savings = Column(Float)
    preferred_transport = Column(String, default="auto")
    timestamp = Column(DateTime, server_default=func.now(), index=True)
