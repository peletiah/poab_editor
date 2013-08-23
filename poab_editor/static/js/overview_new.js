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
          for (var i=0; i < $scope.logs.length; i++) {
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
  for (var i=0; i < log.images.length; i++) {
    //console.log(log.images[i].uuid)
    $scope.itemSyncState(log.images[i].uuid, log.id, 'sync_in_progress')
  }
  for (var i=0; i < log.tracks.length; i++) {
    $scope.itemSyncState(log.tracks[i].uuid, log.id, 'sync_in_progress')
  }
  //do the actual sync to the server
  for (var i=0; i < log.images.length; i++) {
    $scope.syncItem(log.images[i], log, 'image')
  }
  for (var i=0; i < log.tracks.length; i++) {
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
    $scope.syncedItems.pushIfNotExist(data, function(e) {
      return e.item_uuid === data.item_uuid;
    });
    
    //console.log('syncedItems are next')
    //console.log($scope.syncedItems)
    //console.log('=====')
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
  //console.log(items_sync_state)
  //console.log(items_sync_state.length)
  for (var i=0; i < items_sync_state.length; i++) {
    console.log(items_sync_state[i])
    all_sync_states.pushIfNotExist(items_sync_state[i], function(e) {
      return e.item_uuid === items_sync_state[i].item_uuid;
    }) //we need an array of sync_states for the allTrue-function
    console.log(all_sync_states)
  }
  //console.log(all_sync_states)
  all_synced=all_sync_states.every(allTrue) //test if all items are in sync
  console.log(all_synced)
  return all_synced
}

function allTrue(element, i, array) {
  console.log(element, i, array)
  return ((element.state == 'was_synced') || (element.state == 'is_synced'))
}


function interlinkAllRemoteItems(syncedItems) {
    for ( var i=0; i < syncedItems.length; i++ ) {
      type=syncedItems[i].type
      //console.log(syncedItems[i].type+': ', syncedItems[i].item_uuid)
      //console.log(syncedItems[i])
      //console.log(data)

      $http({
          url: '/sync?interlink',
          data: syncedItems[i],
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
  console.log('interlink finished')
};


$scope.itemSyncState = function(item_uuid, log_id, state) {
  //console.log(item_uuid)
  $scope.isItemSynced[log_id].pushIfNotExist({state: state, item_uuid: item_uuid}, function(e) {
      return e.item_uuid === data.item_uuid;
    });
  //console.log($scope.isItemSynced)
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

// check if an element exists in array using a comparer function
// comparer : function(currentElement)
Array.prototype.inArray = function(comparer) { 
    for(var i=0; i < this.length; i++) { 
        if(comparer(this[i])) return true; 
    }
    return false; 
};


// adds an element to the array if it does not already exist using a comparer 
// function
Array.prototype.pushIfNotExist = function(element, comparer) { 
    if (!this.inArray(comparer)) {
        this.push(element);
    }
};

 

}


