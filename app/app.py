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
from card import Card

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
    global kingdom, person
    data = json.loads(request.data.decode())
    card_to_buy = Card(data['to_buy'])

    app.logger.info("Buying " + card_to_buy.name)

    dominion_utils.buy_card(person, card_to_buy, kingdom)

    data = {"turn": kingdom.turn_num, "hand": dominion_utils.cards_to_string(person.hand),
            "kingdom": dominion_utils.kingdom_to_string(kingdom)}
    data = json.dumps(data)
    resp = Response(data, status=200, mimetype='application/json')
    return resp

@app.route('/end_turn', methods=['GET'])
def end_turn():
    global kingdom, person
    person.clean_up()
    person.print_state()

    game_over = False
    if kingdom.is_game_over() != -1:
        game_over = True
    else:
        kingdom.next_turn()

    data = {"turn": kingdom.turn_num, "hand": dominion_utils.cards_to_string(person.hand),
            "kingdom": dominion_utils.kingdom_to_string(kingdom), "game_over": game_over}
    data = json.dumps(data)
    resp = Response(data, status=200, mimetype='application/json')
    return resp

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
    purchaseable_cards = dominion_utils.get_purchaseable_cards(person.num_coins(), kingdom)
    purchaseable_cards_data = [{'name': c.name, 'id': c.id} for c in purchaseable_cards]

    app.logger.info("purchaseable: %s", str(purchaseable_cards_data))

    resp = Response(json.dumps(purchaseable_cards_data), status=200, mimetype='application/json')
    return resp

@app.route('/get_action_cards', methods=['GET'])
def get_action_cards():
    global kingdom, person
    action_cards =  [card for card in person.hand if card.f_action]
    action_cards_data = [{'name': c.name, 'id': c.id} for c in action_cards]

    app.logger.info("action cards: %s", str(action_cards_data))

    resp = Response(json.dumps(action_cards_data), status=200, mimetype='application/json')
    return resp


if __name__ == '__main__':
    app.run(port=5000,debug=True)