import fastapi
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from src.routers.courier import router as router_courier
from src.routers.order import router as router_order

app = fastapi.FastAPI(debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router_courier, tags=['courier'])
app.include_router(router_order, tags=['order'])

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5051)