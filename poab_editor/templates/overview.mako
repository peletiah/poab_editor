<%inherit file='base.mako' />

<%include file='header.mako' />

<div ng-init="logs=${logs}" ng-controller="OverviewCtrl">

  <alert ng-repeat="alert in alerts" type="alert.type" close="closeAlert($index)">{{alert.msg}}</alert>
  <div ng-repeat="(index, log) in logs">
    <div ng-show="log.id">
      <div>
        <a href="/editor/{{log.id}}" title="Edit">{{log.topic}}</a>
        &nbsp;         
        <a href="/editor/{{log.id}}" title="Edit">
          <span class="icon-pencil"></span>
        </a>

        <a title="Preview" colorbox transition="fade", speed=350, href="/preview?logid={{log.id}}">
          <span class="icon-eye-open"></span>
        </a>

        <a href="#" title="Delete" ng-click="confirmDelete(log)">
          <span class="icon-remove"></span>
        </a>

        <a href="#" title="Sync to server" ng-click="syncToServer(log, log.id)" ng-hide="syncInProgress[log.id]">
          <span class="icon-refresh"></span>
        </a>

        <span class="opaque">
          <span class="icon-refresh" ng-show="syncInProgress[log.id]"></span>
        </span>

        <a href="#" title="Show Sync Details" ng-click="toggleDetails(log.id)" ng-show="DetailsHidden(log.id)">
          <span class="icon-zoom-in"></span>
        </a>

        <a href="#" title="Hide Sync Details" ng-click="toggleDetails(log.id)" ng-show="displayDetails[log.id]">
          <span class="icon-zoom-out"></span>
        </a>
      </div>

      <div>
        <small>created on {{log.created}} by {{log.author}}</small>
      </div>

      <ul ng-repeat="image in log.images" ng-show="displayDetails[log.id]">
        <li>
          <img src="/static{{image.location}}thumbs/{{image.name}}">
          <span class="syncStatus">
            <span ng-show="imageSynced[image.id]" class="icon-ok"></span>
            <span ng-show="isImageTransferring[image.id]" class='loading'></span>
          </span>
        </li>
      </ul>
      <hr>
    </div>
  </div>

