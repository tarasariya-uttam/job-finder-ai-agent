from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_jobs():
    return {"message": "Job API ready."}

@router.get("/search")
async def search_jobs():
    return {"message": "Job search endpoint - to be implemented"} 