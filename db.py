saved_files = {}

def is_duplicate(dest, filename):
    return dest in saved_files and filename in saved_files[dest]

def save(dest, filename):
    if dest not in saved_files:
        saved_files[dest] = set()
    saved_files[dest].add(filename)