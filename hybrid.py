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
import time, os
app = Flask(__name__)

VERSION = """hybrid v0.1

License: GNU Affero General Public License v3.0 only
URL: https://git.runxiyu.org/runxiyu/current/hybrid.git"""

# REMEMBER: You can only listen inside /hybrid/. Everything outside is
#           supposed to be static.

@app.route('/hybrid/', methods=['GET'])
def index():
    return Response("No endpoint specified!", mimetype="text/plain")

@app.route('/hybrid/version', methods=['GET'])
def version():
    return Response(VERSION, mimetype="text/plain")

if __name__ == "__main__":
    app.run(port=8080)
