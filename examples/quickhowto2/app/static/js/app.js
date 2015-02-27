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


app.factory("alertsManager", function() {
  return {
    alerts: [],

    addAlert: function(message, severity) {
        if (!this.alerts) {
            this.alerts = [{message: message, severity: severity}];
        }
        else {
            this.alerts.push({message: message, severity: severity});
        }
        console.log(this.alerts);
    },
    removeAlert: function(message) {
      for (var index in this.alerts) {
        if (this.alerts[index].message == message) {
          this.alerts.splice(index,1);
	}
      }
    }
  };
});
