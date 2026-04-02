from transformers import pipeline
#pipeline is a helper that lets you use a pretrained model without dealing with the low-level details

#store loaded model here once it has been loaded for the first time 
_sentiment_pipeline = None

def get_sentiment_pipeline():
    global _sentiment_pipeline

    # only load the model if it hasn't been loaded yet
    if _sentiment_pipeline is None:
        _sentiment_pipeline = pipeline(
            "sentiment-analysis", # the task we want to perform
            model="distilbert-base-uncased-finetuned-sst-2-english"
            # the specific pretrained model to use
        )

    # return loaded model
    return _sentiment_pipeline

def analyze_sentiment(text: str) -> dict:
    """
    Returns a dict with:
      - label: 'POSITIVE' or 'NEGATIVE'
      - score: confidence float 0-1
      - tone_hint: plain English string to inject into system prompt
    """
    pipe = get_sentiment_pipeline() #get the model
    result = pipe(text[:512])[0]    #truncate to model's max input

    label = result["label"] # 'POSITIVE' or 'NEGATIVE'
    score = result["score"] # confidence score between 0 and 1

    # Based on the label and confidence score, write a human-readable tone instruction
    if label == "NEGATIVE" and score > 0.90:
        tone_hint = "The patient appears frustrated or upset. Respond with extra empathy and patience."
    elif label == "NEGATIVE":
        tone_hint = "The patient may be concerned or anxious. Use a calm, reassuring tone."
    else:
        tone_hint = "The patient seems calm. Respond in a clear, professional tone."

    # Return all three values as a dictionary
    return {"label": label, "score": round(score, 4), "tone_hint": tone_hint}