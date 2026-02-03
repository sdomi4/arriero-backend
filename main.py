from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from observatory.observatory import Observatory

# import routers
from routes.dome import router as dome_router
from routes.telescope import router as telescope_router
from routes.camera import router as camera_router
from routes.cover import router as cover_router
from routes.filterwheel import router as filterwheel_router
from routes.switch import router as switch_router
from routes.observing_conditions import router as observing_conditions_router
from routes.safety_monitor import router as safety_monitor_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up observatory...")
    try:
        observatory = Observatory()
        observatory.startup()
        app.state.observatory = observatory
        
    except Exception as e:
        print(f"Error during observatory startup: {e}")
        raise e
    
    yield

    app.state.observatory = None
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
app.include_router(dome_router)
app.include_router(telescope_router)
app.include_router(camera_router)
app.include_router(cover_router)
app.include_router(filterwheel_router)
app.include_router(switch_router)
app.include_router(observing_conditions_router)
app.include_router(safety_monitor_router)