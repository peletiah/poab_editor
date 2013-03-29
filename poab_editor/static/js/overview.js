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




// SYNC TO SERVER

$scope.displayDetails = [];
$scope.syncInProgress = [];
$scope.isItemSynced = [];



  $scope.syncToServer = function(log) {
    $scope.displayDetails[log.id] = true;
    $scope.syncInProgress[log.id] = true;
    $scope.isItemSynced[log.id]=[]
    //set Sync-State for all items to False
    $scope.syncItem('', log, 'log')
    $scope.itemSyncState(log.uuid, log.id, 'sync_in_progress')
    for (i in log.images) {
      $scope.itemSyncState(log.images[i].uuid, log.id, 'sync_in_progress')
    }
    for (i in log.tracks) {
      $scope.itemSyncState(log.tracks[i].uuid, log.id, 'sync_in_progress')
    }
    //do the actual sync to the server
    for (i in log.images) {
      $scope.syncItem(log.images[i], log, 'image')
    }
    for (i in log.tracks) {
      $scope.syncItem(log.tracks[i], log, 'track')
    }

  }

  $scope.syncItem = function(item, log, type) {
    data={}
    if (type=='image') {
      data['image']=item
    } else if (type=='track') {
      data['track']=item
    }
    data['log']=log;
    $http({
      url: '/sync?type='+type,
      data: data,
      method: 'POST',
      headers : {'Content-Type':'application/json; charset=UTF-8'}
    }).success($scope.syncItemSuccess);
  };


  $scope.syncItemSuccess = function(data, status) {
      console.log('Success')
      //console.log(data)
      item_uuid = data.item_uuid
      log_id = data.log_id
      sync_status = data.sync_status
      if (status = '200') {
        $scope.itemSyncState(item_uuid, log_id, sync_status)
      } else {
        console.log('Error!'+status)
        $scope.alerts.push({type: 'error', msg: 'Error while syncing Image: '+data+', Status Code: '+status});
      };
      if (allItemsSynced($scope.isItemSynced[log_id])) { //test if all items in array are true with function allItemsSynced
        $timeout(
        function() {
          $scope.syncInProgress[log_id]=false;
          $scope.displayDetails[log_id]=false;
          }, 4000)
      };
  };

  function allItemsSynced(items_sync_state) {
    all_synced=true
    for (each in items_sync_state) {
      if ((items_sync_state[each] == 'was_synced') || (items_sync_state[each] == 'is_synced')) {
        all_synced=true
      } else {
        all_synced=false
      }
    }
    return all_synced
  }

  $scope.itemSyncState = function(item_uuid, log_id, state) {
    $scope.isItemSynced[log_id][item_uuid]=state
  }


  $scope.toggleDetails = function(log){
      if ($scope.displayDetails[log.id] == false) {
        $scope.displayDetails[log.id] = true
      } else {
        $scope.displayDetails[log.id] = false;
      }
  };

  $scope.DetailsHidden = function(log) {
      return (($scope.displayDetails[log.id] == false) && ($scope.syncInProgress[log.id] == true));
  }
  

}


