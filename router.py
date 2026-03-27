from config import ROUTES

def get_destinations(tags):
    destinations = []

    for dest, route_tags in ROUTES.items():
        for tag in tags:
            if tag in route_tags:
                destinations.append(dest)
                break

    return destinations
