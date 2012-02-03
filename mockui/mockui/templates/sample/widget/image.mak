<script>
  $("#image_widget_area img").live("click", function(){
     service.WidgetDialogService.finish_dialog(this);
    });
</script>
<div id="image_widget_area">
  <img src="/static/img/samples/1.jpg"/>
  <img src="/static/img/samples/2.jpg"/>
  <img src="/static/img/samples/3.jpg"/>
  <img src="/static/img/samples/4.jpg"/>
  <img src="/static/img/samples/5.jpg"/>
  <img src="/static/img/samples/6.jpg"/>
  <img src="/static/img/samples/7.jpg"/>
</div>

