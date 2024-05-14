from flask import Flask, render_template, request, redirect, abort
from flask.wrappers import Response
import time, os
bp = Blueprint('hybrid', __name__, template_folder='templates')
app = Flask(__name__)
app.register_blueprint(bp, url_prefix="/hybrid")

@app.route('/', methods=['GET'])
def index():
    return "No endpoint specified!"

if __name__ == "__main__":
    app.run(port=8080)
