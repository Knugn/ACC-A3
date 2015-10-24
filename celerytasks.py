from celeryapp import celery
import swiftutil
import tweetutil

sc = swiftutil.getswiftconnection()

@celery.task(ignore_result=True)
def print_hello():
    print 'hello there'

@celery.task
def gen_prime(x):
    multiples = []
    results = []
    for i in xrange(2, x+1):
        if i not in multiples:
            results.append(i)
            for j in xrange(i*i, x+1, i):
                multiples.append(j)
    return results

@celery.task
def count_pronouns(file_name, bucket_name="tweets"):
    global sc 
    result = tweetutil.countpronounsintweetfile(swiftutil.bucketfilelinegen(sc, bucket_name, file_name))
    result['file'] = bucket_name+"/"+file_name
#    sc.close()
    return result
