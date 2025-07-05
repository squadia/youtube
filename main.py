from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "API YouTube opérationnelle"}

@app.post("/transcript")
async def get_transcript(request: Request):
    try:
        data = await request.json()
        video_id = data.get("video_id")
        if not video_id:
            return JSONResponse(status_code=400, content={"error": "Aucun ID vidéo fourni."})
        return {"status": "ok", "video_id": video_id}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
