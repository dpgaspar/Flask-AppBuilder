

app.controller("TableCtrl", function($scope, $http, modelRestService) {

  $scope.filter = "";
  $scope.order_column = "";
  $scope.order_direction = "";
  $scope.base_url = base_url;
  $scope.show_url = show_url;
  $scope.add_url = add_url;
  $scope.edit_url = edit_url;
  $scope.delete_url = delete_url;
  $scope.can_show = can_show;
  $scope.can_add = can_add;
  $scope.can_edit = can_edit;
  $scope.can_delete = can_delete;
  $scope.modelview_name = modelview_name;
  $scope.page_size = page_size;
  $scope.page = page;

  function query() {
    modelRestService.query($scope.modelview_name,
                            $scope.base_url,
                            $scope.filter,
                            $scope.order_column,
                            $scope.order_direction,
                            $scope.page,
                            $scope.page_size)
    .then(function( data ) {
        $scope.data = data;
    });
  }

   $scope.delete = function(pk) {
      $http.delete($scope.base_url + '/' + pk).
        success(function(data, status, headers, config) {
          query();
        }).
        error(function(data, status, headers, config) {
          // log error
        });
   }

   $scope.$watch('filter', function (value) {
        query();
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
        query();
   }

    $scope.pageSizeClick = function(page_size) {
        $scope.page_size = page_size;
        query();
    }

    $scope.pageClick = function(page) {
        $scope.page = page;
        query();
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

    query();
    console.log($scope);
});
