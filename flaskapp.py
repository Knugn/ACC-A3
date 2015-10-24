#!flask/bin/python
from flask import Flask, jsonify, url_for
import sys
import swiftutil
from celeryapp import celery
from celery import group
import celerytasks
import time
import json
import timeit
from collections import Counter
from operator import add

flask = Flask(__name__)
sc = swiftutil.getswiftconnection()

def setupcontexttask(flaskapp, celeryapp):
    TaskBase = celeryapp.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with flaskapp.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celeryapp.Task = ContextTask
    return

@flask.route('/')
def index():
    return 'Index Page'

@flask.route('/about')
def about():
    return 'This site provides a web service to count swedish pronouns in tweets.'

@flask.route('/count_pronouns')
def count_pronouns_usage():
    return {
        #'Count pronouns in all files in default bucket' : url_for(count_pronouns()),
        'Count pronouns in file \'tweets/tweets_0.txt\' bucket' : url_for(count_pronouns('tweets','tweets_0.txt')),
        }

@flask.route('/count_pronouns/')
@flask.route('/count_pronouns//<file_name>')
@flask.route('/count_pronouns/<bucket_name>/')
@flask.route('/count_pronouns/<bucket_name>/<file_name>')
def count_pronouns(bucket_name='tweets', file_name=None):
    #global sc
    if not bucket_name:
        return 'Must specify a bucket.'
    if not file_name:
        return jsonify(count_pronouns_in_bucket(bucket_name))
    return jsonify(count_pronouns_in_bucket_file(bucket_name, file_name))
    
    #return json.dumps(pcountresults)

def count_pronouns_in_bucket(bucket_name):
    t1 = timeit.default_timer()
    global sc
    (resp_header, obj_list) = sc.get_container(bucket_name)
    taskgroup = group(celerytasks.count_pronouns.s(obj['name'], bucket_name) for obj in obj_list)()
    partialresults = taskgroup.get()
    return {
        'combined_results': {
            'bucket':bucket_name,
            'pronoun_counts':dict(reduce(lambda c, pc: c.update(pc) or c, (Counter(pr['pronoun_counts']) for pr in partialresults))),
            'computation_time':reduce(add, (pr['computation_time'] for pr in partialresults)),
            'line_count':reduce(add, (pr['line_count'] for pr in partialresults)),
            'tweet_count':reduce(add, (pr['tweet_count'] for pr in partialresults))
            },
        'partial_results':partialresults,
        'real_time_taken':timeit.default_timer()-t1
    }

#    pcounttasks = {}
#    for obj in obj_list:
#        filename = obj['name']
#        pcounttasks[filename] = (celerytasks.count_pronouns.delay(filename))
#    pcountresults = {}
#    for pctKey, pctVal in pcounttasks.iteritems():
#        while not pctVal.ready():
#            time.sleep(1)
#        pcountresults[pctKey] = pctVal.get()
#    return pcountresults

def count_pronouns_in_bucket_file(bucket_name, file_name):
    #task = celerytasks.count_pronouns.delay(file_name, bucket_name)
    task = celerytasks.count_pronouns.apply_async([file_name, bucket_name])
    return task.wait()

@flask.route('/pronouncount/api/', methods=['GET'])
def pronoun_count():
    global sc
    #sc = swiftutil.getswiftconnection()
    (resp_header, obj_list) = sc.get_container("tweets")
    pcounttasks = {}
    for obj in obj_list:
        filename = obj['name']
        pcounttasks[filename] = (celerytasks.count_pronouns.delay(filename))
    pcountresults = {}
    for pctKey, pctVal in pcounttasks.iteritems():
        while not pctVal.ready():
            time.sleep(1)
        pcountresults[pctKey] = pctVal.get()
    #sc.close()
    return json.dumps(pcountresults)

if __name__ == '__main__':
    setupcontexttask(flask, celery)
    flask.run(host='0.0.0.0',debug=True)
