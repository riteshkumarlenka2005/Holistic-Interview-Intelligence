from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router  # make sure routes.py has router defined
from services.emotion import load_emotion_model
app = FastAPI()

# Allow frontend to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include routes
@app.on_event("startup")
def startup_event():
    load_emotion_model()

app.include_router(router)