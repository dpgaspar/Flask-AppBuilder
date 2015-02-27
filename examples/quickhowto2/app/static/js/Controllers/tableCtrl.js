

app.controller("TableCtrl", function($scope, $http, $attrs, ApiService, loadingManager, alertsManager) {

  $scope.filter = "";
  $scope.order_column = "";
  $scope.order_direction = "";
  $scope.page_size = 10;
  $scope.page = 0;
  $scope.base_url = $attrs.base;


  function init() {
    loadingManager.loading();
    ApiService.getInfo($scope.base_url).then(function(data) {
        loadingManager.loaded();
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

        $scope.search_filters = data.search_filters;
        $scope.search_fields = data.search_fields;
        $scope.label_columns = data.label_columns;
        $scope.active_filters = [];
        console.log("INIT", $scope);
        read();
    },
    function(reason) {
        loadingManager.loaded();
        alertsManager.addAlert(reason, "danger");
    });
  }

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
    init();
});
