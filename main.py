from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi
import openai
import os

app = FastAPI()

openai.api_key = os.getenv("OPENAI_API_KEY")

class VideoUrl(BaseModel):
    url: str

def extract_video_id(url):
    if "watch?v=" in url:
        return url.split("watch?v=")[-1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[-1].split("?")[0]
    else:
        return None

@app.post("/analyser")
async def analyser_video(data: VideoUrl):
    video_id = extract_video_id(data.url)
    if not video_id:
        raise HTTPException(status_code=400, detail="URL invalide")

    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        full_text = " ".join([entry["text"] for entry in transcript_list])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur transcript : {str(e)}")

    try:
        prompt = f"Résume cette vidéo en français de façon concise :\n{full_text}"
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )
        summary = response.choices[0].message.content.strip()
        return {"résumé": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur GPT : {str(e)}")
