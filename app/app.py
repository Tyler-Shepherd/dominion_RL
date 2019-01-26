from flask import Flask
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
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

kingdom = None
person = None

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

@app.route('/start_game', methods=['GET'])
def start_game():
    global kingdom, person
    kingdom = dominion_utils.generate_kingdom()
    kingdom.reset()

    person = Person()
    person.initialize(kingdom)
    person.reset_game()

    data = {"turn": kingdom.turn_num, "hand": dominion_utils.cards_to_string(person.hand), "kingdom": dominion_utils.kingdom_to_string(kingdom)}
    data = json.dumps(data)
    resp = Response(data, status=200, mimetype='application/json')
    return resp

@app.route('/get_purchaseable_cards', methods=['GET'])
def get_purchaseable_cards():
    global kingdom, person
    purchaseable_cards = dominion_utils.cards_to_string(dominion_utils.get_purchaseable_cards(person.num_coins(), kingdom))

    app.logger.info("purchaseable: %s", str(purchaseable_cards))

    resp = Response(json.dumps(purchaseable_cards), status=200, mimetype='application/json')
    return resp

if __name__ == '__main__':
    app.run(port=5000,debug=True)