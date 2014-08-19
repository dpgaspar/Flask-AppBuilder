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


var AdminJsonSelect2 = function(name) {

    var data = [];
    var json_url = "./jsonselect/" + name;

    refresh();
    $.getJSON( json_url, function( data_json ) {
      $.each( data_json, function( key, val ) {
        var item = {};
        item['id'] = key;
        item['text'] = val;
        data.push(item);
      });
    });

    function refresh() {
        $('.json-select2').select2({
            width: "100%",
            multiple: false,
            data: data
        });
    }
};

AdminJsonSelect2();