# ai/preprocess.py
import re, string, emoji, nltk
from nltk.corpus import stopwords

nltk.download("stopwords", quiet=True)
STOP = set(stopwords.words("english"))

def clean(text: str) -> str:
    """Basic Twitter / Reddit style cleaning."""
    text = emoji.replace_emoji(text, replace='')
    text = re.sub(r"http\S+", "", text)                 # strip URLs
    text = text.translate(str.maketrans('', '', string.punctuation))
    toks = [t.lower() for t in text.split() if t.lower() not in STOP]
    return " ".join(toks)
