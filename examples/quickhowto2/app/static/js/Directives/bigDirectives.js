
app.directive('abModelTable', function($compile, ApiService, loadingManager, alertsManager) {
  return {

      restrict: 'E',
      replace: 'true',
      scope: 'true',
      scope: {
        base: '@',
        uiTexts: '='
        },
      templateUrl: '/static/angularAssets/abModelTable.html',
      controller: function ($scope) {
          console.log("INIT2 " + $scope.base_url);
          function read() {
            if (!$scope.modelview_name) return;
            loadingManager.loading();
            ApiService.read($scope.modelview_name,
                                    $scope.base_url_read,
                                    $scope.filter,
                                    $scope.order_column,
                                    $scope.order_direction,
                                    $scope.page,
                                    $scope.page_size)
            .then(function( data ) {
                $scope.data = data;
                loadingManager.loaded();
            },
            function(reason) {
                loadingManager.loaded();
                alertsManager.addAlert(reason, "danger");
            });
          }

           $scope.remove = function(pk) {
              loadingManager.loading();
              ApiService.remove($scope.base_url_delete, pk).
                then(function(data) {
                  loadingManager.loaded();
                  alertsManager.addAlert(data.message, "info");
                  read();
                },
                function(reason) {
                  loadingManager.loaded();
                  alertsManager.addAlert(reason, "danger");
                  // log error
                });
           }

           $scope.$watch('filter', function (value) {
                $scope.page = 0;
                read();
            });

           $scope.orderClick = function(col) {
                if ($scope.order_column == col) {
                    if ($scope.order_direction == 'asc') {
                        $scope.order_direction = 'desc';
                    }
                    else {
                        $scope.order_direction = 'asc';
                    }
                }
                else {
                    $scope.order_column = col;
                    $scope.order_direction = 'asc';
                }
                read();
           }

            $scope.pageSizeClick = function(page_size) {
                $scope.page_size = page_size;
                $scope.page = 0;
                read();
            }

            $scope.pageClick = function(page) {
                $scope.page = page;
                read();
            }

            $scope.addFilter = function(col) {
                search_field = {html: $scope.search_fields[col],
                                col: col,
                                options: $scope.search_filters[col],
                                label: $scope.label_columns[col]};
                $scope.active_filters.push(search_field);
            }

            $scope.removeFilter = function(index) {
                $scope.active_filters.splice(index, 1);
            }

            $scope.getOrderType = function(col) {
                if ($scope.order_column == col) {
                    if ($scope.order_direction == 'asc') {
                        return 2;
                    }
                    else {
                        return 1;
                    }
                }
                return 0;
            }
            read();
          }
    };
});


app.directive('abModelSearch', function($compile, ApiService, filterManager) {
  return {

      restrict: 'E',
      scope: 'true',
      templateUrl: '/static/angularAssets/abModelSearch.html',

    };
});
