
import re
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class SentimentRequest(BaseModel):
    sentences: List[str]


POSITIVE = set("""
happy happiness love loved lovely loving like liked enjoy enjoyed
excellent amazing awesome wonderful fantastic great good best brilliant
beautiful perfect superb fabulous delighted pleased excited thrilled
glad joyful cheerful satisfied impressive nice fun funny helpful
recommend favorite positive success successful win winning appreciate
grateful optimistic outstanding cool sweet adorable magnificent
incredible phenomenal pleasant exciting valuable impressive
""".split())

NEGATIVE = set("""
sad sadness unhappy hate hated dislike awful terrible horrible worst
bad poor disappointing disappointed angry upset miserable depressed
annoying annoying frustrating frustrated boring dull disgusting ugly
fail failed failure lose losing broken useless pathetic rude regret
pain painful problem trouble difficult negative sick tired scared
afraid worried anxious nervous unfortunate unpleasant nasty disaster
inferior mediocre irritating irritatingly sucks sucks
""".split())

POSITIVE_PHRASES = [
    "looking forward to", "can't wait", "cannot wait",
    "well done", "highly recommend", "works perfectly",
    "exceeded expectations", "out of this world",
    "thank you", "thanks a lot", "feel better",
    "love it", "enjoyed it", "good job", "no problem",
]

NEGATIVE_PHRASES = [
    "fed up", "not worth it", "waste of time",
    "waste of money", "doesn't work", "does not work",
    "didn't work", "not working", "never works",
    "very disappointed", "extremely disappointed",
    "feel terrible", "feel awful", "hate it",
    "can't stand", "cannot stand", "not satisfied",
]

NEGATIONS = {
    "not", "no", "never", "neither", "nor", "hardly",
    "barely", "isn't", "wasn't", "weren't", "don't",
    "doesn't", "didn't", "can't", "cannot", "couldn't",
    "wouldn't", "shouldn't", "won't", "without"
}

INTENSIFIERS = {
    "very", "really", "extremely", "absolutely", "incredibly",
    "so", "too", "highly", "deeply", "super"
}

def classify(sentence: str) -> str:
    text = sentence.lower().replace("’", "'")

    # Count sentiment-bearing phrases first.
    score = 0
    for phrase in POSITIVE_PHRASES:
        if phrase in text:
            score += 2

    for phrase in NEGATIVE_PHRASES:
        if phrase in text:
            score -= 2

    # Tokenize words and common contractions.
    words = re.findall(r"[a-z]+(?:'[a-z]+)?", text)

    for i, word in enumerate(words):
        # Skip words already accounted for as phrases only indirectly;
        # word-level evidence still helps with mixed sentences.
        base = 0

        if word in POSITIVE:
            base = 1
        elif word in NEGATIVE:
            base = -1
        else:
            continue

        # Check for a negation in the previous three words.
        previous = words[max(0, i - 3):i]
        negated = any(w in NEGATIONS for w in previous)

        # Negated positive words count against positivity;
        # negated negative words reduce negativity.
        if negated:
            base *= -1

        # Intensifiers strengthen the sentiment.
        if any(w in INTENSIFIERS for w in previous):
            base *= 1.5

        score += base

    if score > 0.5:
        return "happy"
    if score < -0.5:
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


@app.get("/")
def root():
    return {"message": "Sentiment API is running"}
