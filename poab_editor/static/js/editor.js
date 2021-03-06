// Controllers


var EditorCtrl = function ($scope, $dialog, $http, $timeout) {

// ## GENERAL FUNCTIONS ##

 $scope.closeAlert = function(index) {
    $scope.alerts.splice(index, 1);
  };


    
    $scope.list = [1,2,3];
    
    $scope.current = 0;
    

  $scope.alerts = [];



// ## LOG FUNCTIONS ##

  $scope.saveLog = function() {
    $scope.log.images = $scope.images
    $scope.log.tracks = $scope.tracks
    $scope.log.etappe = $scope.etappe
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
      console.log(data['log_id'])
      console.log(data['etappe_id'])
      console.log($scope.etappe)
      $scope.log.id = data['log_id'];
      $scope.etappe.id = data['etappe_id'];
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

var t = '<div class="modal-header">'+
          '<h3></h3>'+
          '</div>'+
          '<div class="modal-body">'+
          '<p>Enter a value to pass to <code>close</code> as the result: <input ng-model="result" /></p>'+
          '</div>'+
          '<div class="modal-footer">'+
          '<button ng-click="close(result)" class="btn btn-primary" >Close</button>'+
          '</div>';


  //delete specific image, with confirmation-dialog
  $scope.confirmDeleteImage = function(image){
    var msg = '<div class="modal-header">'+
              '<h3>Deleting image'+image.name+'</h3>'+
              '</div>'+
              '<div class="modal-body">'+
              '<p>Are you sure you want to delete <b>'+image.name+'</b>:</p>'+
              '<p><img src="/static'+image.location+'500/'+image.name+'"></p>'+
              '</div>'+
              '<div class="modal-footer">'+
              '<button ng-click="close(\'cancel\')" class="btn btn-small" >Cancel</button>'+
              '<button ng-click="close(\'ok\')" class="btn btn-small" >OK</button>'+
              '</div>';
    var btns = [{result:'cancel', label: 'Cancel', cssClass: 'btn btn-small'}, {result:'ok', label: 'OK', cssClass: 'btn btn-primary btn-small'}];
    var image_json = JSON.stringify(image, null, 0);
 
    $scope.opts = {
        backdrop: true,
        keyboard: true,
        backdropClick: true,
        template:  msg, // OR: templateUrl: 'path/to/view.html',
        controller: 'TestDialogController' 
      };
    
    $dialog.dialog($scope.opts)
      .open()
      .then(function(result){
        //has the user confirmed the dialog-box
        if (result == 'ok') {
          //delete image-entry from Database(via Backend-Server)
          $http({
            url: '/delete_image',
            data: image_json,
            method: 'POST',
            headers : {'Content-Type':'application/json; charset=UTF-8'}
          }).success($scope.deleteImageSuccess);
          //immediately delete image-entry from view($scope.images-array)
          for (i in $scope.images) {
            if ($scope.images[i].id == image.id) {
              delete $scope.images[i]
              console.log('delete',$scope['images'])
            };
          };
        }
      });
  };

 
  $scope.deleteImageSuccess = function (data, status) {
    if (status = '200') {
      $scope.alerts.push({type: 'success', msg: 'Image "'+data+'" has been successfully deleted'});
      $timeout(function() {$scope.closeAlert(0)}, 3000)
    } else {
      console.log('Error!'+status)
      $scope.alerts.push({type: 'error', msg: 'Error while deleting Image: '+data+', Status Code: '+status});
    };
  };


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
      /* This event is raised when the server sent back a response */
      $scope.$apply( function(){
        files_json = JSON.parse(evt.target.responseText)
        //has a trackfile or images been uploaded?
        if ( files_json['tracks'] ) {
          var filetype = 'tracks'
        } else if ( files_json['images'] ) { 
          var filetype = 'images'
        };
        //adding files to $scope, if they are not in $scope yet
        console.log('Server response was json with '+filetype+', trying to add them to scope')
        for (var i = 0; i < files_json[filetype].length; i++) {
          var uuidmatch = false;
          console.log('upload',$scope[filetype], $scope[filetype].length)
          for ( var j = 0; j < $scope[filetype].length; j++) {
            if ( typeof $scope[filetype][j] !== 'undefined') {
              if ( files_json[filetype][i].uuid == $scope[filetype][j].uuid ) {
                uuidmatch = true;
                console.log('uuidmatch found, object already in $scope');
              };
            }
          }
          if ( uuidmatch == false) {
            console.log('this object is not in $scope yet, we will add it');
            console.log(files_json[filetype][i].uuid)
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


function TestDialogController($scope, dialog){

  $scope.close = function(result){

    dialog.close(result);

  };

}
