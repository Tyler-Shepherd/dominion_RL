angular.module('DominionAI', [])

.controller('DominionAIController', ['$scope', '$log', '$http',
  function($scope, $log, $http) {

//  $scope.ai_hand = "heyyyyyyy";
//  $scope.ai_deck = "hmmmmmm";
  $scope.play_log = "Press to Start";
  $scope.turn_num = -1;
  $scope.person_hand = "";
  $scope.kingdom = "";

  $scope.purchaseable_cards = []

  $scope.gameNotStarted = true;

  // play_phase = 0: not person turn
  // play_phase = 1: action phase
  // play_phase = 2: buy phase
  $scope.play_phase = 0;

  $scope.buyCard = function() {
    var card_to_buy = $scope.to_buy;

    $log.log("Buying " + card_to_buy);

    $http.post('/buy', {"to_buy": card_to_buy}).
      success(function(results) {
        $log.log(results);
      }).
      error(function(error) {
        $log.log(error);
      });
  };

  $scope.startGame = function() {
    $log.log("Starting Game");
    $scope.play_log = "Game Started";

    $http.get('/start_game').then(function(response) {
        $log.log(response);

        $scope.gameNotStarted = false;
        $scope.play_phase = 1;
        $scope.turn_num = response.data.turn;
        $scope.person_hand = response.data.hand;
        $scope.kingdom = response.data.kingdom;
        });
  };

  $scope.endActionPhase = function() {
    $scope.play_phase = 2;

    $http.get('/get_purchaseable_cards').then(function(response) {
        $log.log(response);

        // TODO: need a better return type that gives card id and name
        // then put into an array of objects for ng-repeat with .name key
        $scope.purchaseable_cards = response.data;
    });
  };
}
]);