from celery import Celery
import swiftutil
import tweetutil

app = Celery('tasks', backend='amqp', broker='amqp://')

@app.task(ignore_result=True)
def print_hello():
    print 'hello there'

@app.task
def gen_prime(x):
    multiples = []
    results = []
    for i in xrange(2, x+1):
        if i not in multiples:
            results.append(i)
            for j in xrange(i*i, x+1, i):
                multiples.append(j)
    return results

@app.task
def count_pronouns(filename, bucketname="tweets"):
    sc = swiftutil.getswiftconnection()
    result = tweetutil.countpronounsintweetfile(swiftutil.bucketfilelinegen(sc, bucketname, filename))
    sc.close()
    return result
