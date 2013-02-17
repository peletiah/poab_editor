angular.module("ui.bootstrap", ["ui.bootstrap.tpls", ]);

angular.module("ui.bootstrap.tpls", []);

angular.module("ui.bootstrap.alert", []).directive('alert', function () {
  return {
    restrict:'E',
    templateUrl:'template/alert/alert.html',
    transclude:true,
    scope:{
      type:'=',
      close:'&'
    },
    link:function (scope, element, attrs) {
      scope.type = scope.type || 'info';
      scope.dismiss = function () {
        scope.close();
      };
    }
  };
});


angular.module('ui.bootstrap.tabs', [])
.controller('TabsController', ['$scope', '$element', function($scope, $element) {
  var panes = $scope.panes = [];

  $scope.select = function selectPane(pane) {
    angular.forEach(panes, function(pane) {
      pane.selected = false;
    });
    pane.selected = true;
  };

  this.addPane = function addPane(pane) {
    if (!panes.length) {
      $scope.select(pane);
    }
    panes.push(pane);
  };

  this.removePane = function removePane(pane) { 
    var index = panes.indexOf(pane);
    panes.splice(index, 1);
    //Select a new pane if removed pane was selected 
    if (pane.selected && panes.length > 0) {
      $scope.select(panes[index < panes.length ? index : index-1]);
    }
  };
}])
.directive('tabs', function() {
  return {
    restrict: 'E',
    transclude: true,
    scope: {},
    controller: 'TabsController',
    templateUrl: 'template/tabs/tabs.html',
    replace: true
  };
})
.directive('pane', function() {
  return {
    require: '^tabs',
    restrict: 'E',
    transclude: true,
    scope:{
      heading:'@'
    },
    link: function(scope, element, attrs, tabsCtrl) {
      tabsCtrl.addPane(scope);
      scope.$on('$destroy', function() {
        tabsCtrl.removePane(scope);
      });
    },
    templateUrl: 'template/tabs/pane.html',
    replace: true
  };
});

angular.module("template/alert/alert.html", []).run(["$templateCache", function($templateCache){
  $templateCache.put("template/alert/alert.html",
    "<div class='alert alert-block' ng-class=\"'alert-' + type\">" +
    "  <button type='button' class='cclose' ng-click='dismiss()'>&times;</button>" +
    "  <div ng-transclude></div>" +
    "</div>");
}]);

angular.module("template/tabs/tabs.html", []).run(["$templateCache", function($templateCache){
  $templateCache.put("template/tabs/tabs.html",
    "<div class=\"tabbable\">" +
    "  <ul class=\"nav nav-tabs\">" +
    "    <li ng-repeat=\"pane in panes\" ng-class=\"{active:pane.selected}\">" +
    "      <a href=\"\" ng-click=\"select(pane)\">{{pane.heading}}</a>" +
    "    </li>" +
    "  </ul>" +
    "  <div class=\"tab-content\" ng-transclude></div>" +
    "</div>" +
    "");
}]);

angular.module("template/tabs/pane.html", []).run(["$templateCache", function($templateCache){
  $templateCache.put("template/tabs/pane.html",
    "<div class=\"tab-pane\" ng-class=\"{active: selected}\" ng-show=\"selected\" ng-transclude></div>" +
    "");
}]);
