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
                return [1,2,3,10,20];
            };
      },
  };
});
