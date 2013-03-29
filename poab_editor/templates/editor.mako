<%inherit file='base.mako' />


<%include file='header.mako' />

<div ng-init="images=${images}; log=${log}; tracks=${tracks}" ng-controller="EditorCtrl">
<tabs>



   <pane class="paneContent" heading="Editor" active="pane.active">
      <div>
        <input type="text" ng-model="log.topic" placeholder="Topic">
      </div>
      <div class="tinymc">
        <textarea ui-tinymce ng-model="log.content"></textarea>
       <div>
      <button class="btn btn-small btn-primary" id="preview" colorbox transition="fade", speed=350, href="/preview?logid={{log.id}}">preview</button>
      <button class="btn btn-small btn-primary" id="save" ng-click="saveLog()">save</button>
      <alert ng-repeat="alert in alerts" type="alert.type" close="closeAlert($index)">{{alert.msg}}</alert>
      </div>
      </div>
      <div class="overflow">
        <div ng-repeat="image in images">
          <div class="overflowContent" ng-show="image.id"> <!-- only display this section if the image.id is not null -->
            <a ng-click="insertImageTag(image.id)" href="#">
              <img src="/static{{image.location}}150/{{image.name}}">
            </a>
            <span class="imgid">{{image.id}}</span>
          </div>
        </div>
      </div>
     <hr>
   </pane>

  <pane class="paneContent" heading="Images" active="pane.active">
    <div>
      <div>
        <input type="file" ng-model-instant id="fileToUpload" multiple onchange="angular.element(this).scope().setFiles(this)" />
        <label class="checkbox"><input ng-model="upload" type="checkbox" name="upload"/> Upload</label>
      </div>
      <div ng-show="files.length">
        <ul ng-repeat="file in files.slice(0)">
          <li>
            <span>{{file.webkitRelativePath || file.name}}</span>
            (<span ng-switch="file.size > 1024*1024">
              <span ng-switch-when="true">{{file.size / 1024 / 1024 | number:2}} MB</span>
              <span ng-switch-default>{{file.size / 1024 | number:2}} kB</span>
            </span>)
           </li>
        </ul>
        <input class="btn btn-small btn-primary" type="button" ng-click="uploadFile('image')" value="Add files" />
      </div>
      <div ng-show='progressVisible'>
        <img src='/static/images/icons/load_indicator.gif'> <small>Adding files, please wait...</small>
      </div>
    </div>
    <alert ng-repeat="alert in alerts" type="alert.type" close="closeAlert($index)">{{alert.msg}}</alert>
    <form class="form-horizontal" ng-submit="updateImageMetadata()">
     <hr>
     <input ng-show="images[1].id" class="btn btn-small btn-primary" type="submit" name="btnSubmit" value="Save" />
     <hr>
     <div ng-repeat="image in images | filter:query">
        <div ng-show="image.id"> <!-- only display this section if the image.id is not null -->
          <img src="/static{{image.location}}500/{{image.name}}">
          <div class="metadata">
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
      </div>
      <div ng-show="images[0].id"><input class="btn btn-small btn-primary" type="submit" name="btnSubmit" value="Save" /></div>
   </form>
   </pane>

  <pane class="paneContent" heading="Track" active="pane.active">
    <div>
      <div>
        <input type="file" ng-model-instant id="fileToUpload" multiple onchange="angular.element(this).scope().setFiles(this)" />
        <label class="checkbox"><input ng-model="upload" type="checkbox" name="upload"/> Upload</label>
      </div>
      <div ng-show="files.length">
        <ul ng-repeat="file in files.slice(0)">
          <li>
            <span>{{file.webkitRelativePath || file.name}}</span>
            (<span ng-switch="file.size > 1024*1024">
              <span ng-switch-when="true">{{file.size / 1024 / 1024 | number:2}} MB</span>
              <span ng-switch-default>{{file.size / 1024 | number:2}} kB</span>
            </span>)
           </li>
        </ul>
        <input class="btn btn-small btn-primary" type="button" ng-click="uploadFile('track')" value="Add files" />
      </div>
      <div ng-show='progressVisible'>
        <img src='/static/images/icons/load_indicator.gif'> <small>Adding files, please wait...</small>
      </div>
    </div>
    <alert ng-repeat="alert in alerts" type="alert.type" close="closeAlert($index)">{{alert.msg}}</alert>
    <hr>
    <ul ng-repeat="track in tracks | filter:query">
      <div ng-show="track.id"> <!-- only display this section if the image.id is not null -->
        <li>{{track.location}}{{track.name}}</li>
      </div>
    </ul>

    </pane>



  </tabs>
</div>

