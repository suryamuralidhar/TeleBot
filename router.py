ROUTES = {
    -1003835504670: ["rug"],
    -1003757370342: ["fabric"],
}

def match(tags, hashtags):
    return any(tag in h or h in tag for h in hashtags)

def get_destinations(hashtags):
    results = []

    for dest, tags in ROUTES.items():
        for tag in tags:
            if match(tag, hashtags):
                results.append(dest)
                break

    return results