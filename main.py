from fastapi import FastAPI, Request
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

class VideoURL(BaseModel):
    url: str

def extract_video_id(youtube_url: str) -> str:
    """
    Extrait l’ID d’une vidéo YouTube depuis une URL standard.
    """
    from urllib.parse import urlparse, parse_qs
    parsed_url = urlparse(youtube_url)
    query_params = parse_qs(parsed_url.query)
    return query_params.get("v", [None])[0]

@app.post("/analyser")
async def analyser_video(data: VideoURL):
    video_id = extract_video_id(data.url)
    if not video_id:
        return {"error": "Impossible d’extraire l’ID de la vidéo"}

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['fr', 'en'])
        full_text = " ".join([entry['text'] for entry in transcript])

        prompt = f"Voici le transcript d’une vidéo YouTube :\n{full_text}\n\nFais-moi un résumé clair et structuré, comme un article de blog avec les grandes idées."
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        summary = response.choices[0].message.content.strip()

        return {"summary": summary}

    except Exception as e:
        return {"error": str(e)}
