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




  $scope.syncImgSuccess = function(data, status) {
      console.log('Success')
      if (status = '200') {
        $scope.imageSynced[data.image_id] = true;
        $scope.isImageTransferring[data.image_id] = false;
      } else {
      console.log('Error!'+status)
      $scope.alerts.push({type: 'error', msg: 'Error while syncing Image: '+data+', Status Code: '+status});
      };
      image_id = data.image_id
      log_id = data.log_id
      $scope.itemsSynced[image_id]=true
      console.log('sync'+$scope.itemsSynced.every(allSynced))
      if ($scope.itemsSynced.every(allSynced)) {
        $timeout(function() {
          $scope.syncInProgress[log_id]=false;
          $scope.displayDetails[log_id]=false;
        }, 4000)
      };
    };

  function allSynced(element, index, array) {
    return (element == true);
  }


  $scope.syncImg = function(image, log) {
    data={}
    data['image']=image;
    data['log']=log;
    $scope.isImageTransferring[image.id] = true;
    $scope.imageSynced[image.id] = false;
    $http({
      url: '/sync',
      data: data,
      method: 'POST',
      headers : {'Content-Type':'application/json; charset=UTF-8'}
    }).success($scope.syncImgSuccess);
  };



$scope.displayDetails = [];
$scope.syncInProgress = [];
$scope.itemsSynced = [];
$scope.imageSynced=[];
$scope.isImageTransferring=[];
$scope.allSynced = false;

  $scope.toggleDetails = function(index){
      if ($scope.displayDetails[index] == false) {
        $scope.displayDetails[index] = true
      } else {
        $scope.displayDetails[index] = false;
      }
  };

  $scope.DetailsHidden = function(index) {
      return (($scope.displayDetails[index] == false) && ($scope.syncInProgress[index] == true));
  }
 
  $scope.syncToServer = function(log, index) {
    //$scope.activeIndex = index; //was activated, show details
    $scope.displayDetails[index] = true;
    $scope.syncInProgress[index] = true;
    for (i in log.images) {
      //$timeout(function() {
      //  $scope.syncInProgress[index]=false; 
      //  $scope.displayDetails[index] = false;
      //}, 3000)
      $scope.itemsSynced[log.images[i].id] = false
      console.log($scope.itemsSynced)
      $scope.syncImg(log.images[i],log)
      console.log($scope.itemsSynced.every(allSynced))
    }
  }

}


