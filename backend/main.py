from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os

# Import services
# Assuming these are in the same directory for simplicity
from ml_service import MLService
from serp_service import SerpService
from navigation_service import NavigationService

app = FastAPI(title="ACL 2026 Safety API", version="1.0.0")

# CORS Setup
origins = [
    "http://localhost:3000",
    "http://localhost:5173", # Vite default
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://localhost:5000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Services
ml_service = MLService()
serp_service = SerpService()
nav_service = NavigationService()

# --- Pydantic Models ---
class LocationPing(BaseModel):
    lat: float
    lng: float
    device_id: str
    timestamp: Optional[str] = None

class RouteRequest(BaseModel):
    start_lat: float
    start_lng: float
    end_lat: Optional[float] = None
    end_lng: Optional[float] = None
    prefer_wheelchair: bool = False
    avoid_crowds: bool = False
    closest_exit: bool = False

class SOSAlert(BaseModel):
    lat: float
    lng: float
    user_id: str
    message: Optional[str] = "SOS Alert"

# --- Endpoints ---

@app.get("/")
async def root():
    return {"message": "ACL 2026 Safety API is running"}

@app.post("/ping-location")
async def ping_location(ping: LocationPing):
    """
    Receives location pings from user devices to update crowd density maps.
    """
    # In a real app, store this in a database (PostGIS, Redis, etc.)
    # For now, we just acknowledge receipt
    print(f"Received ping from {ping.device_id} at {ping.lat}, {ping.lng}")

    # Analyze risk for this location (Mock)
    # Mock data for demonstration: density=50, hour=20, dist=100m, terrain=0.2
    risk_level = ml_service.predict_crowd_risk(50, 20, 100, 0.2)

    return {"status": "received", "current_risk": risk_level}

@app.get("/heatmap")
async def get_heatmap():
    """
    Returns heatmap data for crowd density visualization.
    """
    # In a real app, query database for recent pings and aggregate
    data = ml_service.generate_heatmap_data()
    return data # Returns list of {lat, lng, weight}

@app.get("/markers")
async def get_markers():
    """
    Returns accessibility landmarks (Medical, Exits, etc.)
    """
    return nav_service.get_markers()

@app.post("/safe-route")
async def get_safe_route(route_req: RouteRequest):
    """
    Calculates a safe/accessible route based on preferences.
    """
    route = nav_service.calculate_route(
        start_lat=route_req.start_lat,
        start_lng=route_req.start_lng,
        end_lat=route_req.end_lat,
        end_lng=route_req.end_lng,
        wheelchair=route_req.prefer_wheelchair,
        avoid_crowds=route_req.avoid_crowds,
        closest_exit=route_req.closest_exit
    )
    return {"route": route}

@app.get("/live-alerts")
async def get_live_alerts():
    """
    Fetches real-time alerts from SerpAPI (News/Weather).
    """
    alerts = serp_service.get_live_alerts()
    return alerts

@app.post("/sos")
async def trigger_sos(sos: SOSAlert):
    """
    Triggers an SOS alert.
    """
    # In a real app, this would notify emergency services / security dashboard
    print(f"SOS ALERT from {sos.user_id} at {sos.lat}, {sos.lng}: {sos.message}")
    return {"status": "alert_sent", "message": "Emergency services notified"}
