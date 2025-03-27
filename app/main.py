from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.content import router as content_router
from app.services.nlp_processor import nlp

app = FastAPI(
    title="Content Capsule Generator API",
    description="API for generating learning capsules from natural language prompts",
    version="0.1.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(content_router)

@app.on_event("startup")
async def startup_event():
    # Initialize NLP model
    nlp("Initialize model")  # Warm-up call

@app.get("/")
async def root():
    return {
        "message": "Content Capsule Generator API is running",
        "endpoints": {
            "/content/generate": "POST - Generate learning capsules"
        }
    }
