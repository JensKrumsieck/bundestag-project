import os


def ensure_path(path:str):   
    if not os.path.exists(path):
        os.mkdir(path)

def remove_duplicates(list:list):
    seen = set()
    for item in list :
        if item not in seen:
            seen.add(item)
    return seen
