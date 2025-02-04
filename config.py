import json

def getConfig(feedfolder: str):
    configStr: str = open(feedfolder + "/_config.md").read()
    config = json.loads(configStr)
    return config

if __name__ == "__main__":
    ff = "./content/teppei"
    print(getConfig(ff))

