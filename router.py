# ================================
# 🧭 ROUTER CONFIG
# ================================

ssROUTES = {
    -1003728548283: ["sofa"],
    
}

# ================================
# 🔍 MATCH FUNCTION
# ================================

def match(tag, hashtags):
    """
    Fuzzy match:
    tag = "rug"
    hashtag = "rugs" / "rugdesign"
    """
    tag = tag.lower()
    return any(tag in h or h in tag for h in hashtags)


# ================================
# 🎯 DESTINATION FINDER
# ================================

def get_destinations(hashtags):
    """
    Returns list of destination channel IDs
    based on matching hashtags
    """

    # normalize hashtags
    hashtags = [h.lower().replace("_", "") for h in hashtags]

    results = []

    for dest, tags in ROUTES.items():

        matched = False

        for group in tags:

            # multi-condition group (e.g. ["track","light"])
            if isinstance(group, list):
                if all(match(g, hashtags) for g in group):
                    matched = True
                    break

            # single tag
            else:
                if match(group, hashtags):
                    matched = True
                    break

        if matched:
            results.append(dest)

    return results
