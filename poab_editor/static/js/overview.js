// Controllers

var OverviewCtrl = function ($scope, $dialog, $http, $timeout){
  $scope.alerts=[];


  //delete specific log-entry, with confirmation-dialog
  $scope.confirmDeleteLog = function(log){
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
          //$http({
          //  url: '/delete_log',
          //  data: log_json,
          //  method: 'POST',
          //  headers : {'Content-Type':'application/json; charset=UTF-8'}
          //}).success($scope.deleteLogSuccess);
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
$scope.syncedItems = [];



  $scope.syncToServer = function(log) {
    //unhide details-display while syncing
    $scope.displayDetails[log.id] = true;
    //hide sync-button while syncing
    $scope.syncInProgress[log.id] = true;
    $scope.isItemSynced[log.id]=[] //initialize isItemSynced-array
    $scope.syncItem('', log, 'log') //sync log

    //set Sync-State for all items to sync_in_progress
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
    console.log(data)
    $http({
      url: '/sync?type='+type,
      data: data,
      method: 'POST',
      headers : {'Content-Type':'application/json; charset=UTF-8'}
    }).success($scope.syncItemSuccess);
  };


  $scope.syncItemSuccess = function(data, status) {
      console.log(data)
      uuid_exists = false

      // make sure we only push new items to $scope.syncedItems
      // otherwise interlinkAllRemoteItems will be run multiple times for identical items
      for ( i in $scope.syncedItems ) {
        if ( data.item_uuid == $scope.syncedItems[i].item_uuid) {
          uuid_exists = true
        }
      };
      if ( !uuid_exists ) {
        $scope.syncedItems.push(data)
      };

      item_uuid = data.item_uuid
      log_id = data.log_id
      sync_status = data.sync_status
      if (status = '200') {
        $scope.itemSyncState(item_uuid, log_id, sync_status)
      } else {
        console.log('Error!'+status)
        $scope.alerts.push({type: 'error', msg: 'Error while syncing Image: '+data+', Status Code: '+status});
      };
      //console.log('allTimesSynced: '+allItemsSynced($scope.isItemSynced[log_id]));
      //test if all items in object are synced - if true, hide log-details after 4 sec
      if (allItemsSynced($scope.isItemSynced[log_id])) {
        interlinkAllRemoteItems($scope.syncedItems);
        };
  };

  function allItemsSynced(items_sync_state) {
    all_sync_states=[]

    for (each in items_sync_state) {
      all_sync_states.push(items_sync_state[each]) //we need an array of sync_states for the allTrue-function
    }
    all_synced=all_sync_states.every(allTrue) //test if all items are in sync
    return all_synced
  }

  function allTrue(element, index, array) {
    return ((element == 'was_synced') || (element == 'is_synced'))
  }


  function interlinkAllRemoteItems(syncedItems) {
      console.log(syncedItems)
      for ( index in syncedItems ) {
        type=syncedItems[index].type
        //console.log(syncedItems[index].type+': ', syncedItems[index].item_uuid)
        //console.log(syncedItems[index])
        //console.log(data)

        $http({
            url: '/sync?interlink',
            data: syncedItems[index],
            method: 'POST',
            headers : {'Content-Type':'application/json; charset=UTF-8'}
        }).success($scope.syncItemLinkSuccess);

      }

      $timeout(
        function() {
          $scope.syncInProgress[log_id]=false;
          $scope.displayDetails[log_id]=false;
          }, 4000)

  };

  $scope.syncItemLinkSuccess = function(data, status) {
    console.log(data)
  };


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
      //TODO: Throws error when deleting log!
      return (($scope.displayDetails[log.id] == false) && ($scope.syncInProgress[log.id] == true));
  }
  

}


