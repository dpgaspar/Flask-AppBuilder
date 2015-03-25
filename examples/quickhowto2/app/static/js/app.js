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


app.factory("filterManager", function() {
    return {
        filters: {}, // TYPE: { 'MODELVIEW_NAME': [[COL, FILTER_TYPE, VALUE],[COL, FILTER_TYPE, VALUE]...], ... }

        addFilter: function(modelview_name, col, filter_type, value) {
            filter = [col, filter_type, value];
            if (!filters[modelview_name]) {
                filters[modelview_name] = [filter];
            }
            else {
                filters[modelview_name].push(filter);
            }
        },
        removeFilter: function(modelview_name, index) {
            filters[modelview_name].splice(index, 1);
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
