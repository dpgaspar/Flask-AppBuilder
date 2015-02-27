
app.controller("alertsCtrl", function($scope, alertsManager) {

  $scope.alerts = alertsManager.alerts;

  $scope.removeAlert = function(message) {
    alertsManager.removeAlert(message);
  }
 });
