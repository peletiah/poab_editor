var EditorModule = angular.module('editor', ['ui.bootstrap','ui.directives'], 
  function($compileProvider) {
    // configure new 'compile' directive by passing a directive
    // factory function. The factory function injects the '$compile'
    $compileProvider.directive('compile', function($compile) {
      // directive factory creates a link function
      return function(scope, element, attrs) {
        scope.$watch(
          function(scope) {
             // watch the 'compile' expression for changes
            return scope.$eval(attrs.compile);
          },
          function(value) {
            // when the 'compile' expression changes
            // assign it into the current DOM
            element.html(value);
 
            // compile the new DOM and link it to the current
            // scope.
            // NOTE: we only compile .childNodes so that
            // we don't get into infinite loop compiling ourselves
            $compile(element.contents())(scope);
          }
        );
      };
    })
  }
);

EditorModule.directive('colorbox', function($http, $compile, $parse) {
  var colorboxDefinition = {
    restrict: 'AC',    
    link: function (scope, element, attributes, ngModel) {
            element.on("click", function(e) {
              e.preventDefault();
              $http.get(attributes.href).success(function(data) {
                console.log(attributes.transition)
                console.log(attributes.html)
                $.colorbox({
                    html : attributes.html || $compile(data)(scope),
                    transition : attributes.transition || "elastic",
                    speed : parseInt(attributes.speed || 350),
                    title : attributes.title || false,
                    scrolling : (attributes.scrolling ? /^true$/i.test(attributes.Scrolling) : true),
                    opacity : parseFloat(attributes.opacity || 0.85),
                    escKey : (attributes.escKey ? /^true$/i.test(attributes.EscKey) : true),
                    width : attributes.width || false,
                    height : attributes.height || false,
                    innerWidth : attributes.innerWidth || false,
                    innerHeight : attributes.innerHeight || false,
                    initialWidth : attributes.initialWidth || 300,
                    initialHeight : attributes.initialHeight || 100,
                    maxWidth : attributes.maxWidth || false,
                    maxHeight : attributes.maxHeight || false,
                    fixed : attributes.fixed || false,
                    top : attributes.top || false,
                    bottom : attributes.bottom || false,
                    left : attributes.left || false,
                    right : attributes.right || false,
                    onOpen : (attributes.onOpen ? (scope.registeredCallbacks && scope.registeredCallbacks.hasOwnProperty(attributes.onOpen) ? scope.registeredCallbacks[attributes.onOpen]() : false) : false),
                    onLoad : (attributes.onLoad ? (scope.registeredCallbacks && scope.registeredCallbacks.hasOwnProperty(attributes.onLoad) ? scope.registeredCallbacks[attributes.onLoad]() : false) : false),
                    onComplete : (attributes.onComplete ? (scope.registeredCallbacks && scope.registeredCallbacks.hasOwnProperty(attributes.onComplete) ? scope.registeredCallbacks[attributes.onComplete]() : false) : false),
                    onCleanup : (attributes.onCleanup ? (scope.registeredCallbacks && scope.registeredCallbacks.hasOwnProperty(attributes.onCleanup) ? scope.registeredCallbacks[attributes.onCleanup]() : false) : false),
                    onClosed : (attributes.onClosed ? (scope.registeredCallbacks && scope.registeredCallbacks.hasOwnProperty(attributes.onClosed) ? scope.registeredCallbacks[attributes.onClosed]() : false) : false)
                })
            })
          })
    }
  }
  return colorboxDefinition;  
})

EditorModule.directive('datePicker', function ($parse) {
    return function (scope, element, attrs, controller) {
        var ngModel = $parse(attrs.ngModel);
        $(function(){
            element.datepicker({
                format: 'yyyy-mm-dd',
                weekStart: 1})
                .on('changeDate', function (ev) {
                    var dd = ev.date.getDate()
                    var mm = ev.date.getMonth()+1;//January is 0! 
                    var yyyy = ev.date.getFullYear(); 
                    if(dd<10){dd='0'+dd} 
                    if(mm<10){mm='0'+mm}
                    console.log(yyyy+'-'+mm+'-'+dd)
                    scope.$apply(function(scope){
                        // Change binded variable
                        ngModel.assign(scope, yyyy+'-'+mm+'-'+dd);
                    });
                })
        })
    }
});


// TinyMCE Parameters
EditorModule.value('ui.config', {
   tinymce: {
      theme: 'advanced',
      theme_advanced_buttons1 : "bold, italic, underline, undo, redo,separator,code,link,bullist",
      theme_advanced_buttons2 : "",
      theme_advanced_buttons3 : "",
      theme_advanced_source_editor_width : 700,
      theme_advanced_source_editor_height : 600,
      theme_advanced_source_editor_wrap : false,
      theme_advanced_resizing : true,
      theme_advanced_resizing_max_width : 500,
      plugins: "paste",
      theme_advanced_buttons1_add : "pastetext",
      paste_auto_cleanup_on_paste : true,
      paste_text_sticky : true,
      paste_text_sticky_default : false,
   }
});
