import json
import os

def getConfig(feedfolder: str):
    configPath = feedfolder + "/_config.md"
    if os.path.exists(configPath):
        configStr: str = open(configPath).read()
        config = json.loads(configStr)
        return config
    else:
        return {}

if __name__ == "__main__":
    ff = "./content/teppei"
    print(getConfig(ff))

