angular.module('DominionAI', [])

.controller('DominionAIController', ['$scope', '$log', '$http',
  function($scope, $log, $http) {

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
}
]);