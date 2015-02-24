

app.controller("TableCtrl", function($scope, $http, $attrs, modelRestService) {

  $scope.filter = "";
  $scope.order_column = "";
  $scope.order_direction = "";
  $scope.page_size = 10;
  $scope.page = 0;
  $scope.base_url = $attrs.base;
  

  function init() {
    modelRestService.getInfo($scope.base_url).then(function(data) {
        $scope.base_url_read = data.api_urls.read;
        $scope.base_url_delete = data.api_urls.delete;
        $scope.delete_url = data.modelview_urls.delete;
        $scope.show_url = data.modelview_urls.show;
        $scope.add_url = data.modelview_urls.add;
        $scope.edit_url = data.modelview_urls.edit;
        $scope.can_show = data.can_show;
        $scope.can_add = data.can_add;
        $scope.can_edit = data.can_edit;
        $scope.can_delete = data.can_delete;
        $scope.modelview_name = data.modelview_name;
        query();
    });
  }

  function query() {
    if (!$scope.modelview_name) return;
    modelRestService.query($scope.modelview_name,
                            $scope.base_url_read,
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
      $http.delete($scope.base_url_delete + pk).
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
    init();
});
