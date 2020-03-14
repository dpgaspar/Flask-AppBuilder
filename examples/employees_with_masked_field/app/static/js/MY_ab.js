
//THIS script is a copy of ab.js, only INCLUDED  some code to handle the elements 
// with html 'class': my_appbuilder_date, my_appbuilder_date_no_picker and my_appbuilder_num_decimal


//-----------------------------------------------------------
// AJAX REST call to server to fetch data for select2 Slaves
//-----------------------------------------------------------
function loadSelectDataSlave(elem) {
    $(".my_select2_ajax_slave").each(function( index ) {
        var elem = $(this);
        var master_id = elem.attr('master_id');
        var master_val = $('#' + master_id).val();
        if (master_val) {
            var endpoint = elem.attr('endpoint');
            endpoint = endpoint.replace("{{ID}}", master_val);
            $.get( endpoint, function( data ) {
                elem.select2({data: data, placeholder: "Select", allowClear: true});
            });
        }
        else {
            elem.select2({data: {id: "",text: ""}, placeholder: "Select", allowClear: true});
        }
        $('#' + master_id).on("change", function(e) {
            var endpoint = elem.attr('endpoint');
            if (e.val) {
                endpoint = endpoint.replace("{{ID}}", e.val);
                $.get( endpoint, function( data ) {
                    elem.select2({data: data, placeholder: "Select", allowClear: true});
                });
            }
        })
    });
}


//----------------------------------------------------
// AJAX REST call to server to fetch data for select2
//----------------------------------------------------
function loadSelectData() {
    $(".my_select2_ajax").each(function( index ) {
        var elem = $(this);
        $.get( $(this).attr('endpoint'), function( data ) {
            elem.select2({data: data, placeholder: "Select", allowClear: true});
        });
    });
}


//---------------------------------------
// Setup date time modal views, select2
//---------------------------------------
$(document).ready(function() {

    $('.appbuilder_datetime').datetimepicker({pickTime: false});
    $('.appbuilder_date').datetimepicker({
        pickTime: false });
    $(".my_select2").select2({placeholder: "Select a State", allowClear: true});
    loadSelectData();
    loadSelectDataSlave();
    $(".my_select2.readonly").select2("readonly",true);     //readonly is set in a different way if using select2 >= V4.x
    $("a").tooltip({container:'.row', 'placement': 'bottom'});
    
    
    //==BEGIN INCLUDED CODE
        
    //Note that js_locale_definitions is a global variable available in EVERY page/script - it was defined in my_init.html
    var lang_datepicker = js_locale_definitions['locale'];
    if (lang_datepicker == "pt_BR") {
       lang_datepicker = "pt-BR";
    }
    if (lang_datepicker == "zh") {
       lang_datepicker = "zh-CN";
    }
    
    // Handle elements with the html 'class': my_appbuilder_date
    $(".my_appbuilder_date").datetimepicker({
            language: lang_datepicker,                  //<<-- included language and format here !
            format: js_locale_definitions['dt_format_for_datepicker'],
            pickTime: false 
    });
                
    // Handle elements with the html 'class': my_appbuilder_date_no_picker
    // NOTICE: $field here is a plain text field, because a MyBS3TextfieldWidget was set by MyDateField.    
    $(".my_appbuilder_date_no_picker").each(function() {  //tryed Cleave on the 'class', but raised an error, so looping each one...
        $field = $(this);  // 'this' here presents each element that has the class
        new Cleave($field, {
           date: true,
           delimiter: js_locale_definitions['dt_delim'],
           datePattern: js_locale_definitions['dt_pattern_for_cleave']
        });	        
    });    

    // Handle elements with the html 'class': my_appbuilder_num_decimal
    // NOTICE: $field here is a plain text field, because a MyBS3TextfieldWidget was set by MyDateField.    
    $(".my_appbuilder_num_decimal").each(function() {   
        $field = $(this);  // 'this' here presents each element that has the class
        var decimal_scale = $field.attr('data-decimal_scale') * 1;
        var positive_only = $field.attr('data-positive_only') === undefined ? false : true;
        
        //console.log(' my_appbuilder_num_decimal >> ' + $field.attr('id'));
        //console.log('            decimal_scale  >> ' + decimal_scale);
        //console.log('            positive_only  >> ' + positive_only);
        
        new Cleave($field, {
            numeral: true,
            numeralThousandsGroupStyle: 'thousand',
            numeralDecimalScale: decimal_scale, // Scale/places; be sure it is compatible with DB storage(in models.py)
            numeralDecimalMark: js_locale_definitions['dec_sep'],  // The decimal separator was already adjusted by MyDecimalField for the current locale
            delimiter: js_locale_definitions['th_delim'],           // idem
            numeralPositiveOnly: positive_only,
            //prefix: '$',                 // COULD have a currency symbol (check business requirements)  
        });	
        
    });    
    //==END OF INCLUDED CODE    
    
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




