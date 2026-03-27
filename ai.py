def extract_tags(text):
    words = text.lower().split()
    return [w.replace("#", "") for w in words if w.startswith("#")]
