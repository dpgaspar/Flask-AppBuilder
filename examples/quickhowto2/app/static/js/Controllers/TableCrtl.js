
app.controller("TableCtrl", function($scope, $http) {

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


  function ajaxGet() {
      var query_string = "";
      var get_params = {};
      if ($scope.filter != "" ) {
        get_params['_flt_0_name'] = $scope.filter;
      }
      if ($scope.order_column != "") {
        get_params['_oc_ContactModelView2'] = $scope.order_column;
        get_params['_od_ContactModelView2'] = $scope.order_direction;
      }
      console.log("GET", get_params);
      $http.get($scope.base_url, { params : get_params }).
        success(function(data, status, headers, config) {
          $scope.data = data;
        }).
        error(function(data, status, headers, config) {
          // log error
        });
   }
   $scope.$watch('filter', function (value) {
        ajaxGet();
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
        ajaxGet();
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

    ajaxGet();
    console.log($scope);
});
