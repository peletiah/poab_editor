<!doctype html>
<html lang="en" ng-app='editor'>
<head>
  <meta charset="utf-8">
  <title>poab Editor</title>
 <link rel="stylesheet" href="/static/css/preview.css">
</head>
<body>

  <div>
    <div class="logdetail">
    <div class="logheader">
      <span class="logheader_left">${log.created.strftime("%B %d, %Y")}</span>
      <span class="logheader_right"><a  rel="map_colorbox" href="/track/simple/314733" title="View location of this entry on a map">Vienna, Austria</a></span>
    </div>
    <div class="logcontent">
      <h2>
        <a title="Permanent link to this journal-entry">${log.topic}</a>
      </h2>
    <h3></h3>
    <div class="logdetail_icons">
    </div>
    <div class="logtext">
      ${preview | n}
    </div>
      <span class="txt_icon">
        <a title="Permanent link to this journal-entry"></a>
      </span>
  </div>
</body>
</html>

