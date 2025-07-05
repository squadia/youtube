from fastapi import FastAPI
from pydantic import BaseModel
import yt_dlp
import whisper
import openai
import os
import tempfile

# Clé OpenAI (à remplacer ou à mettre dans les variables d'environnement Render)
openai.api_key = os.getenv("OPENAI_API_KEY", "ta_cle_openai_ici")

app = FastAPI()

class VideoInput(BaseModel):
    url: str

@app.get("/")
def home():
    return {"message": "API YouTube opérationnelle"}

@app.post("/analyser")
def analyser_video(input: VideoInput):
    url = input.url

    # Créer un dossier temporaire pour stocker le fichier audio
    with tempfile.TemporaryDirectory() as tmpdir:
        audio_path = os.path.join(tmpdir, "audio.mp3")

        # Télécharger l'audio avec yt-dlp
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': audio_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Transcrire avec Whisper
        model = whisper.load_model("base")  # tu peux mettre "small", "medium", "large"
        result = model.transcribe(audio_path)
        transcription = result["text"]

        # Résumer avec GPT
        prompt = f"""Voici une transcription d'une vidéo YouTube :

{transcription}

Fais un résumé structuré et concis en 5 bullet points maximum. Mets en valeur les infos utiles pour quelqu'un qui n'a pas le temps de tout écouter."""
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )

        summary = response["choices"][0]["message"]["content"]

    return {
        "url": url,
        "résumé": summary
    }

