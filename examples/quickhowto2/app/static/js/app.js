var app = angular.module('FAB', []);

app.config(['$interpolateProvider', function($interpolateProvider) {
  $interpolateProvider.startSymbol('{[');
  $interpolateProvider.endSymbol(']}');
}]);

app.factory("loadingManager", function($rootScope) {
  return {
    loading: function() {
      $rootScope.loading = true;
    },
    loaded: function() {
      $rootScope.loading = false;
    }
  };

});
