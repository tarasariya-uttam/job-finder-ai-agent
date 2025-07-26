from fastapi import FastAPI
from app.routers import jobs

app = FastAPI(
    title="Job Finder AI Agent",
    description="An AI-powered job matching and recommendation system",
    version="1.0.0"
)

# Mount routers
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])

@app.get("/")
async def root():
    return {"message": "Job Finder AI Agent API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 