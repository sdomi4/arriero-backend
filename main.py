from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from observatory.observatory import Observatory

# import routers



@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up observatory...")
    try:
        observatory = Observatory()
        observatory.startup()
        
    except Exception as e:
        print(f"Error during observatory startup: {e}")
        raise e
    
    yield


    print("Shutting down observatory...")


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers