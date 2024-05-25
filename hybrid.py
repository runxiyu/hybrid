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
import time, os, random, shutil, hashlib, hmac, json

app = Flask(__name__)

VERSION = """hybrid v0.1

License: GNU Affero General Public License v3.0 only
URL: https://git.runxiyu.org/runxiyu/current/hybrid.git"""

with open("/srv/hybrid/github_webhook_secret.txt", "r") as fd:
    GITHUB_WEBHOOK_SECRET = fd.readline().strip()

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


def verify_github_webhook_signature(payload_body, secret_token, signature_header) -> bool:
    if not signature_header:
        return False
    hash_object = hmac.new(secret_token.encode('utf-8'), msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + hash_object.hexdigest()
    if hmac.compare_digest(expected_signature, signature_header):
        return True
    return False

@app.route("/hybrid/github", methods=["POST"])
def github():
    data = json.loads(request.data)
    data["X-runxiyu-GitHub-Signature-Validation"] = bool(verify_github_webhook_signature(data, GITHUB_WEBHOOK_SECRET, request.headers.get("X-Hub-Signature-256", "")))
    with open("/srv/hybrid/github-results.json", "w") as fd:
        json.dump(data, fd, indent="\t")

if __name__ == "__main__":
    app.run(port=8082)
