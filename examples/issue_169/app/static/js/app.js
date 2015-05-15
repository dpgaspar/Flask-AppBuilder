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

app.factory("filterManager", function() {
    return {
        filters: {}, // TYPE: { 'MODELVIEW_NAME': [[COL, FILTER_TYPE, VALUE],[COL, FILTER_TYPE, VALUE]...], ... }

        addFilter: function(viewName, colName, filterType, value) {
           filter = [colName, filterType, value];
           if (!(viewName in filters)) {
               filters[viewName] = [filter];
           }
           else {
               filters[viewName].push(filter);
           }
           console.log(filters);
        },
        removeFilter: function(viewName, colName, filterType, value) {
           if (!(viewName in filters)) { return; }
           _filters = filters[viewName];
           for (i = 0; index < _filters.length; i++)
           {
               if ((_filters[i][0] == colName) & (_filters[i][1] == filterType) & (_filters[i][2] == value)) {
                   _filters.splice(i,1);
               }
           }
           console.log(filters);
        }

    };    
});


