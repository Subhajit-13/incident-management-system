from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException

app = FastAPI(
    title="Incident Management System",
    description="Backend API for managing incidents",
    version="1.0.0",
)

class IncidentCreate(BaseModel):
    title: str
    description: str


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

@app.post("/incidents")
def create_incident(incident: IncidentCreate):
    global next_incident_id
    incident_dict = incident.model_dump()
    incident_dict["id"] = next_incident_id
    incidents.append(incident_dict)
    next_incident_id += 1
    return {"message": "Incident created successfully", "incident": incident_dict}

@app.get("/incidents")
def list_incidents():
    return {"incidents": incidents}

