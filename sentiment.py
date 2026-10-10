
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)





app = FastAPI()

class SentimentRequest(BaseModel):
    sentences: List[str]

def classify(sentence):
    text = sentence.lower()

    happy_words = ["love", "happy", "great", "excellent", "good", "wonderful", "amazing", "enjoy"]
    sad_words = ["sad", "terrible", "hate", "bad", "awful", "angry", "disappointed", "worst"]

    happy = sum(word in text for word in happy_words)
    sad = sum(word in text for word in sad_words)

    if happy > sad:
        return "happy"
    elif sad > happy:
        return "sad"
    return "neutral"

@app.post("/sentiment")
def sentiment(request: SentimentRequest):
    return {
        "results": [
            {
                "sentence": sentence,
                "sentiment": classify(sentence)
            }
            for sentence in request.sentences
        ]
    }

