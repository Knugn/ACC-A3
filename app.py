#!flask/bin/python
from flask import Flask, jsonify
#import subprocess
import sys
import swiftutil
import tasks
import time

app = Flask(__name__)

@app.route('/pronouncount/api/', methods=['GET'])
def pronoun_count():
    #data=subprocess.check_output(["cowsay","Hello student"])
    sc = swiftutil.getswiftconnection()
    (resp_header, obj_list) = sc.get_container("tweets")
    pcounttasks = {}
    for obj in obj_list:
        filename = obj['name']
        pcounttasks[filename] = (tasks.count_pronouns.delay(filename))
    pcountresults = 
    for pctEntry in pcounttasks:
        while !pctEntry.value.ready():
            time.sleep(1)
        pcountresults[pctEntry.key] = pctEntry.value.get()
    sc.close()
    return pcountresults

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
