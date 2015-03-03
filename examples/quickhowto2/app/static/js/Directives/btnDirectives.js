app.directive('abBtnAdd', function($compile) {
  return {

      restrict: 'AE',
      replace: 'true',
      scope: 'true',
      scope: {
        tipText: '@',
        url: '@',
        dataPlacement: '@'
        },
      templateUrl: '/static/angularAssets/abBtnAdd.html',
      link: function link ( scope, element, attrs ) {
		$(element).hover(function(){
                // on mouseenter
                $(element).tooltip('show');
                }, function(){
                // on mouseleave
                   $(element).tooltip('hide');
                });
            },
      controller: function ($scope) {
          $scope.dataPlacement = $scope.dataPlacement || 'bottom';
      }
  };
});

app.directive('abBtnShow', function() {
  return {

      restrict: 'AE',
      replace: 'true',
      scope: 'true',
      scope: {
        tipText: '@',
        url: '@',
        dataPlacement: '@'
        },
      templateUrl: '/static/angularAssets/abBtnShow.html',
      link: function link ( scope, element, attrs ) {
                $(element).hover(function(){
                // on mouseenter
                $(element).tooltip({container:'.row'});
                $(element).tooltip('show');
                }, function(){
                // on mouseleave
                   $(element).tooltip('hide');
                });
            },
      controller: function ($scope) {
          $scope.dataPlacement = $scope.dataPlacement || 'bottom';
      }
  };
});


app.directive('abBtnEdit', function() {
  return {

      restrict: 'AE',
      replace: 'true',
      scope: 'true',
      scope: {
        tipText: '@',
        url: '@',
        dataPlacement: '@'
        },
      templateUrl: '/static/angularAssets/abBtnEdit.html',
      link: function link ( scope, element, attrs ) {
                $(element).hover(function(){
                // on mouseenter
                $(element).tooltip({container:'.row'});
                $(element).tooltip('show');
                }, function(){
                // on mouseleave
                   $(element).tooltip('hide');
                });
            },
      controller: function ($scope) {
          $scope.dataPlacement = $scope.dataPlacement || 'bottom';

      }
  };
});

app.directive('abBtnDelete', function() {
  return {

      restrict: 'AE',
      replace: 'true',
      scope: 'true',
      scope: {
        tipText: '@',
        url: '@',
        onClick: '&',
        dataPlacement: '@'
        },
      templateUrl: '/static/angularAssets/abBtnDelete.html',
      link: function link ( scope, element, attrs ) {
                $(element).hover(function(){
                  // on mouseenter
                  $(element).tooltip({container:'.row'});
                  $(element).tooltip('show');
                  }, function(){
                  // on mouseleave
                  $(element).tooltip('hide');
                });
                $(element).click(function(){
                    scope.onClick();
                    $(element).tooltip('hide');
                });
            },
      controller: function ($scope) {
          $scope.dataPlacement = $scope.dataPlacement || 'bottom';

      }
  };
});

app.directive('abSelect', function() {
  return {

      restrict: 'AE',
      replace: 'true',
      scope: 'true',
      scope: {
        data: '=',
        id: '@',
        name: '@',
        dataPlaceholder: '@'
        },
      templateUrl: '/static/angularAssets/abSelect.html',
      link: function postLink(scope, element, attrs) {
          $(element).select2({placeholder: "Select a State", allowClear: true});

        }
  };
});

app.directive('abDate', function() {
  return {

      restrict: 'AE',
      replace: 'true',
      scope: 'true',
      scope: {
        format: '@',
        value: '@',
        language: "@",
        daysOfWeekDisabled: "@",
        minViewMode: "@"
        },
      templateUrl: '/static/angularAssets/abDate.html',
      link: function postLink(scope, element, attrs) {
          if (!scope.format) { scope.format = "yyyy-MM-dd"; }
          if (!scope.language) { scope.language = "en"; }
          if (!scope.daysOfWeekDisabled) { scope.daysOfWeekDisabled = ""; }
          if (!scope.minViewMode) { scope.minViewMode = "0"; }
          minVM = parseInt(scope.minViewMode)
          $(element).datetimepicker({pickTime: false, format: scope.format, language: scope.language,
                                    daysOfWeekDisabled: scope.daysOfWeekDisabled,
                                    minViewMode: minVM});
      }
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


app.directive('dynamic', function ($compile) {
    return {
      restrict: 'A',
      replace: true,
      scope: { dynamic: '=dynamic'},
      link: function postLink(scope, element, attrs) {
        scope.$watch( 'dynamic' , function(html){
          element.html(html);
          if (angular.element(html).hasClass('appbuilder_date')) {
            $(element).datetimepicker({pickTime: false });
          }
          if (angular.element(html).hasClass('appbuilder_datetime')) {
            $(element).datetimepicker();
          }
          // REALLY STUPID

          $compile(element.contents())(scope);
          // $('.appbuilder_datetime').datetimepicker({pickTime: false});
          //  $('.appbuilder_date').datetimepicker({
          //      pickTime: false });
          //  $(".my_select2").select2({placeholder: "Select a State", allowClear: true});;
          //  $(".my_select2.readonly").select2("readonly",true)
          //  $("a").tooltip({container:'.row', 'placement': 'bottom'});

        });
      }
    };
});


app.directive('abModalOkCancel', function($http, $compile) {
  return {

      restrict: 'A',
      scope: 'true',
      scope: {
        titleText: '@',
        bodyText: '@',
        okText: '@',
        cancelText: '@',
        onOk: '&'

        },
      compile: function(element, cAtts){
        var template,
        $element,
        loader;

          loader = $http.get('/static/angularAssets/abModalOkCancel.html')
            .success(function(data) {
              template = data;
            });
          return function(scope, element, lAtts) {
            loader.then(function() {
              //compile templates/form_modal.html and wrap it in a jQuery object
              $element = $( $compile(template)(scope) );
            });
            element.on('click', function(e) {
                e.preventDefault();
                $element.modal('show');
            });
            scope.clickOk = function() {
                console.log('OK');
                scope.onOk()();
                $element.modal('hide');
            };
        }
      }
  };
});

