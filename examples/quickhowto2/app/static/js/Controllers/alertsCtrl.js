
app.controller("alertsCtrl", function($scope, alertsManager) {

  $scope.alerts = alertsManager.alerts;

  $scope.removeAlert = function(message) {
    alertsManager.removeAlert(message);
  }
 });


app.controller("ModelCtrl", function($scope, ApiService, loadingManager, alertsManager) {

    $scope.filter = "";
    $scope.filters = []; // This is of type [[<COL_NAME>,<TYPE>,<VALUE>], .... ]

    $scope.order_column = "";
    $scope.order_direction = "";
    $scope.page_size = 10;
    $scope.page = 0;
    init();

    function init() {
        loadingManager.loading();
        if (!$scope.base_url) { return; }
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

        },
        // on Fail
        function(reason) {
            console.log(reason + ' ERROR' + $scope);
            loadingManager.loaded();
            alertsManager.addAlert(reason, "danger");
        });
    }


  });

