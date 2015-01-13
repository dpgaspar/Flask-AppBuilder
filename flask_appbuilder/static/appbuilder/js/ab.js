//---------------------------------------
// Setup date time modal views
//---------------------------------------
$(document).ready(function() {
    $('.appbuilder_datetime').datetimepicker({pickTime: false});
    $('.appbuilder_date').datetimepicker({
        pickTime: false });
    $(".my_select2").select2({placeholder: "Select a State", allowClear: true});;
    $(".my_select2.readonly").select2("readonly",true)
    $("a").tooltip({container:'.row', 'placement': 'bottom'});
});


$( ".my_change" ).on("change", function(e) {
 var theForm=document.getElementById("model_form");
  theForm.action = "";
  theForm.method = "get";
  theForm.submit();
 })


//---------------------------------------
// Bootstrap modal, javascript alert
//---------------------------------------
function ab_alert(text) {
    $('#modal-alert').on('show.bs.modal', function(e) {
            $('.modal-text').text(text);
        }
    );
    $('#modal-alert').modal('show');
};


//---------------------------------------
// Modal confirmation JS support
//---------------------------------------

// On link attr "data-text" is set to the modal text
$(document).ready(function(){
    $(".confirm").click(function() {
        $('.modal-text').text($(this).data('text'));
    });
});

// If positive confirmation on model follow link
$('#modal-confirm').on('show.bs.modal', function(e) {
    $(this).find('#modal-confirm-ok').attr('href', $(e.relatedTarget).data('href'));
});

