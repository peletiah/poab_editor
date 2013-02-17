<!doctype html>
<html lang="en" ng-app='editor'>
<head>
  <meta charset="utf-8">
  <title>poab Editor</title>
  <link rel="stylesheet" href="/static/css/bootstrap/css/bootstrap.css">
  <link rel="stylesheet" href="/static/css/layout.css">
  <link rel="stylesheet" href="/static/css/fileupload.css">
  <link rel="stylesheet" href="/static/css/jquery-ui/jquery-ui.css">
  <script type="text/javascript" src="/static/lib/jquery/1.9.0/jquery.min.js"></script>
  <script type="text/javascript" src="/static/lib/jqueryui/1.10.0/jquery-ui.min.js"></script>
  <script type="text/javascript" src="/static/lib/angularjs/1.0.4/angular.js"></script>
  <script type="text/javascript" src="/static/lib/angular-ui-0.3.2/build/angular-ui.js"></script>
  <script type="text/javascript" src="/static/lib/ng-bootstrap/ui-bootstrap-tpls-0.1.0.js"></script>
  <script type="text/javascript" src="/static/lib/tinymce/3.5.8/tiny_mce_src.js"></script>
  <script type="text/javascript" src="/static/lib/tinymce/3.5.8/jquery.tinymce.js"></script>
  <script src="/static/js/controllers.js"></script>
  <script src="/static/js/fileupload.js"></script>
</head>
<body>
<div>
  <tabs>
   <pane class="paneContent" heading="Images">
    <div ng-include src="'/static/fileupload.html'"></div>
    </pane>
    <pane class="paneContent" heading="Editor">
      <textarea ui-tinymce ng-model="tinymce"></textarea>
    </pane>
  </tabs>
</div>
</body>
</html>

