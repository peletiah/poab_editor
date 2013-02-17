//angular.module('editor', [], function() {})

FileUploadCtrl.$inject = ['$scope']

function FileUploadCtrl(scope) {
    scope.setFiles = function(element) {
    scope.$apply(function(scope) {
      console.log('files:', element.files);
      // Turn the FileList object into an Array
        scope.files = []
        for (var i = 0; i < element.files.length; i++) {
          scope.files.push(element.files[i])
        }
      scope.progressVisible = false
      });
    };

    scope.uploadFile = function() {
        var fd = new FormData()
        for (var i in scope.files) {
            fd.append("uploadedFile", scope.files[i])
        }
        var xhr = new XMLHttpRequest()
        xhr.upload.addEventListener("progress", uploadProgress, false)
        xhr.addEventListener("load", uploadComplete, false)
        xhr.addEventListener("error", uploadFailed, false)
        xhr.addEventListener("abort", uploadCanceled, false)
        xhr.open("POST", "/fileupload")
        scope.progressVisible = true
        xhr.send(fd)
    }

    function uploadProgress(evt) {
        scope.$apply(function(){
            if (evt.lengthComputable) {
                scope.progress = Math.round(evt.loaded * 100 / evt.total)
            } else {
                scope.progress = 'unable to compute'
            }
        })
    }

    function uploadComplete(evt) {
        /* This event is raised when the server send back a response */
        scope.$apply( function(){
          scope.filenames = []
          files_json = JSON.parse(evt.target.responseText)['files']
          for (var i = 0; i < files_json.length; i++) {
            scope.filenames.push(files_json[i])
          }
        })
    }

    function uploadFailed(evt) {
        alert("There was an error attempting to upload the file.")
    }

    function uploadCanceled(evt) {
        scope.$apply(function(){
            scope.progressVisible = false
        })
        alert("The upload has been canceled by the user or the browser dropped the connection.")
    }
}


