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

  ctrl.purchaseable_cards = ["hello", "goodbye"];

  ctrl.gameNotStarted = true;

  // play_phase = 0: not person turn
  // play_phase = 1: action phase
  // play_phase = 2: buy phase
  ctrl.play_phase = 0;

  ctrl.buyCard = function() {
    var card_to_buy = ctrl.to_buy;

    $log.log("Buying " + card_to_buy);

    $http.post('/buy', {"to_buy": card_to_buy}).
      success(function(results) {
        $log.log(results);
      }).
      error(function(error) {
        $log.log(error);
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
        });
  };

  ctrl.endActionPhase = function() {
    ctrl.play_phase = 2;

    $http.get('/get_purchaseable_cards').then(function(response) {
        $log.log(response);

        // TODO: need a better return type that gives card id and name
        // then put into an array of objects for ng-repeat with .name key
        ctrl.purchaseable_cards = response.data;

        $log.log('purchaseable:');
        $log.log(ctrl.purchaseable_cards);
    });
  };
}
]);