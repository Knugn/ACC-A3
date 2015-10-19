#!flask/bin/python
from flask import Flask, jsonify
import subprocess
import sys

app = Flask(__name__)

@app.route('/pronouncount/api/', methods=['GET'])
def cow_say():
    #data=subprocess.check_output(["cowsay","Hello student"])
    return data

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
