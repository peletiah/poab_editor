var EditorModule = angular.module('editor', ['ui.bootstrap','ui.directives'], 
  function($compileProvider) {
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
  }
);

EditorModule.directive('colorbox', function($http, $compile, $parse) {
  var colorboxDefinition = {
    restrict: 'AC',    
    link: function (scope, element, attributes, ngModel) {
            element.on("click", function(e) {
              e.preventDefault();
              $http.get(attributes.href).success(function(data) {
                console.log(attributes.transition)
                console.log(attributes.html)
                $.colorbox({
                    html : attributes.html || $compile(data)(scope),
                    transition : attributes.transition || "elastic",
                    speed : parseInt(attributes.speed || 350),
                    title : attributes.title || false,
                    scrolling : (attributes.scrolling ? /^true$/i.test(attributes.Scrolling) : true),
                    opacity : parseFloat(attributes.opacity || 0.85),
                    escKey : (attributes.escKey ? /^true$/i.test(attributes.EscKey) : true),
                    width : attributes.width || false,
                    height : attributes.height || false,
                    innerWidth : attributes.innerWidth || false,
                    innerHeight : attributes.innerHeight || false,
                    initialWidth : attributes.initialWidth || 300,
                    initialHeight : attributes.initialHeight || 100,
                    maxWidth : attributes.maxWidth || false,
                    maxHeight : attributes.maxHeight || false,
                    fixed : attributes.fixed || false,
                    top : attributes.top || false,
                    bottom : attributes.bottom || false,
                    left : attributes.left || false,
                    right : attributes.right || false,
                    onOpen : (attributes.onOpen ? (scope.registeredCallbacks && scope.registeredCallbacks.hasOwnProperty(attributes.onOpen) ? scope.registeredCallbacks[attributes.onOpen]() : false) : false),
                    onLoad : (attributes.onLoad ? (scope.registeredCallbacks && scope.registeredCallbacks.hasOwnProperty(attributes.onLoad) ? scope.registeredCallbacks[attributes.onLoad]() : false) : false),
                    onComplete : (attributes.onComplete ? (scope.registeredCallbacks && scope.registeredCallbacks.hasOwnProperty(attributes.onComplete) ? scope.registeredCallbacks[attributes.onComplete]() : false) : false),
                    onCleanup : (attributes.onCleanup ? (scope.registeredCallbacks && scope.registeredCallbacks.hasOwnProperty(attributes.onCleanup) ? scope.registeredCallbacks[attributes.onCleanup]() : false) : false),
                    onClosed : (attributes.onClosed ? (scope.registeredCallbacks && scope.registeredCallbacks.hasOwnProperty(attributes.onClosed) ? scope.registeredCallbacks[attributes.onClosed]() : false) : false)
                })
            })
          })
    }
  }
  return colorboxDefinition;  
})


// TinyMCE Parameters
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
      theme_advanced_resizing_max_width : 500,
      plugins: "paste",
      theme_advanced_buttons1_add : "pastetext",
      paste_auto_cleanup_on_paste : true,
      paste_text_sticky : true,
      paste_text_sticky_default : true,
   }
});




// Controllers

var OverviewCtrl = function ($scope, $dialog, $http, $timeout){
  $scope.alerts=[];

  //delete specific log-entry, with confirmation-dialog
  $scope.confirmDelete = function(log){
    var title = log.topic;
    var msg = 'Are you sure you want to delete \''+log.topic+'\'\n, created on '+log.created+'?';
    var btns = [{result:'cancel', label: 'Cancel', cssClass: 'btn btn-small'}, {result:'ok', label: 'OK', cssClass: 'btn btn-primary btn-small'}];
    var log_json = JSON.stringify(log, null, 0);
     
    $dialog.messageBox(title, msg, btns)
      .open()
      .then(function(result){
        //has the user confirmed the dialog-box
        if (result == 'ok') {
          //delete log-entry from Database(via Backend-Server)
          $http({
            url: '/delete',
            data: log_json,
            method: 'POST',
            headers : {'Content-Type':'application/json; charset=UTF-8'}
          }).success($scope.deleteLogSuccess);
          //immediately delete log-entry from view($scope.logs-array)
          for (i in $scope.logs) {
            if ($scope.logs[i] == log) {
              delete $scope.logs[i]
            };
          };
        }
      });
  };
  
  $scope.deleteLogSuccess = function (data, status) {
    if (status = '200') {
      $scope.alerts.push({type: 'success', msg: 'Log "'+data+'" has been successfully deleted'});
      $timeout(function() {$scope.closeAlert(0)}, 3000)
    } else {
      console.log('Error!'+status)
      $scope.alerts.push({type: 'error', msg: 'Error while deleting Log: '+data+', Status Code: '+status});
    };
  };

 $scope.closeAlert = function(index) {
    $scope.alerts.splice(index, 1);
  };



}



var EditorCtrl = function ($scope, $http, $timeout) {
  $scope.alerts = [];

  //save log(updated or new), backend returns id
  $scope.saveLog = function() {
    $scope.log.images = $scope.images
    $scope.log.tracks = $scope.tracks
    console.log($scope.log)
    log_json = JSON.stringify($scope.log, null, 0)
    console.log(log_json)
    $http({
        url:'/save_log',
        data: log_json,
        method: 'POST',
        headers : {'Content-Type':'application/json; charset=UTF-8'}
    }).success($scope.saveLogSuccess);
  }

  $scope.saveLogSuccess = function (data, status) {
    if (status = '200') {
      $scope.log.id = data;
      $scope.alerts.push({type: 'success', msg: 'Log successfully saved!'});
      $timeout(function() {$scope.closeAlert(0)}, 3000)
    } else {
      console.log('Error!'+status)
      $scope.alerts.push({type: 'error', msg: 'Error while saving Log: '+status});
    };
  };


  $scope.updatePreview = function() {
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

  $scope.updateImageMetadata = function () {
    images_json = JSON.stringify($scope.images, null, 0)
    $http({
        url:'/update_image_metadata',
        data: images_json,
        method: 'POST',
        headers : {'Content-Type':'application/json; charset=UTF-8'}
      }).success($scope.saveMetadataSuccess);
  }

  $scope.saveMetadataSuccess = function (data, status) {
    if (status = '200') {
      $scope.alerts.push({type: 'success', msg: 'Image Metadata successfully saved!'});
      $timeout(function() {$scope.closeAlert(0)}, 3000)
    } else {
      console.log('Error!'+status)
      $scope.alerts.push({type: 'error', msg: 'Error while saving Image Metadata: '+status});
    };
  };



  $scope.insertImageTag = function(imageId) {
    tinyMCE.execCommand("mceInsertContent", false, '<p>[imgid'+imageId.toString()+']</p><p></p>');
  };

 $scope.closeAlert = function(index) {
    $scope.alerts.splice(index, 1);
  };


    $scope.upload = true
    $scope.setFiles = function(element) {
      console.log($scope.upload)
      $scope.$apply(function($scope) {
        console.log('files:', element.files);
        // Turn the FileList object into an Array
        $scope.files = []
        for (var i = 0; i < element.files.length; i++) {
          $scope.files.push(element.files[i])
        }
        $scope.progressVisible= false
      });
    };

    $scope.uploadFile = function(filetype) {
        var fd = new FormData()
        for (var i in $scope.files) {
            fd.append("uploadedFile", $scope.files[i])
            fd.append("upload", $scope.upload)
        }
        var xhr = new XMLHttpRequest()
        xhr.upload.addEventListener("progress", uploadProgress, false)
        xhr.addEventListener("load", uploadComplete, false)
        xhr.addEventListener("error", uploadFailed, false)
        xhr.addEventListener("abort", uploadCanceled, false)
        xhr.open("POST", "/fileupload?type="+filetype)
        $scope.progressVisible = true
        xhr.send(fd)
    }

    function uploadProgress(evt) {
        $scope.$apply(function(){
            if (evt.lengthComputable) {
                $scope.progress = Math.round(evt.loaded * 100 / evt.total)
            } else {
                $scope.progress = 'unable to compute'
            }
        })
    }

    function uploadComplete(evt) {
        /* This event is raised when the server send back a response */
        $scope.$apply( function(){
          files_json = JSON.parse(evt.target.responseText)
          console.log(files_json)
          //has a trackfile or images been uploaded?
          if ( files_json['tracks'] ) {
            var filetype = 'tracks'
          } else if ( files_json['images'] ) { 
            var filetype = 'images'
          };
          //adding files to $scope, if they are not in $scope yet
          console.log('Server response was json with '+filetype+', trying to add them to scope')
          for (var i = 0; i < files_json[filetype].length; i++) {
            var hashmatch = false;
            for ( var j = 0; j < $scope.tracks.length; j++) {
              if ( files_json[filetype][i].hash == $scope.tracks[j].hash ) {
                hashmatch = true;
                console.log('hashmatch found, already in $scope');
              };
            };
            if ( hashmatch == false) {
              console.log('this file is not in $scope yet, we will add it');
              console.log(files_json[filetype][i].hash)
              if ( filetype == 'tracks' ) { 
                $scope.tracks.push(files_json[filetype][i])
              } else if ( filetype == 'images' ) {
                $scope.images.push(files_json[filetype][i])
              } 
            }
          }
          $scope.progressVisible = false
          $scope.files.length = false
          $scope.alerts.push({type: 'success', msg: filetype+' have been successfully added'});
          $timeout(function() {$scope.closeAlert(0)}, 3000)
          if ($scope.log.id) {
            console.log($scope.log.id)
            $scope.saveLog()
          };
        })
    }

    function uploadFailed(evt) {
        alert("There was an error attempting to upload the file.")
    }

    function uploadCanceled(evt) {
        $scope.$apply(function(){
            $scope.progressVisible = false
        })
        alert("The upload has been canceled by the user or the browser dropped the connection.")
    }
};


