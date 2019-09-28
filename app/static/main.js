cards_to_string = function(cards) {
    let c_str = '';
    for(i=0; i<cards.length; i++) {
        c_str += cards[i].name + " ";
    }
    return c_str;
}

var app = angular.module('DominionAI', []);

app.config(['$interpolateProvider', function($interpolateProvider) {
  $interpolateProvider.startSymbol('{[');
  $interpolateProvider.endSymbol(']}');
}]);

app.controller('DominionAIController', ['$log', '$http',
  function($log, $http) {

  var ctrl = this;

  ctrl.play_log = "Press to Start";
  ctrl.turn_num = -1;
  ctrl.person_hand = "";
  ctrl.person_hand_serialized = [];
  ctrl.kingdom = "";
  ctrl.in_play = "";

  //num_actions and num_buys are just views of data from server, not set by client
  ctrl.action_cards = [];
  ctrl.num_actions = 0;

  ctrl.purchaseable_cards = [];
  ctrl.num_buys = 0;
  ctrl.num_coins = 0;

  ctrl.gameNotStarted = true;
  ctrl.gameOver = false;

  ctrl.winner = "";
  ctrl.person_vp = 0;
  ctrl.agent_vp = 0;

  // play_phase = -2: agent buy phase
  // play_phase = -1: agent action phase
  // play_phase = 0: nobody's turn
  // play_phase = 1: player action phase
  // play_phase = 2: player buy phase
  ctrl.play_phase = 0;

  ctrl.follow_up = {};
  ctrl.follow_up_active = false;

  ctrl.num_cards_in_deck = 10;

  ctrl.buyCard = function(card_to_buy) {
    $log.log("Buying " + card_to_buy);

    $http.post('/buy', {"to_buy": card_to_buy})
      .then(function(response) {
        $log.log(response);
        ctrl.num_buys = response.data.num_buys;
        ctrl.person_vp = response.data.person_vp;
        ctrl.kingdom = response.data.kingdom;
        $http.get('/get_purchaseable_cards')
            .then(function(response) {
                $log.log(response);
                ctrl.purchaseable_cards = response.data.purchaseable;
                ctrl.in_play = cards_to_string(response.data.in_play);
                ctrl.person_hand = cards_to_string(response.data.hand);
                ctrl.num_coins = response.data.num_coins;

                $log.log('Purchaseable:');
                $log.log(ctrl.purchaseable_cards);
            });
       })
      .catch(function(error) {
        $log.log(error);
      });
  };

  ctrl.playCard = function(card_to_play) {
    $log.log("Playing " + card_to_play);

    $http.post('/play_action_card', {"to_play": card_to_play})
      .then(function(response) {
        $log.log(response);
        ctrl.num_actions = response.data.num_actions;
        ctrl.kingdom = response.data.kingdom;
        ctrl.action_cards = response.data.action_cards;
        ctrl.person_hand = cards_to_string(response.data.hand);
        ctrl.person_hand_serialized = response.data.hand;
        ctrl.num_buys = response.data.num_buys;
        ctrl.in_play = cards_to_string(response.data.in_play);
        ctrl.num_cards_in_deck = response.data.num_cards_in_deck;
        ctrl.num_coins = response.data.num_coins;
        ctrl.person_vp = response.data.person_vp;
        ctrl.agent_vp = response.data.agent_vp;

        if (response.data.follow_up) {
            ctrl.follow_up = response.data.follow_up;
            ctrl.follow_up_active = true;
            $log.log("Follow up action");
            $log.log(ctrl.follow_up);
        }
      })
      .catch(function(error) {
        $log.log(error);
      });
  };

  ctrl.endTurn = function() {
    $http.get('/end_turn').then(function(response) {
        $log.log(response);

        if(response.data.game_over) {
            ctrl.gameOver = true;
            ctrl.person_vp = response.data.person_vp;
            ctrl.agent_vp = response.data.agent_vp;
            ctrl.winner = response.data.winner;
            ctrl.play_phase = 0;
        }
        else {
            ctrl.play_phase = -1;
        }

        ctrl.turn_num = response.data.turn;
        ctrl.person_hand = cards_to_string(response.data.hand);
        ctrl.person_hand_serialized = response.data.hand;
        ctrl.kingdom = response.data.kingdom;
        ctrl.in_play = cards_to_string(response.data.in_play);
        ctrl.num_cards_in_deck = response.data.num_cards_in_deck;

        // Agent num_buys and num_actions
        ctrl.num_actions = response.data.num_actions;
        ctrl.num_buys = response.data.num_buys;
    });
  };

  ctrl.startGame = function() {
    $log.log("Starting Game");
    ctrl.play_log = "Game Started";

    $http.get('/start_game').then(function(response) {
        $log.log(response);

        ctrl.gameNotStarted = false;
        ctrl.play_phase = response.data.play_phase;
        ctrl.turn_num = response.data.turn;
        ctrl.person_hand = cards_to_string(response.data.hand);
        ctrl.person_hand_serialized = response.data.hand;
        ctrl.kingdom = response.data.kingdom;
        ctrl.num_cards_in_deck = 5;
        $http.get('/get_action_cards').then(function(response) {
            $log.log(response);
            ctrl.action_cards = response.data;
            ctrl.num_actions = 1;
            ctrl.num_buys = 1;
            ctrl.num_coins = 0;
        });
    });
  };

  ctrl.endActionPhase = function() {
    $http.get('/get_purchaseable_cards').then(function(response) {
        ctrl.play_phase = 2;

        $log.log(response);
        ctrl.purchaseable_cards = response.data.purchaseable;
        ctrl.in_play = cards_to_string(response.data.in_play);
        ctrl.person_hand = cards_to_string(response.data.hand);
        ctrl.num_coins = response.data.num_coins;

        $log.log('purchaseable:');
        $log.log(ctrl.purchaseable_cards);
    });
  };

  ctrl.agentNext = function() {
    if(ctrl.play_phase === -1) {
        // agent action phase, play action card or end action phase
        $http.get('/get_agent_action').then(function(response) {
            $log.log(response);

            ctrl.kingdom = response.data.kingdom;

            if (response.data.end_action_phase) {
                ctrl.play_phase = -2;
                ctrl.play_log = "Opponent ended action phase.";
            }
            else {
                ctrl.play_log = "Opponent played " + response.data.played_card;
            }

            ctrl.num_buys = response.data.num_buys;
            ctrl.num_actions = response.data.num_actions;
            ctrl.person_hand = cards_to_string(response.data.hand);
            ctrl.person_hand_serialized = response.data.hand;
            ctrl.in_play = cards_to_string(response.data.in_play);
            ctrl.num_coins = response.data.num_coins;
            ctrl.person_vp = response.data.person_vp;
            ctrl.agent_vp = response.data.agent_vp;

            if (response.data.follow_up) {
                ctrl.follow_up = response.data.follow_up;
                ctrl.follow_up_active = true;
                $log.log("Follow up action");
                $log.log(ctrl.follow_up);
            }
        });
    }

    else if (ctrl.play_phase === -2) {
        // agent buy phase, buy card or end turn
        $http.get('/get_agent_buy').then(function(response) {
            $log.log(response);

            ctrl.kingdom = response.data.kingdom;
            ctrl.in_play = cards_to_string(response.data.in_play);
            ctrl.num_coins = response.data.num_coins;
            ctrl.person_vp = response.data.person_vp;
            ctrl.agent_vp = response.data.agent_vp;

            if (response.data.end_buy_phase) {
                $http.get('/end_agent_turn').then(function(response) {
                    $log.log(response);

                    if(response.data.game_over) {
                        ctrl.gameOver = true;
                        ctrl.winner = response.data.winner;
                        ctrl.play_phase = 0;
                    } else {
                        $http.get('/get_action_cards').then(function(response) {
                            ctrl.play_phase = 1;

                            $log.log(response);
                            ctrl.action_cards = response.data;
                        });
                    }

                    ctrl.turn_num = response.data.turn;
                    ctrl.person_hand = cards_to_string(response.data.hand);
                    ctrl.person_hand_serialized = response.data.hand;
                    ctrl.kingdom = response.data.kingdom;
                    ctrl.num_buys = response.data.num_buys;
                    ctrl.num_actions = response.data.num_actions;
                    ctrl.in_play = cards_to_string(response.data.in_play);

                    ctrl.play_log = "Opponent ended turn - your turn.";
                });
            } else {
                ctrl.play_log = "Opponent bought " + response.data.bought_card;
                ctrl.num_buys = response.data.num_buys;
            }
        });
    }
  };

  ctrl.followUpGainCard = function(card_to_gain) {
    $log.log("Follow up gain " + card_to_gain);

    $http.post('/gain', {"to_gain": card_to_gain})
      .then(function(response) {
        $log.log(response);
        ctrl.kingdom = response.data.kingdom;
        ctrl.person_vp = response.data.person_vp;
        ctrl.agent_vp = response.data.agent_vp;

        ctrl.follow_up.remaining -= 1;
        if (ctrl.follow_up.remaining == 0) {
            ctrl.follow_up_active = false;
        }
       })
      .catch(function(error) {
        $log.log(error);
      });
  };

  ctrl.followUpDiscard = function(card_to_discard) {
    $log.log("Follow up discard " + card_to_discard);

    $http.post('/discard', {"to_discard": card_to_discard})
      .then(function(response) {
        $log.log(response);
        ctrl.kingdom = response.data.kingdom;
        ctrl.person_hand = cards_to_string(response.data.hand);
        ctrl.person_hand_serialized = response.data.hand;

        ctrl.follow_up.remaining -= 1;
        if (ctrl.follow_up.remaining == 0) {
            ctrl.follow_up_active = false;
        }
       })
      .catch(function(error) {
        $log.log(error);
      });
  };
}
]);