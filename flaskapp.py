#!flask/bin/python
from flask import Flask, jsonify
import sys
import swiftutil
import celerytasks
import time
import json

flask = Flask(__name__)

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
    flask.run(host='0.0.0.0',debug=True)
