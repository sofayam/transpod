import datetime
import requests
import os.path

def nth_sunday(year, n):
    first_day = datetime.date(year, 1, 1)
    # Find the first Monday of the year
    first_sunday = first_day + datetime.timedelta(days=(6 - first_day.weekday()) % 7)
    # Add (n-1) weeks to get the nth Monday
    nth_sunday = first_sunday + datetime.timedelta(weeks=n-1)
    return nth_sunday.strftime('%Y%m%d')


def trendurl(dstr):
    return "http://www.c-radio.net/" + dstr + "/trend_" + dstr + "_1.mp3"




def geturl(media_url, file_path):
    if os.path.exists(file_path):
        print (f"Already got {file_path}")
    else: 
        print(f"Downloading: {media_url}")
        response = requests.get(media_url, stream=True)

        if response.status_code == 200:
            with open(file_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
                print(f"Downloaded: {file_path}")
        else:
            print(f"Failed to download the episode. HTTP Status Code: {response.status_code}")

def saveurl(year, n):
    dstr = nth_sunday(year, n)
    url = trendurl(dstr)
    filePath = f"トレンドウォッチ_{dstr}.mp3"
    geturl(url, filePath)

def testmonth(year):
    dstrbase = year + "12"
    for i in range (1,31):
        dstr = dstrbase + f"{i:02d}"
        url = trendurl(dstr)
        geturl(url, dstr + ".mp3")


def grabAll():
    for year in range(2011,2012):
        for i in range(1, 52):
            saveurl(year, i)


testmonth("2011")

# grabAll()
