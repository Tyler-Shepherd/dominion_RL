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

  // play_phase = 0: not person turn
  // play_phase = 1: action phase
  // play_phase = 2: buy phase
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

  ctrl.endTurn = function() {
    $http.get('/end_turn').then(function(response) {
        $log.log(response);

        if(response.data.game_over) {
            ctrl.gameOver = true;
            ctrl.play_phase = -1;
        }
        else {
            ctrl.play_phase = 1;
            $http.get('/get_action_cards').then(function(response) {
                $log.log(response);
                ctrl.action_cards = response.data;
                ctrl.num_actions = 1;
            });
        }

        ctrl.turn_num = response.data.turn;
        ctrl.person_hand = response.data.hand;
        ctrl.kingdom = response.data.kingdom;
    });
  };

  ctrl.startGame = function() {
    $log.log("Starting Game");
    ctrl.play_log = "Game Started";

    $http.get('/start_game').then(function(response) {
        $log.log(response);

        ctrl.gameNotStarted = false;
        ctrl.play_phase = 1;
        ctrl.turn_num = response.data.turn;
        ctrl.person_hand = response.data.hand;
        ctrl.kingdom = response.data.kingdom;
        $http.get('/get_action_cards').then(function(response) {
                $log.log(response);
                ctrl.action_cards = response.data;
                ctrl.num_actions = 1;
            });
        });
  };

  ctrl.endActionPhase = function() {
    ctrl.play_phase = 2;

    $http.get('/get_purchaseable_cards').then(function(response) {
        $log.log(response);
        ctrl.purchaseable_cards = response.data;
        ctrl.num_buys = 1;

        $log.log('purchaseable:');
        $log.log(ctrl.purchaseable_cards);
    });
  };
}
]);