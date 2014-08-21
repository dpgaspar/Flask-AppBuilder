$(document).ready(function() {
    $('.appbuilder_datetime').datetimepicker();
    $('.appbuilder_date').datetimepicker({
        pickTime: false });
    $(".my_select2").select2({placeholder: "Select a State", allowClear: true});
    $("a").tooltip({'selector': '','placement': 'bottom'});
});

$( ".my_change" ).on("change", function(e) {
 var theForm=document.getElementById("model_form");
  theForm.action = "";
  theForm.method = "get";
  theForm.submit();
 })

