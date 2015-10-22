#!flask/bin/python
from flask import Flask, jsonify
import sys
import swiftutil
from celeryapp import celery
import celerytasks
import time
import json

flask = Flask(__name__)

def setupcontexttask(celery):
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return

@flask.route('/pronouncount/api/', methods=['GET'])
def pronoun_count():
    sc = swiftutil.getswiftconnection()
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
    sc.close()
    return json.dumps(pcountresults)

if __name__ == '__main__':
    setupcontexttask(celery)
    flask.run(host='0.0.0.0',debug=True)
