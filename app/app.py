from flask import Flask
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
import sys

app = Flask(__name__)

# export FLASK_APP=app.py
# flask run

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/buy', methods=['POST'])
def buy():
    print(request.form, file=sys.stderr)
    print(request.form["to_buy"], file=sys.stderr)

    return {'aaaah'}