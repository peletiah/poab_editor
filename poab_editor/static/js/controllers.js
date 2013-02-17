var EditorModule = angular.module('editor', ['ui.bootstrap','ui.directives'])

EditorModule.value('ui.config', {
   tinymce: {
      theme: 'advanced',
      theme_advanced_buttons1 : "bold, italic, underline,undo,redo",
      theme_advanced_buttons2 : "",
      theme_advanced_buttons3 : "",
      theme_advanced_source_editor_width : 700,
      theme_advanced_source_editor_height : 600,
      theme_advanced_source_editor_wrap : false,
      theme_advanced_resizing : true
   }
});


function ImageCtrl($scope, $http) {
  $scope.metadataUpdateSuccess = function (data, status) {
    console.log('done')
  }


  $scope.saveMetadata = function () {
    images_json = JSON.stringify($scope.images, null, 0)
    console.log(images_json)
    $http({
        url:'/update_image_metadata',
        data: images_json,
        method: 'POST',
        headers : {'Content-Type':'application/json; charset=UTF-8'}
      }).success($scope.metadataUpdateSuccess);
  }
}
