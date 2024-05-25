#!/usr/bin/env python3
#
# Although the above shebang line exists, you should probably run it in a
# production environment with something like gunicorn or uwsgi.
#
# SPDX-License-Identifier: AGPL-3.0-only
# https://git.runxiyu.org/runxiyu/current/hybrid.git
#


import flask
import werkzeug
import time
import os
import random
import shutil
import hashlib
import hmac
import json
import requests
import subprocess
import tempfile
import typing

response_t: typing.TypeAlias = typing.Union[werkzeug.Response, flask.Response, str]

app = flask.Flask(__name__)

VERSION = """hybrid v0.1

License: GNU Affero General Public License v3.0 only
URL: https://git.runxiyu.org/runxiyu/current/hybrid.git"""

with open("/srv/hybrid/github_webhook_secret.txt", "r") as fd:
    GITHUB_WEBHOOK_SECRET = fd.readline().strip()


FROM_ADDRESS_WITH_NAME = "Hybrid <hybrid@runxiyu.org>"
FROM_ADDRESS = "hybrid@runxiyu.org"
REPLY_TO = "me@runxiyu.org"

REPO_MAPPER = {
    "runxiyu/sjdb-src": "~runxiyu/sjdb@lists.sr.ht",
    "runxiyu/ykps-wsgi": "~runxiyu/ykps@lists.sr.ht",
}

def repo_addr(repo: str) -> str:
    if (addr := REPO_MAPPER.get(repo, None)):
        return addr
    else:
        return "me@runxiyu.org"


# REMEMBER: You can only listen inside /hybrid/. Everything outside is
#           supposed to be static.


@app.route("/hybrid/", methods=["GET"])
def index() -> response_t:
    return flask.Response("No endpoint specified!", mimetype="text/plain")


@app.route("/hybrid/version", methods=["GET"])
def version() -> response_t:
    return flask.Response(VERSION, mimetype="text/plain")


@app.route("/hybrid/test/post", methods=["GET", "POST"])
def test_post() -> response_t:
    ts = int(time.time())
    r = random.randint(0, 10000)
    with open("/tmp/post_%d_%d" % (ts, r), "wb") as fd:
        fd.write(flask.request.stream.read())
    return flask.Response("/tmp/post_%d_%d" % (ts, r), mimetype="text/plain")


def verify_github_webhook_signature(
    payload_body: bytes, secret_token: str, signature_header: str
) -> bool:
    if not signature_header:
        return False
    hash_object = hmac.new(
        secret_token.encode("utf-8"), msg=payload_body, digestmod=hashlib.sha256
    )
    expected_signature = "sha256=" + hash_object.hexdigest()
    if hmac.compare_digest(expected_signature, signature_header):
        return True
    return False


@app.route("/hybrid/github", methods=["POST"])
def github() -> response_t:
    raw_data = flask.request.data
    if not verify_github_webhook_signature(
        raw_data,
        GITHUB_WEBHOOK_SECRET,
        flask.request.headers.get("X-Hub-Signature-256", ""),
    ):
        return flask.Response(None, status=403)
    jq = json.loads(raw_data)
    if jq["action"] != "opened":
        return flask.Response(None, status=200)
    to_address = repo_addr(jq["repository"]["full_name"])
    with tempfile.NamedTemporaryFile(delete=True) as fd:
        with requests.get(
            jq["pull_request"]["patch_url"],
            headers={"Accept-Encoding": "identity"},
            stream=True,
        ) as r:
            shutil.copyfileobj(r.raw, fd)
        fd.flush()
        proc = subprocess.run(
            [
                "git",
                "send-email",
                "--from",
                FROM_ADDRESS_WITH_NAME,
                "--8bit-encoding",
                "UTF-8",
                "--to",
                to_address,
                "--confirm",
                "never",
                # "--suppress-cc",
                # "all",
                "--reply-to",
                REPLY_TO,
                "--envelope-sender",
                FROM_ADDRESS,
                "--no-smtp-auth",
                "--smtp-server",
                "localhost",
                "--smtp-server-port",
                "25",
                fd.name,
            ],
            capture_output=True,
        )
        try:
            proc.check_returncode()
        except subprocess.CalledProcessError:
            return flask.Response(
                proc.stderr,
                status="500",
                mimetype="text/plain",
            )
    return flask.Response(None, status=204)


if __name__ == "__main__":
    app.run(port=8082)
