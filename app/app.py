from flask import Flask
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
import sys
import json
import logging

sys.path.append('../')
sys.path.append('./scripts')
from player import Player
from kingdom import Kingdom
import dominion_utils
from person import Person

app = Flask(__name__)

kingdom = dominion_utils.generate_kingdom()
kingdom.reset()

person = Person()
person.initialize(kingdom)
person.reset_game()

# export FLASK_APP=app.py
# flask run

@app.route('/')
def hello():
    app.logger.info('Index loaded')

    return render_template('index.html')

@app.route('/buy', methods=['POST'])
def buy():
    data = json.loads(request.data.decode())
    print(data)
    card_to_buy = data['to_buy']

    app.logger.info("Buying " + card_to_buy)
    person.print_state()
    person.clean_up()

    return ''

if __name__ == '__main__':
    app.run(port=5000,debug=True)