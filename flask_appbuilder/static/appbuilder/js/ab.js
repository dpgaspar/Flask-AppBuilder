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


var JsonSelect2 = function(name) {

    var data = [];
    var json_url = "./jsonselect/" + name;

    refresh();
    
    function query() {
        $.getJSON( json_url, function( data_json ) {
            data = data_json.results;
        });
    }

    function refresh() {
        query();
        $('.json-select2').select2({
            width: "100%",
            multiple: false,
            data: data
        });
    }
};


$(".json_select2").each(function() {
    JsonSelect2(this.id);
});


