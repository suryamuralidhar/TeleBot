def auto_tags(text):
    text = (text or "").lower()

    tags = []

    if "sofa" in text:
        tags.append("sofa")
    if "rug" in text or "carpet" in text:
        tags.append("rug")
    if "light" in text:
        tags.append("light")
    if "table" in text:
        tags.append("table")

    return tags