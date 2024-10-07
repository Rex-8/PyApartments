from os import listdir


# get asset function
def getAsset(type, filename):
    # gets required asset from the given type and filename in the assets folder

    return f'assets/{type}s/{[f for f in listdir(f"assets/{type}s/") if f.startswith(filename)][0]}'
