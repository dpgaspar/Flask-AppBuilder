app.directive('abBtnAdd', function() {
  return {

      restrict: 'AE',
      replace: 'true',
      scope: 'true',
      scope: {
        tipText: '@',
        url: '@'
        },
      templateUrl: '/static/angularAssets/abBtnAdd.html'
  };
});

app.directive('abBtnShow', function() {
  return {

      restrict: 'AE',
      replace: 'true',
      scope: 'true',
      scope: {
        tipText: '@',
        url: '@'
        },
      templateUrl: '/static/angularAssets/abBtnShow.html'
  };
});


app.directive('abBtnEdit', function() {
  return {

      restrict: 'AE',
      replace: 'true',
      scope: 'true',
      scope: {
        tipText: '@',
        url: '@'
        },
      templateUrl: '/static/angularAssets/abBtnEdit.html'
  };
});

app.directive('abBtnDelete', function() {
  return {

      restrict: 'AE',
      replace: 'true',
      scope: 'true',
      scope: {
        tipText: '@',
        url: '@'
        },
      template: '<a href="{[url]}" class="btn btn-sm btn-primary" \
                data-toggle="tooltip" rel="tooltip" title="{[tipText]}">\
                <i class="fa fa-eraser"></i></a>'
  };
});

app.directive('abPagination', function() {
  return {

      restrict: 'AE',
      replace: 'true',
      scope: 'false',
      scope: {
        page: '@',
        pageSize: '@',
        count: '@',
        size: '@',
        onClick: '&'
        },
      templateUrl: '/static/angularAssets/abPagination.html',
      controller: function ($scope) {

            $scope.initVars = function() {
                $scope.init_page = 0;
                if ($scope.size) {
                    $scope.size = parseInt($scope.size);
                }
                else {
                    $scope.size = 6;
                }
                $scope.count = parseInt($scope.count) || 0;
                $scope.page = parseInt($scope.page);
                $scope.pageSize = parseInt($scope.pageSize);
              
                $scope.pages = Math.floor($scope.count / $scope.pageSize);
                $scope.min = $scope.page - ($scope.size/2);
                $scope.max = $scope.page + ($scope.size/2);
                if ($scope.min < 0) {
                    $scope.max = $scope.max - $scope.min;
                    $scope.min = 0;
                }
                if ($scope.max >= $scope.pages) {
                    $scope.max = $scope.pages;
                    $scope.min = $scope.min - $scope.max + $scope.pages;

                }
            };
            $scope.initVars();

            $scope.selPage = function (page) {
                if (page >= 0 && page <= $scope.pages) {
                    $scope.page = page;
                    $scope.initVars();
                    $scope.onClick()(page);
                }
            };

            $scope.range = function(min, max, step) {
                $scope.initVars();
                step = step || 1;
                var input = [];
                for (var i = min; i <= max; i += step) input.push(i);
                return input;
            };
      },
  };
});


app.directive('abMenuPageSize', function() {
  return {
      restrict: 'AE',
      replace: 'true',
      scope: 'true',
      scope: {
        min: '@',
        max: '@',
        step: '@',
        pageSize: '@',
        title: '@',
        url: '@',
        onClick: '&'
        },
      templateUrl: '/static/angularAssets/abMenuPageSize.html',
      controller: function ($scope) {
            $scope.selPageSize = function (page_size) {
                $scope.onClick()(page_size);
            };
            $scope.range = function() {
                $scope.min = parseInt($scope.min);
                $scope.max = parseInt($scope.max);
                $scope.step = parseInt($scope.step);
                $scope.step = $scope.step || 1;
                var input = [];
                for (var i = $scope.min; i <= $scope.max; i += $scope.step) input.push(i);
                return input;
            };
      },
  };
});
