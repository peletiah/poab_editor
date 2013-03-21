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


  $scope.syncImg = function(image) {
    $http({
      url: '/sync',
      data: image,
      method: 'POST',
      headers : {'Content-Type':'application/json; charset=UTF-8'}
    }).success($scope.syncImgSuccess);
  };

  $scope.syncImgSuccess = function(data, status) {
      console.log('Success')
      if (status = '200') {
        $scope.alerts.push({type: 'success', msg: 'Image "'+data+'" has been synced to server'});
        $timeout(function() {$scope.closeAlert(0)}, 1000)
      } else {
      console.log('Error!'+status)
      $scope.alerts.push({type: 'error', msg: 'Error while syncing Image: '+data+', Status Code: '+status});
      };
    };

  $scope.syncToServer = function(log) {
    $scope.active = true
    for (i in log.images) {
      console.log(log.images[i])
      $scope.syncImg(log.images[i])
    }
  }

}



var EditorCtrl = function ($scope, $http, $timeout) {

// ## GENERAL FUNCTIONS ##

 $scope.closeAlert = function(index) {
    $scope.alerts.splice(index, 1);
  };


  $scope.alerts = [];



// ## LOG FUNCTIONS ##

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


  //inserts 'imgid'-tag in tinyMCE when an image in log-tab is clicked
  $scope.insertImageTag = function(imageId) {
    tinyMCE.execCommand("mceInsertContent", false, '<p>[imgid'+imageId.toString()+']</p><p></p>');
  };


// ## IMAGE FUNCTIONS ##

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
      }
      fd.append("upload", $scope.upload)
      console.log(fd)
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


