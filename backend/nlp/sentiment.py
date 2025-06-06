from transformers import pipeline

# 💡  Siebert model is compact and performs well on short text
_classifier = pipeline(
    task="sentiment-analysis",
    model="siebert/sentiment-roberta-large",
    top_k=None,            
)

def classify(text: str) -> str:
    """
    >>> classify("I'm happy")
    'positive'
    >>> classify("So-so day.")
    'neutral'
    """
    if not text.strip():
        return "neutral"
    out = _classifier(text[:512])[0]     # {'label': 'POSITIVE', 'score': 0.98}
    # Treat low-confidence outputs as neutral
    return out["label"].lower() if out["score"] >= 0.6 else "neutral"