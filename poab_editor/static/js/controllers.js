var EditorModule = angular.module('editor', ['ui.bootstrap','ui.directives'], function($compileProvider) {
  // configure new 'compile' directive by passing a directive
  // factory function. The factory function injects the '$compile'
  $compileProvider.directive('compile', function($compile) {
    // directive factory creates a link function
    return function(scope, element, attrs) {
      scope.$watch(
        function(scope) {
           // watch the 'compile' expression for changes
          return scope.$eval(attrs.compile);
        },
        function(value) {
          // when the 'compile' expression changes
          // assign it into the current DOM
          element.html(value);
 
          // compile the new DOM and link it to the current
          // scope.
          // NOTE: we only compile .childNodes so that
          // we don't get into infinite loop compiling ourselves
          $compile(element.contents())(scope);
        }
      );
    };
  })
});


EditorModule.value('ui.config', {
   tinymce: {
      theme: 'advanced',
      theme_advanced_buttons1 : "bold, italic, underline, undo, redo,separator,code,bullist",
      theme_advanced_buttons2 : "",
      theme_advanced_buttons3 : "",
      theme_advanced_source_editor_width : 700,
      theme_advanced_source_editor_height : 600,
      theme_advanced_source_editor_wrap : false,
      theme_advanced_resizing : true,
      theme_advanced_resizing_max_width : 500
   }
});


var TabsCtrl = function ($scope, $http) {
  $scope.updatePreview = function() {
    log_json = JSON.stringify($scope.log, null, 0)
    console.log(log_json)
    $http({
        url:'/update_log',
        data: log_json,
        method: 'POST',
        headers : {'Content-Type':'application/json; charset=UTF-8'}
      }).success($scope.HTTPPostSuccess);
    //regex-match to find [imgidNN]-tags and replace them with <img src=...>-tags for previewing
    var re = /\[imgid(\d{1,})\]/g,
        imageIdMatch,
        imageIds = [];
    $scope.log.preview=$scope.log.content
    while (imageIdMatch = re.exec($scope.log.content))
      imageIds.push(+imageIdMatch[1]);
    for (var i = 0; i < imageIds.length; i++) {
     for ( var j = 0; j < $scope.images.length; j++) {
        if (imageIds[i] == $scope.images[j].id) {
          var re = new RegExp("\\[imgid"+imageIds[i]+"\\]", "g")
          console.log("[imgid"+imageIds[i]+"]", $scope.images[j].id)
          $scope.log.preview=$scope.log.preview.replace(re, '<img src="static'+$scope.images[j].location+'preview/'+$scope.images[j].name+'">')
        }
      }
    }
  }


  $scope.HTTPPostSuccess = function (data, status) {
    console.log('done')
  }

  $scope.updateImageMetadata = function () {
    images_json = JSON.stringify($scope.images, null, 0)
    console.log(images_json)
    $http({
        url:'/update_image_metadata',
        data: images_json,
        method: 'POST',
        headers : {'Content-Type':'application/json; charset=UTF-8'}
      }).success($scope.HTTPPOSTSuccess);
  }



  $scope.insertImageTag = function(imageId) {
    tinyMCE.execCommand("mceInsertContent", false, '<p>[imgid'+imageId.toString()+']</p><p></p>');
  };

};


