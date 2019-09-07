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

# export FLASK_APP=app.py
# flask run

# Python Flask middleware

@app.route('/')
def hello():
    app.logger.info('Index loaded')

    return render_template('index.html')

@app.route('/buy', methods=['POST'])
def buy():
    global kingdom, person, agent
    data = json.loads(request.data.decode())
    card_to_buy = Card(data['to_buy'])

    dominion_utils.buy_card(person, card_to_buy, kingdom)

    data = {"turn": kingdom.turn_num, "hand": dominion_utils.serialize_cards(person.hand),
            "kingdom": dominion_utils.kingdom_to_string(kingdom), "num_buys": person.num_buys}
    data = json.dumps(data)
    resp = Response(data, status=200, mimetype='application/json')
    return resp

@app.route('/gain', methods=['POST'])
def gain():
    global kingdom, person, agent
    data = json.loads(request.data.decode())
    card_to_gain = Card(data['to_gain'])

    app.logger.info(person.name + " gaining " + card_to_gain.name)

    dominion_utils.gain_card(person, card_to_gain, kingdom)

    data = {"turn": kingdom.turn_num, "hand": dominion_utils.serialize_cards(person.hand),
            "kingdom": dominion_utils.kingdom_to_string(kingdom)}
    data = json.dumps(data)
    resp = Response(data, status=200, mimetype='application/json')
    return resp

@app.route('/discard', methods=['POST'])
def discard():
    global kingdom, person, agent
    data = json.loads(request.data.decode())
    card_to_discard = Card(data['to_discard'])

    app.logger.info("Discard " + card_to_discard.name)
    print(card_to_discard)
    print(person.hand)

    dominion_utils.discard_card(card_to_discard, person)

    data = {"turn": kingdom.turn_num, "hand": dominion_utils.serialize_cards(person.hand),
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

    app.logger.info(person.name + " playing " + card_to_play.name)

    person.hand.remove(card_to_play)
    person.in_play.append(card_to_play)
    follow_up_action = card_to_play.play(person)
    person.num_actions -= 1

    action_cards = [card for card in person.hand if card.f_action]
    action_cards_data = dominion_utils.serialize_cards(action_cards)

    data = {"hand": dominion_utils.serialize_cards(person.hand), "action_cards": action_cards_data,
            "kingdom": dominion_utils.kingdom_to_string(kingdom), "num_actions": person.num_actions,
            "num_buys": person.num_buys}
    data["follow_up"] = follow_up_action.serialize() if follow_up_action else None

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
    elif kingdom.starting_player == -1:
        kingdom.next_turn()

    data = {"turn": kingdom.turn_num, "hand": dominion_utils.serialize_cards(person.hand),
            "kingdom": dominion_utils.kingdom_to_string(kingdom), "game_over": game_over,
            "num_buys": agent.num_buys, "num_actions": agent.num_actions}
    data = json.dumps(data)
    resp = Response(data, status=200, mimetype='application/json')
    return resp

@app.route('/end_agent_turn', methods=['GET'])
def end_agent_turn():
    global kingdom, person, agent
    agent.clean_up()
    agent.print_state()

    game_over = False
    if kingdom.is_game_over() != -1:
        game_over = True
    elif kingdom.starting_player == 1:
        kingdom.next_turn()

    data = {"turn": kingdom.turn_num, "hand": dominion_utils.serialize_cards(person.hand),
            "kingdom": dominion_utils.kingdom_to_string(kingdom), "game_over": game_over,
            "num_buys": person.num_buys, "num_actions": person.num_actions}
    data = json.dumps(data)
    resp = Response(data, status=200, mimetype='application/json')
    return resp

@app.route('/get_agent_action', methods=['GET'])
def get_agent_action():
    global kingdom, person, agent

    played_card, follow_up = agent.action_phase()

    data = {"kingdom": dominion_utils.kingdom_to_string(kingdom),
            "end_action_phase": played_card is None,
            "played_card": played_card.name if played_card else "",
            "num_buys": agent.num_buys, "num_actions": agent.num_actions,
            "hand": dominion_utils.serialize_cards(person.hand)}
    data["follow_up"] = follow_up.serialize() if follow_up else None
    data = json.dumps(data)
    resp = Response(data, status=200, mimetype='application/json')
    return resp

@app.route('/get_agent_buy', methods=['GET'])
def get_agent_buy():
    global kingdom, person, agent

    bought_card = agent.buy_phase()

    data = {"kingdom": dominion_utils.kingdom_to_string(kingdom),
            "end_buy_phase": bought_card is None,
            "bought_card": bought_card.name if bought_card else "",
            "num_buys": agent.num_buys}
    data = json.dumps(data)
    resp = Response(data, status=200, mimetype='application/json')
    return resp


@app.route('/start_game', methods=['GET'])
def start_game():
    global kingdom, person, agent
    kingdom = dominion_utils.generate_kingdom()
    kingdom.reset()

    person = Person()
    person.initialize(kingdom)
    person.reset_game()

    agent = Agent()
    agent.initialize(kingdom)
    agent.reset_game()

    person.opponent = agent
    agent.opponent = person

    # 1 if agent turn
    # -1 if opponent turn
    whose_turn = kingdom.starting_player

    data = {"turn": kingdom.turn_num, "hand": dominion_utils.serialize_cards(person.hand), "kingdom": dominion_utils.kingdom_to_string(kingdom), "play_phase": whose_turn}
    data = json.dumps(data)
    resp = Response(data, status=200, mimetype='application/json')
    return resp

@app.route('/get_purchaseable_cards', methods=['GET'])
def get_purchaseable_cards():
    global kingdom, person, agent
    person.play_treasures()
    purchaseable_cards = dominion_utils.get_purchaseable_cards(person, person.coins, kingdom)
    purchaseable_cards_data = dominion_utils.serialize_cards(purchaseable_cards)

    resp = Response(json.dumps(purchaseable_cards_data), status=200, mimetype='application/json')
    return resp

@app.route('/get_action_cards', methods=['GET'])
def get_action_cards():
    global kingdom, person, agent
    action_cards =  [card for card in person.hand if card.f_action]
    action_cards_data = dominion_utils.serialize_cards(action_cards)

    app.logger.info("Action cards: %s", str(action_cards_data))

    resp = Response(json.dumps(action_cards_data), status=200, mimetype='application/json')
    return resp


if __name__ == '__main__':
    app.run(port=5000,debug=True)