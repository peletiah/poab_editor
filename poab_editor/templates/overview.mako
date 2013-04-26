<%inherit file='base.mako' />

<%include file='header.mako' />

<div ng-init="logs=${logs}" ng-controller="OverviewCtrl">

  <alert ng-repeat="alert in alerts" type="alert.type" close="closeAlert($index)">{{alert.msg}}</alert>
  <div ng-repeat="log in logs">
    <div ng-show="log.id">
      <div>
        <a class="toolbar" href="/editor/{{log.id}}" title="Edit">{{log.topic}}</a>
        <a class="toolbar" href="/editor/{{log.id}}" title="Edit">
          <span class="icon-pencil"></span></a>

        <a class="toolbar" title="Preview" colorbox transition="fade", speed=350, href="/preview?logid={{log.id}}">
          <span class="icon-eye-open"></span></a>

        <a class="toolbar" href="#" title="Delete" ng-click="confirmDelete(log)">
          <span class="icon-remove"></span></a>

        <a class="toolbar" href="#" title="Sync to server" ng-click="syncToServer(log)" ng-hide="syncInProgress[log.id]">
          <span class="icon-refresh"></span></a>

        <span class="toolbar opaque">
          <span class="icon-refresh" ng-show="syncInProgress[log.id]"></span>
        </span>

        <a class="toolbar" href="#" title="Show Sync Details" ng-click="toggleDetails(log)" ng-show="DetailsHidden(log)">
          <span class="icon-zoom-in"></span></a>

        <a class="toolbar" href="#" title="Hide Sync Details" ng-click="toggleDetails(log)" ng-show="displayDetails[log.id]">
          <span class="icon-zoom-out"></span></a>
      </div>

      <div>
        <small>created on {{log.created}} by {{log.author}}</small>
      </div>
      <ul ng-show="displayDetails[log.id]">
        <li>
          {{isItemSynced[log.id][log.uuid]}}
          {{log.topic}} (Log)
          <span class="syncStatus">
            <span ng-show="isItemSynced[log.id][log.uuid]=='sync_in_progress'" class='loading'></span>
            <span ng-show="isItemSynced[log.id][log.uuid]=='was_synced'" class='icon-check'></span>
            <span ng-show="isItemSynced[log.id][log.uuid]=='is_synced'" class="icon-ok"></span>
            <span ng-show="isItemSynced[log.id][log.uuid]=='sync_error'" class="icon-warning-sign"></span>
          </span>
        </li>
      </ul>

      <ul ng-repeat="image in log.images" ng-show="displayDetails[log.id]">
        <li>
          {{isItemSynced[log.id][image.uuid]}}
          <img src="/static{{image.location}}150/{{image.name}}">
          <span class="syncStatus">
            <span ng-show="isItemSynced[log.id][image.uuid]=='sync_in_progress'" class='loading'></span>
            <span ng-show="isItemSynced[log.id][image.uuid]=='was_synced'" class='icon-check'></span>
            <span ng-show="isItemSynced[log.id][image.uuid]=='is_synced'" class='icon-ok'></span>
            <span ng-show="isItemSynced[log.id][image.uuid]=='sync_error'" class='icon-warning-sign'></span>
          </span>
        </li>
      </ul>
      <ul ng-repeat="track in log.tracks" ng-show="displayDetails[log.id]">
        <li>
          {{isItemSynced[log.id][track.uuid]}}
          {{track.name}}
          <span class="syncStatus">
            <span ng-show="isItemSynced[log.id][track.uuid]=='sync_in_progress'" class='loading'></span>
            <span ng-show="isItemSynced[log.id][track.uuid]=='was_synced'" class='icon-check'></span>
            <span ng-show="isItemSynced[log.id][track.uuid]=='is_synced'" class='icon-ok'></span>
            <span ng-show="isItemSynced[log.id][track.uuid]=='sync_error'" class='icon-warning-sign'></span>
          </span>
        </li>
      </ul>

      <hr>
    </div>
  </div>

