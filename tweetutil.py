import re
import json

pronounregex = re.compile(r'^(han|hon|den|det|denna|denne|hen)$')

def countpronouns(jsontweet, pcountdict):
    tweetdict = json.loads(jsontweet)
    tweettext = tweetdict["text"]
    pronounlist = filter(pronounregex.match, tweettext.lower().split(' '))
    for w in pronounlist:
        pcountdict[w]+=1