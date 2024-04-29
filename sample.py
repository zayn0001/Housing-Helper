from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse
import asyncio
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Set to ["*"] to allow requests from any origin
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
async def generate_data():
    for i in range(10):
        yield f"{i}"
        await asyncio.sleep(1)

@app.get("/stream")
async def stream_data(response: Response):
    response.headers["Content-Type"] = "text/event-stream"
    response.headers["Cache-Control"] = "no-cache"
    response.headers["Connection"] = "keep-alive"

    return StreamingResponse(generate_data())
