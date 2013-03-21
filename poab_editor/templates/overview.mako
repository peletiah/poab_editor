<%inherit file='base.mako' />

<%include file='header.mako' />

<div ng-init="logs=${logs}" ng-controller="OverviewCtrl">

  <alert ng-repeat="alert in alerts" type="alert.type" close="closeAlert($index)">{{alert.msg}}</alert>
  <div ng-repeat="log in logs">
    <div ng-show="log.id">
      <div>
        <a href="/editor/{{log.id}}" title="Edit">{{log.topic}}</i></a>&nbsp; 
        <a href="/editor/{{log.id}}" title="Edit"><i class="icon-pencil"></i></a>
        <a title="Preview" colorbox transition="fade", speed=350, href="/preview?logid={{log.id}}"><i class="icon-eye-open"></i></a>
        <a href="#" title="Delete" ng-click="confirmDelete(log)"><i class="icon-trash"></i></a>
        <a href="#" title="Sync to server" ng-click="syncToServer(log)"><i class="icon-refresh"></i></a>
      </div>
      <div><small>created on {{log.created}} by {{log.author}}</small></div>
      <ul ng-repeat="image in log.images" ng-show="active">
        <li><img src="/static{{image.location}}thumbs/{{image.name}}"></li>
      </ul>
      <hr>
    </div>
  </div>

