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
<div ng-init="images=${images}">
  <tabs>

  <pane class="paneContent" heading="Images" >
    <form class="form-horizontal" ng-submit="saveMetadata()" ng-controller="ImageCtrl">
      <input class="btn btn-small btn-primary" type="submit" name="btnSubmit" value="Save" />
        <hr>
      <div ng-repeat="image in images">
          <img src="static{{image.location}}preview/{{image.name}}">
          <div class="img_metadata">
              <div class="control-group">
                <label class="control-label" for="inputTitle">image title</label>
                <div class="controls">
                  <input type="text" name="inputTitle-{{image.id}}" ng-model="image.title" placeholder="Title of the image" value="{{image.title}}">
                </div>
              </div>
              <div class="control-group">
                <label class="control-label" for="inputComment">image comment</label>
                <div class="controls">
                  <textarea name="inputComment" ng-model="image.comment" placeholder="Comment for this image" value="{{image.comment}}"></textarea>
                </div>
              </div>
              <div class="control-group">
                <label class="control-label" for="inputAlt">text description</label>
                <div class="controls">
                  <input type="text" name="inputAlt" ng-model="image.alt" placeholder="Description of image content" value="{{image.alt}}">
                </div>
              </div>
         </div>
        <hr>
      </div>
      <input class="btn btn-small btn-primary" type="submit" name="btnSubmit" value="Save" />
   </form>
   </pane>



   <pane class="paneContent" heading="Editor">
      <textarea ui-tinymce ng-model="tinymce"></textarea>
   </pane>


   <pane class="paneContent" heading="Add Images">
      <form action="/fileupload" method="post" accept-charset="utf-8" enctype="multipart/form-data">
             <div class="control-group">
                 <div class="controls">
                    <div><input type="file" name="files" multiple='multiple'/></div>
                    <div><input class="btn btn-small btn-primary" type="submit" name="btnSubmit" value="Add Images" /></div>
                    <label class="checkbox"><input type="checkbox" name="upload" checked/> Upload</label>
                 </div>
             </div>
        </form>
    </pane>
  </tabs>
</div>
</body>
</html>

