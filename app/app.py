from flask import Flask
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
)
import sys
import json
import logging
import random

sys.path.append('../')
sys.path.append('./scripts')
from player import Player
from kingdom import Kingdom
import dominion_utils
from person import Person
from agent import Agent
from card import Card

app = Flask(__name__)

kingdom = None
person = None
agent = None
starting_player = None

# export FLASK_APP=app.py
# flask run

@app.route('/')
def hello():
    app.logger.info('Index loaded')

    return render_template('index.html')

@app.route('/buy', methods=['POST'])
def buy():
    global kingdom, person, agent
    data = json.loads(request.data.decode())
    card_to_buy = Card(data['to_buy'])

    app.logger.info("Buying " + card_to_buy.name)

    dominion_utils.buy_card(person, card_to_buy, kingdom)

    data = {"turn": kingdom.turn_num, "hand": dominion_utils.cards_to_string(person.hand),
            "kingdom": dominion_utils.kingdom_to_string(kingdom)}
    data = json.dumps(data)
    resp = Response(data, status=200, mimetype='application/json')
    return resp

@app.route('/play_action_card', methods=['POST'])
def play_card():
    global kingdom, person, agent
    data = json.loads(request.data.decode())

    card_to_play = next((x for x in person.hand if x.id == data['to_play']), None)
    assert card_to_play is not None

    app.logger.info("Playing " + card_to_play.name)

    person.hand.remove(card_to_play)
    person.in_play.append(card_to_play)
    card_to_play.play(person)

    action_cards =  [card for card in person.hand if card.f_action]
    action_cards_data = [{'name': c.name, 'id': c.id} for c in action_cards]

    data = {"hand": dominion_utils.cards_to_string(person.hand), "action_cards": action_cards_data,
            "kingdom": dominion_utils.kingdom_to_string(kingdom)}
    data = json.dumps(data)
    resp = Response(data, status=200, mimetype='application/json')
    return resp

@app.route('/end_turn', methods=['GET'])
def end_turn():
    global kingdom, person, agent
    person.clean_up()
    person.print_state()

    game_over = False
    if kingdom.is_game_over() != -1:
        game_over = True
    elif starting_player == -1:
        kingdom.next_turn()

    data = {"turn": kingdom.turn_num, "hand": dominion_utils.cards_to_string(person.hand),
            "kingdom": dominion_utils.kingdom_to_string(kingdom), "game_over": game_over}
    data = json.dumps(data)
    resp = Response(data, status=200, mimetype='application/json')
    return resp

@app.route('/end_agent_turn', methods=['GET'])
def end_agent_turn():
    global kingdom, person, agent, starting_player
    agent.clean_up()
    print("Agent state:")
    agent.print_state()

    game_over = False
    if kingdom.is_game_over() != -1:
        game_over = True
    elif starting_player == 1:
        kingdom.next_turn()

    data = {"turn": kingdom.turn_num, "hand": dominion_utils.cards_to_string(person.hand),
            "kingdom": dominion_utils.kingdom_to_string(kingdom), "game_over": game_over}
    data = json.dumps(data)
    resp = Response(data, status=200, mimetype='application/json')
    return resp

@app.route('/get_agent_buy', methods=['GET'])
def get_agent_buy():
    global kingdom, person, agent

    bought_card = agent.buy_phase()

    data = {"kingdom": dominion_utils.kingdom_to_string(kingdom), "bought_card": bought_card.name}
    data = json.dumps(data)
    resp = Response(data, status=200, mimetype='application/json')
    return resp


@app.route('/start_game', methods=['GET'])
def start_game():
    global kingdom, person, agent, starting_player
    kingdom = dominion_utils.generate_kingdom()
    kingdom.reset()

    person = Person()
    person.initialize(kingdom)
    person.reset_game()

    agent = Agent()
    agent.initialize(kingdom)
    agent.reset_game()

    # 1 if agent turn
    # -1 if opponent turn
    whose_turn = 1 if random.random() < 0.5 else -1
    starting_player = whose_turn

    data = {"turn": kingdom.turn_num, "hand": dominion_utils.cards_to_string(person.hand), "kingdom": dominion_utils.kingdom_to_string(kingdom), "play_phase": whose_turn}
    data = json.dumps(data)
    resp = Response(data, status=200, mimetype='application/json')
    return resp

@app.route('/get_purchaseable_cards', methods=['GET'])
def get_purchaseable_cards():
    global kingdom, person, agent
    purchaseable_cards = dominion_utils.get_purchaseable_cards(person.num_coins(), kingdom)
    purchaseable_cards_data = [{'name': c.name, 'id': c.id} for c in purchaseable_cards]

    app.logger.info("purchaseable: %s", str(purchaseable_cards_data))

    resp = Response(json.dumps(purchaseable_cards_data), status=200, mimetype='application/json')
    return resp

@app.route('/get_action_cards', methods=['GET'])
def get_action_cards():
    global kingdom, person, agent
    action_cards =  [card for card in person.hand if card.f_action]
    action_cards_data = [{'name': c.name, 'id': c.id} for c in action_cards]

    app.logger.info("action cards: %s", str(action_cards_data))

    resp = Response(json.dumps(action_cards_data), status=200, mimetype='application/json')
    return resp


if __name__ == '__main__':
    app.run(port=5000,debug=True)