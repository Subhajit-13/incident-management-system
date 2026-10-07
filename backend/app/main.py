from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from enum import Enum
from datetime import datetime

app = FastAPI(
    title="Incident Management System",
    description="Backend API for managing incidents",
    version="1.0.0",
)

class IncidentStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

class IncidentPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
class IncidentCategory(str, Enum):
    APPLICATION="APPLICATION"
    DATABASE="DATABASE"
    NETWORK = "NETWORK"
    SECURITY = "SECURITY"
    INFRASTRUCTURE="INFRASTRUCTURE"
    OTHER = "OTHER"

class IncidentCreate(BaseModel):
    title: str
    description: str
    status: IncidentStatus
    priority: IncidentPriority
    category: IncidentCategory
    reported_by: int
    assigned_to: int | None
    team: str | None
    resolution: str | None

class IncidentUpdate(BaseModel):
    title: str | None
    description: str | None
    status: IncidentStatus | None
    priority: IncidentPriority | None
    category: IncidentCategory | None
    assigned_to: int | None
    team: str | None
    resolution: str | None

class IncidentPatch(BaseModel):
    title: str | None
    description: str | None
    status: IncidentStatus | None
    priority: IncidentPriority | None
    category: IncidentCategory | None
    assigned_to: int | None
    team: str | None
    resolution: str | None

class IncidentResponse(BaseModel):
    id: int
    title: str
    description: str
    status: IncidentStatus
    priority: IncidentPriority
    created_at: datetime
    updated_at: datetime
    category: IncidentCategory
    reported_by: int
    assigned_to: int | None
    team: str | None
    resolution: str | None



incidents = []
next_incident_id = 1


@app.get("/")
def root():
    return {"message": "Incident Management System API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/incidents/{incident_id}")
def get_incident(incident_id: int):
    for incident in incidents:
        if incident["id"] == incident_id:
            return {"incident": incident}
    raise HTTPException(status_code=404, detail="Incident not found")

@app.post("/incidents", response_model=IncidentResponse)
def create_incident(incident: IncidentCreate):

    if incident.status == IncidentStatus.RESOLVED or incident.status == IncidentStatus.CLOSED:
        if incident.resolution is None or incident.resolution.strip() == "":
            raise HTTPException(status_code=400, detail="Resolution must be provided for RESOLVED or CLOSED incidents")
    if incident.status == IncidentStatus.OPEN or incident.status == IncidentStatus.IN_PROGRESS:
        if incident.resolution is not None and incident.resolution.strip() != "":
            raise HTTPException(status_code=400, detail="Resolution must be empty for OPEN or IN_PROGRESS incidents")
        
    global next_incident_id
    incident_dict = incident.model_dump()
    incident_dict["id"] = next_incident_id
    incident_dict["created_at"] = datetime.now()
    incident_dict["updated_at"] = datetime.now()
    incidents.append(incident_dict)
    next_incident_id += 1
    return incident_dict

@app.get("/incidents")
def list_incidents():
    return {"incidents": incidents}

@app.put("/incidents/{incident_id}", response_model=IncidentResponse)
def update_incident(incident_id: int, incident_update: IncidentUpdate):
    for incident in incidents:
        if incident["id"] == incident_id:
            updated_data = incident_update.model_dump()
            if "status" in updated_data:
                new_status = updated_data["status"]
                if new_status == IncidentStatus.RESOLVED or new_status == IncidentStatus.CLOSED:
                    if "resolution" not in updated_data or updated_data["resolution"] is None or updated_data["resolution"].strip() == "":
                        raise HTTPException(status_code=400, detail="Resolution must be provided for RESOLVED or CLOSED incidents")
                if new_status == IncidentStatus.OPEN or new_status == IncidentStatus.IN_PROGRESS:
                    if "resolution" in updated_data and updated_data["resolution"] is not None and updated_data["resolution"].strip() != "":
                        raise HTTPException(status_code=400, detail="Resolution must be empty for OPEN or IN_PROGRESS incidents")
            incident.update(updated_data)
            incident["updated_at"] = datetime.now()
            return incident
    raise HTTPException(status_code=404, detail="Incident not found")


@app.patch("/incidents/{incident_id}", response_model=IncidentResponse)
def patch_incident(incident_id: int, incident_patch: IncidentPatch):
    for incident in incidents:
        if incident["id"] == incident_id:
            updated_data = incident_patch.model_dump(exclude_unset=True)

            if not updated_data:
                raise HTTPException(status_code=400, detail="No fields provided for update")

            final_status = updated_data.get("status", incident.get("status"))
            final_resolution = updated_data.get("resolution", incident.get("resolution"))

            has_resolution = bool(final_resolution and final_resolution.strip())

            if final_status in (IncidentStatus.RESOLVED, IncidentStatus.CLOSED):
                if not has_resolution:
                    raise HTTPException(
                        status_code=400,
                        detail="Resolution must be provided for RESOLVED or CLOSED incidents",
                    )
            elif final_status in (IncidentStatus.OPEN, IncidentStatus.IN_PROGRESS):
                if has_resolution:
                    raise HTTPException(
                        status_code=400,
                        detail="Resolution must be empty for OPEN or IN_PROGRESS incidents",
                    )

            incident.update(updated_data)
            incident["updated_at"] = datetime.now()
            return incident

    raise HTTPException(status_code=404, detail="Incident not found")