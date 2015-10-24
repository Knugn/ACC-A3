import re
import json
import timeit

pronounlist = ['han', 'hon', 'den', 'det', 'denna', 'denne', 'hen']
pronounregex = re.compile(r'^(han|hon|den|det|denna|denne|hen)$')

def countpronouns(jsontweet, pcountdict, ignoreretweets = True):
    tweetdict = json.loads(jsontweet)
    tweettext = tweetdict["text"]
    if ignoreretweets and tweettext.startswith('RT'):
        return 0
    pronounlist = filter(pronounregex.match, tweettext.lower().split())
    for w in pronounlist:
        pcountdict[w]+=1
    return 1

def countpronounsintweetfile(linegen, ignoreretweets = True):
    t1 = timeit.default_timer()
    pcountdict = {}
    for p in pronounlist:
        pcountdict[p] = 0
    linecount = 0
    tweetcount = 0
    for line in linegen:
        linecount += 1
        if (linecount % 2 == 0):
            assert(line == '')
            continue
        tweetcount += countpronouns(line, pcountdict, ignoreretweets)
    t2 = timeit.default_timer()
    dt = t2-t1
    return {'line_count':linecount, 
            'ignore_retweets':ignoreretweets, 
            'tweet_count':tweetcount, 
            'pronoun_counts':pcountdict,
            'computation_time':dt
           }
