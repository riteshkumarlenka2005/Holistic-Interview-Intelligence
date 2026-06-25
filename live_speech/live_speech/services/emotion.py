from transformers import pipeline

classifier = None

def load_emotion_model():
    global classifier
    if classifier is None:
        classifier = pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            return_all_scores=True
        )

def analyze_emotion(text: str):
    if classifier is None:
        load_emotion_model()
    return classifier(text)
