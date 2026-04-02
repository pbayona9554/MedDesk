from transformers import pipeline

_intent_pipeline = None

def get_intent_pipeline():
    global _intent_pipeline
    
    # only load the model if it hasn't been loaded yet
    if _intent_pipeline is None:
        _intent_pipeline = pipeline(
            "zero-shot-classification",       # task type
            model="facebook/bart-large-mnli"  # BART model
        )
    
    return _intent_pipeline

def classify_intent(text: str) -> dict:
    """
    Takes the patient's message and classifies it into one of four intent categories.
    Returns a dict with:
      - intent: the top predicted category
      - score: confidence float 0-1
      - intent_hint: focused instruction to inject into Claude's system prompt
    """
    
    # the categories we want to classify into
    candidate_labels = ["billing", "coverage", "escalation", "general"]
    
    pipe = get_intent_pipeline()
    
    # scores the text against every label and ranks them
    result = pipe(text[:512], candidate_labels)
    
    # top result is the first item in the scores list
    intent = result["labels"][0]       # highest scoring label
    score = result["scores"][0]        # confidence for that label

    # map each intent to a focused instruction for Claude
    intent_hints = {
        "billing": (
            "This patient is asking about a bill, charge, or payment. "
            "Focus on explaining costs clearly, reference their deductible status, "
            "and provide the correct billing contact if needed."
        ),
        "coverage": (
            "This patient is asking about what is or isn't covered by their plan. "
            "Be specific about their plan type and coverage percentages from the policy document."
        ),
        "escalation": (
            "This patient wants to speak to a human or is expressing serious frustration. "
            "Acknowledge their concern immediately and follow escalation procedures."
        ),
        "general": (
            "This patient has a general question. "
            "Answer clearly and concisely using only information from the policy document."
        ),
    }

    intent_hint = intent_hints[intent]

    return {"intent": intent, "score": round(score, 4), "intent_hint": intent_hint}
