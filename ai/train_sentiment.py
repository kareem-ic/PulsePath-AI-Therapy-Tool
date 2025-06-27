# ai/train_sentiment.py
import pandas as pd, joblib, tensorflow as tf
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from preprocess import clean                       # <── import the helper

# 1. load + clean
df = pd.read_csv("combined.csv")                   # CSV with 2 cols: text,label
df["text"] = df["text"].apply(clean)

df.rename(columns={"target": "label"}, inplace=True)

# 2. tokenize
tok = Tokenizer(num_words=12000, oov_token="<UNK>")
tok.fit_on_texts(df.text)
X = pad_sequences(tok.texts_to_sequences(df.text), maxlen=120)

# 3. label-encode
enc = LabelEncoder().fit(df.label)                 # labels: happy / sad / neutral
y  = tf.keras.utils.to_categorical(enc.transform(df.label))

# 4. simple Bi-LSTM
model = tf.keras.Sequential([
    tf.keras.layers.Embedding(12000, 128, input_length=120),
    tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(64)),
    tf.keras.layers.Dense(3, activation="softmax")
])
model.compile("adam", "categorical_crossentropy", metrics=["accuracy"])
model.fit(X, y, epochs=6, batch_size=64, validation_split=0.1)

# 5. save artefacts
model.save("model/sentiment.h5")
joblib.dump(tok, "model/tokenizer.joblib")
joblib.dump(enc, "model/label_encoder.joblib")
print("✓ trained & saved to ai/model/")
