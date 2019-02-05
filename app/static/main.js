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
  ctrl.kingdom = "";

  ctrl.action_cards = [];

  ctrl.purchaseable_cards = [];
  ctrl.num_buys = 1;

  ctrl.gameNotStarted = true;
  ctrl.gameOver = false;

  // play_phase = -2: agent buy phase
  // play_phase = -1: agent action phase
  // play_phase = 0: nobody's turn
  // play_phase = 1: player action phase
  // play_phase = 2: player buy phase
  ctrl.play_phase = 0;

  ctrl.buyCard = function(card_to_buy) {
    $log.log("Buying " + card_to_buy);

    $http.post('/buy', {"to_buy": card_to_buy})
      .then(function(response) {
        $log.log(response);
        ctrl.num_buys -= 1;
        ctrl.kingdom = response.data.kingdom;
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
        ctrl.num_actions -= 1;
        ctrl.kingdom = response.data.kingdom;
        ctrl.action_cards = response.data.action_cards;
        ctrl.person_hand = response.data.hand;
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
            ctrl.play_phase = 0;
        }
        else {
            ctrl.play_phase = -1;
        }

        ctrl.turn_num = response.data.turn;
        ctrl.person_hand = response.data.hand;
        ctrl.kingdom = response.data.kingdom;
        ctrl.num_actions = 1;
        ctrl.num_buys = 1;
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
        ctrl.person_hand = response.data.hand;
        ctrl.kingdom = response.data.kingdom;
        $http.get('/get_action_cards').then(function(response) {
            $log.log(response);
            ctrl.action_cards = response.data;
            ctrl.num_actions = 1;
            ctrl.num_buys = 1;
        });
    });
  };

  ctrl.endActionPhase = function() {
    ctrl.play_phase = 2;

    $http.get('/get_purchaseable_cards').then(function(response) {
        $log.log(response);
        ctrl.purchaseable_cards = response.data;

        $log.log('purchaseable:');
        $log.log(ctrl.purchaseable_cards);
    });
  };

  ctrl.agentNext = function() {
    if(ctrl.play_phase === -1) {
        // agent action phase, play action card or end action phase
        // TODO: add ability to play action cards
        ctrl.play_phase = -2;
        ctrl.play_log = "Opponent ended action phase.";
    }

    else if (ctrl.play_phase === -2) {
        // agent buy phase, buy card or end turn
        if(ctrl.num_buys > 0) {
            $http.get('/get_agent_buy').then(function(response) {
                $log.log(response);

                ctrl.kingdom = response.data.kingdom;
                ctrl.num_buys -= 1;
                ctrl.play_log = "Opponent bought " + response.data.bought_card;
            });
        }
        else {
            $http.get('/end_agent_turn').then(function(response) {
                $log.log(response);

                if(response.data.game_over) {
                    ctrl.gameOver = true;
                    ctrl.play_phase = 0;
                }
                else {
                    ctrl.play_phase = 1;
                    $http.get('/get_action_cards').then(function(response) {
                        $log.log(response);
                        ctrl.action_cards = response.data;
                    });
                }

                ctrl.turn_num = response.data.turn;
                ctrl.person_hand = response.data.hand;
                ctrl.kingdom = response.data.kingdom;
                ctrl.play_phase = 1;
                ctrl.num_buys = 1;
                ctrl.num_actions = 1;

                ctrl.play_log = "Opponent ended turn - your turn.";
            });
        }
    }
  };
}
]);