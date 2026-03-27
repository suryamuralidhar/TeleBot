# ================================
# 🧭 ROUTER CONFIG
# ================================

dROUTES = {
    -1003835504670: ["rug"],
    -1003757370342: ["fabric"],
    -1003754983761: ["decor"],
    -1003827068085: ["sofa"],
    -1003772273357: ["lamp", "light", "lighting"],
    -1003691605172: [["pendent", "light"], "chandelier"],
    -1003557082671: ["table"],
    -1003752015548: ["vase", "flower"],
    -1003809497514: ["armchair", "chair"],
    -1003858996511: ["carpet"],
    -1003794820459: ["bed", "matress"],
    -1003815972764: ["plant", "plants", "bush", "shrubs"],
    -1003861364666: ["grass"],
    -1003891088964: ["tree", "trees", "palm"],
    -1003718603443: ["water", "liquid"],
    -1003319756110: ["metal"],
    -1003751276058: ["window", "windows", "frame"],
    -1003537174392: ["door", "doors"],
    -1003514048910: ["curtain", "curtains"],
    -1003606126385: ["car", "suv", "sedan", "pickup"],
    -1003779084703: ["marble"],
    -1003750864556: ["kitchen"],
    -1003727774043: ["bathroom", "toilet", "restroom"],
    -1003740796851: ["washbasin"],
    -1003773698730: ["sink"],
    -1003566977180: ["shower"],
    -1003707812721: ["faucet", "tap", "mixer"],
    -1003780728078: ["wc"],
    -1003886868767: [["track", "light"]],
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
