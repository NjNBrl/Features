from transformers import pipeline, AutoTokenizer
import re
import os

def preprocess_lyrics(lyrics):
    """Lowercase, remove punctuation, and clean extra spaces."""
    lyrics = lyrics.lower()
    lyrics = re.sub(r'[^\w\s]', '', lyrics)
    lyrics = re.sub(r'\s+', ' ', lyrics).strip()
    return lyrics

def chunk_by_tokens(text, tokenizer, max_tokens=512):
    """
    Split text into chunks based on token length.
    Keeps chunks <= max_tokens for model compatibility.
    """
    tokens = tokenizer.encode(text, add_special_tokens=False)
    for i in range(0, len(tokens), max_tokens):
        # Decode back to text for the classifier
        yield tokenizer.decode(tokens[i:i + max_tokens])

def detect_emotion_from_text(lyrics, classifier, tokenizer):
    """Detect dominant emotion from lyrics using token-based chunking."""
    lyrics = preprocess_lyrics(lyrics)
    chunk_results = []
    
    # Use 510 instead of 512 to leave space for special tokens
    for chunk in chunk_by_tokens(lyrics, tokenizer, max_tokens=510):
        results = classifier(chunk, truncation=True, max_length=512)[0]
        top_emotion = max(results, key=lambda x: x["score"])
        chunk_results.append(top_emotion)

    # Aggregate scores from all chunks
    emotion_scores = {}
    for res in chunk_results:
        emotion_scores[res["label"]] = emotion_scores.get(res["label"], 0) + res["score"]

    final_emotion = max(emotion_scores, key=emotion_scores.get)
    avg_score = emotion_scores[final_emotion] / len(chunk_results)
    return final_emotion, avg_score

def main():
    lyrics_folder = "4A.lyrics"
    output_folder = "5A.lyrics_emotion"
    os.makedirs(output_folder, exist_ok=True)

    # Load tokenizer & classifier
    model_name = "bhadresh-savani/distilbert-base-uncased-emotion"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    classifier = pipeline(
        "text-classification",
        model=model_name,
        top_k=None
    )

    for filename in os.listdir(lyrics_folder):
        if filename.lower().endswith(".txt"):
            path = os.path.join(lyrics_folder, filename)
            with open(path, "r", encoding="utf-8") as f:
                lyrics = f.read()

            emotion, score = detect_emotion_from_text(lyrics, classifier, tokenizer)

            print(f"Processed {filename} => Emotion: {emotion} (Confidence: {score:.2f})")

            # Save result
            base_name = os.path.splitext(filename)[0]
            out_name = f"{base_name}_emotion.txt"
            out_path = os.path.join(output_folder, out_name)

            with open(out_path, "w", encoding="utf-8") as f_out:
                f_out.write(f"Emotion: {emotion}\nConfidence: {score:.2f}")

            print(f"Saved emotion result to {out_path}")

if __name__ == "__main__":
    main()

