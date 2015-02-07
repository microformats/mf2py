from __future__ import print_function
import os
from mf2py import Parser
from flask import Flask, Response, request

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    resp = """<!DOCTYPE HTML>
    <html><head><title>mf2py</title></head>
    <body><form action="/parse" method="get">
    <h1>mf2py test</h1>
    URL: <input type="text" name="url" /> <input type="submit" /></body></html>
    """
    return Response(resp, status=200, mimetype="text/html")


@app.route("/parse", methods=["GET", "POST"])
def parse():
    if request.method == 'GET':
        u = request.args['url']
    else:
        u = request.form['url']
    print(u)
    p = Parser(url=unicode(u))
    return Response(p.to_json(pretty_print=True), status=200,
                    mimetype='application/json')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 33507)))
