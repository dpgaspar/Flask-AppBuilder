app.directive('btnAdd', function() {
  return {

      restrict: 'AE',
      replace: 'true',
      scope: 'true',
      scope: {
        tipText: '@',
        url: '@'
        },
      templateUrl: '/static/angularAssets/btnAdd.html'
  };
});

app.directive('btnShow', function() {
  return {

      restrict: 'AE',
      replace: 'true',
      scope: 'true',
      scope: {
        tipText: '@',
        url: '@'
        },
      templateUrl: '/static/angularAssets/btnShow.html'
  };
});


app.directive('btnEdit', function() {
  return {

      restrict: 'AE',
      replace: 'true',
      scope: 'true',
      scope: {
        tipText: '@',
        url: '@'
        },
      templateUrl: '/static/angularAssets/btnEdit.html'
  };
});

app.directive('btnDelete', function() {
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
