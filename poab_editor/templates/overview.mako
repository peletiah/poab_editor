<!doctype html>
<html lang="en" ng-app='editor'>
<head>
  <meta charset="utf-8">
  <title>poab Editor</title>
  <link rel="stylesheet" href="/static/css/bootstrap/css/bootstrap.css">
  <link rel="stylesheet" href="/static/css/layout.css">
  <link rel="stylesheet" href="/static/css/jquery-ui/jquery-ui.css">
  <script type="text/javascript" src="/static/lib/jquery/1.9.0/jquery.min.js"></script>
  <script type="text/javascript" src="/static/lib/jqueryui/1.10.0/jquery-ui.min.js"></script>
  <script type="text/javascript" src="/static/lib/angularjs/1.0.4/angular.js"></script>
  <script type="text/javascript" src="/static/lib/angular-ui-0.3.2/build/angular-ui.js"></script>
  <script type="text/javascript" src="/static/lib/ng-bootstrap/ui-bootstrap-tpls-0.1.0.js"></script>
  <script type="text/javascript" src="/static/lib/tinymce/3.5.8/tiny_mce_src.js"></script>
  <script type="text/javascript" src="/static/lib/tinymce/3.5.8/jquery.tinymce.js"></script>
  <script src="/static/js/controllers.js"></script>
</head>
<body>
<div ng-init="logs=${logs}">
  <div>
    <a href="/editor">Add a new entry</a>
    <hr>
  </div>
  <div ng-repeat="log in logs">
    <div>'{{log.topic}}' <a href="/editor?logid={{log.id}}">edit</a></div>
    <div><small>created on {{log.created}}</small></div>
    <div compile="log.preview"></div>
    <hr>
  </div>
 </body>
</html>

