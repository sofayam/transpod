from bs4 import BeautifulSoup, SoupStrainer
import requests
import time


base = "https://dharmaseed.org"

text = open("jhanna.html").read()

urls = []

for link in BeautifulSoup(text, 'html.parser', parse_only=SoupStrainer('a')):
    if link.has_attr('href'):
        if 'GAIA' in link['href']:
            urls.append(link['href'])

for url in urls:
    full = base + url

    # grab the url
    print("loading ", full)
    r = requests.get(full)
    fname = url.split("/")[-1]
    open (fname, "wb").write(r.content)
    #pause for a 10 seconds

    time.sleep(10)
    