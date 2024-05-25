#!/usr/bin/env python3
#
# Although the above shebang line exists, you should probably run it in a
# production environment with something like gunicorn or uwsgi.
#
# SPDX-License-Identifier: AGPL-3.0-only
# https://git.runxiyu.org/runxiyu/current/hybrid.git
#


from flask import Flask, render_template, request, redirect, abort
from flask.wrappers import Response
import time, os, random, shutil

app = Flask(__name__)

VERSION = """hybrid v0.1

License: GNU Affero General Public License v3.0 only
URL: https://git.runxiyu.org/runxiyu/current/hybrid.git"""

# REMEMBER: You can only listen inside /hybrid/. Everything outside is
#           supposed to be static.


@app.route("/hybrid/", methods=["GET"])
def index():
    return Response("No endpoint specified!", mimetype="text/plain")


@app.route("/hybrid/version", methods=["GET"])
def version():
    return Response(VERSION, mimetype="text/plain")


@app.route("/hybrid/test/post", methods=["GET", "POST"])
def test_post():
    ts = int(time.time())
    r = random.randint(0, 10000)
    with open("/tmp/post_%d_%d" % (ts, r), "wb") as fd:
        fd.write(request.stream.read())
    return Response("/tmp/post_%d_%d" % (ts, r), mimetype="text/plain")


@app.route("/hybrid/github", methods=["GET", "POST"])
def github():
    ts = int(time.time())
    r = random.randint(0, 10000)
    with open("/tmp/github_%d_%d" % (ts, r), "wb") as fd:
        shutil.copyfileobj(request.stream, fd)
    return Response("/tmp/github_%d_%d" % (ts, r), mimetype="text/plain")


if __name__ == "__main__":
    app.run(port=8082)
