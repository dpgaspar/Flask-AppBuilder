
// This script was changed from ab_filters.js - now receiving as parameter: active_filters_localized 
//  Also, python gbl_locale_definitions is visible here as js_locale_definitions (created in my_init.html)
                                                      
var MyAdminFilters =  //<<<=== Notice: changed the name of this func "object", called by script in my_search_widget_template.html 
    function(element, 
             labels,  
             form, //<<-- just to remember: this 'form' is the 'form_fields' of caller , and it ONLY has the html TAGs of the Fields
             filters,  
             active_filters_localized //CHANGED to use active_filters_localized
             ) {    
    // Admin filters will deal with the adding and removing of search filters
    // :param labels:
    //      {'col','label'}
    // :param active_filters:
    //      [['col','filter name','value'],[...],...]
    
    var $root = $(element);
    var $container = $('.filters', $root);
    var lastCount = 0;

    function removeFilter() {
        $(this).closest('tr').remove();
        $('button', $root).show();

        return false;
    }

    function addActiveFilters()
    {
        //$(active_filters).each(function() {
        $(active_filters_localized).each(function() {     //CHANGED to use active_filters_localized
            addActiveFilter(this[0], this[1], this[2]);
        });
    }

    function addActiveFilter(name, filter_name, value)
    {
        var $el = $('<tr />').appendTo($container);

	    addRemoveFilter($el, name, labels[name]);
        var i_option = addFilterOptionsValue($el, name, filter_name);
	
        var $field = $(form[name])
        // if form item complex like <div><input bla></div>, datetime
        if ( $("input", $($field)).html() != undefined ) {
            $field_inner = $("input", $field);
            $field_inner.attr('name', '_flt_' + i_option + '_' + name);
            $field_inner.val(value);
            $field_inner.attr('class', ' filter_val ' + $field_inner.attr('class'));
	    }
        else {
            if (($field.attr( 'type')) == 'checkbox') {
                $field.attr( 'checked', true );
            }
            $field.attr('name', '_flt_' + i_option + '_' + name);
            $field.val(value);
            $field.attr('class', ' filter_val ' + $field.attr('class'));
        }
        $el.append(
            $('<td/>').append($field)
            );;
            
        //handleMaskedFields($field, name);  //<<=== DON'T do this - search ACTIVE filters elements are treated in My_ab.js.
    
    }
    

	function addRemoveFilter($el, name, label)
	{
		$el.append(
                $('<td class="col-lg-1 col-md-1" />').append(
                    $('<a href="#" class="btn remove-filter" />')
                        .append($('<span class="close-icon">&times;</span>'))
                        .append('&nbsp;')
                        .append(label)
                        .click(removeFilter)
                    )
            );
	}

    function addFilterOptionsValue($el, name, value)
	{
		var $select = $('<select class="filter-op my_select2" />');                     

		cx = 0;
        var i_option = -1;
        $(filters[name]).each(function() {
            if (value == this) {
                $select.append($('<option selected="selected"/>').attr('value', cx).text(this));
                i_option = cx;
            }
            else {
                $select.append($('<option/>').attr('value', cx).text(this));
            }
	    cx += 1;
        });

        $el.append(
               $('<td class="col-lg-1 col-md-1 col-sm-1" />').append($select)
        );
        // avoids error
        if (i_option == -1) { $select.select2(); }
        $select.change(function(e) {
        	changeOperation(e, $el, name)
    	});
        
        return i_option;
	}
    

    function addFilter(name, filter) {
                
        var $el = $('<tr />').appendTo($container);
		
	    addRemoveFilter($el, name, labels[name]);

        addFilterOptionsValue($el, name);
	    var $field = $(form[name]);     //<< --- NOTICE: $field here has ALL the html tags defined in the WTForm Field 'widget'
                                        //               so, a (My)DateField has a '<div> ' before the real text field...
        //console.log("AddFilter name/$field = ", name, $field);

	
	    // if form item complex like <div><input bla></div>, datetime
	    if ( $("input", $($field)).html() != undefined ) {
		    $field_inner = $("input", $($field));
		    $field_inner.attr('name', '_flt_0_' + name);
		    $field_inner.attr('class', ' filter_val ' + $field_inner.attr('class'));
	
	    }
	    else {
		    $field.attr('name', '_flt_0_' + name);
		    $field.attr('class', ' filter_val ' + $field.attr('class'));
	    }
	    $el.append(
        	$('<td/>').append($field)
        );;
                
        if ($field.hasClass( "my_select2" )) {
        	$field.select2({placeholder: "Select a State", allowClear: true});
        }

        //COMMENTED - these IFs are now inside the function handleMaskedFields(name)
        //if ($field.hasClass( "appbuilder_datetime" )) {
        //	$field.datetimepicker(); 
        //}        
        //if ($field.hasClass( "appbuilder_date" )) {
        //    $field.datetimepicker({pickTime: false });        
        //}


        handleMaskedFields($field, name);                          //<<=====  ADDED
      
        
        lastCount += 1;
    };
    
    
    function handleMaskedFields($field, name) {

        //console.log("BEGIN of function handleMaskedFields()");
        
        //NOTICE that js_locale_definitions is a global variable available in EVERY page/script - it was defined in my_init.html        
        //console.log("locale/language currently set in FAB = ", js_locale_definitions['locale']);
        
               
        // the original FAB 'appbuilder_datetime' widget:    
        if ($field.hasClass( "appbuilder_datetime" )) {
        	$field.datetimepicker(); 
        }        
        
        // the original FAB 'appbuilder_date'/DatePickerWidget widget:    
        if ($field.hasClass( "appbuilder_date" )) {
            //console.log("Instantiating datetimepicker() for ", name); 
            $field.datetimepicker({pickTime: false });        
        }
        
        // the new  MyDatePickerWidget:         
        if ($field.hasClass( "my_appbuilder_date" )) {      //<<--- 'class' is set inside MyDatePickerWidget python class !!!        
            var lang_datepicker = js_locale_definitions['locale'];
            if (lang_datepicker == "pt_BR") {
               lang_datepicker = "pt-BR";
            }
            if (lang_datepicker == "zh") {
               lang_datepicker = "zh-CN";
            }
            var dt_format_for_datepicker = js_locale_definitions['dt_format_for_datepicker'];
            //console.log("Instantiating localized datepicker for = ", name, lang_datepicker, dt_format_for_datepicker);
            $field.datetimepicker({
                language: lang_datepicker,            //<<-- includeded parameters for language and format here !
                format: dt_format_for_datepicker,
                pickTime: false 
            });
                    

        }        
        
        // NOTICE: $field here is a plain text field, because a MyBS3TextfieldWidget was set by MyDateField.
        if( $field.hasClass("my_appbuilder_date_no_picker") ) { 
            var cleave_var = new Cleave($field, { 
               date: true,
               delimiter: js_locale_definitions['dt_delim'],
               datePattern: js_locale_definitions['dt_pattern_for_cleave']
            });	
        }
        
        //If field has the type MyDecimalField, it will get the appropriate numeral with decimal Cleave MASK:
        // NOTICE: $field here is a plain text field, because a MyBS3TextfieldWidget was set by MyDateField.            
        if ( $field.hasClass("my_appbuilder_num_decimal") ) {
            var decimal_scale = $field.attr('data-decimal_scale') * 1;
            var positive_only = $field.attr('data-positive_only') === undefined ? false : true;
            //console.log(' Instantianting Cleave decimal for >> ', name + " " + $field.attr('id'));
            //console.log('            decimal_scale  >> ' + decimal_scale);
            //console.log('            positive_only  >> ' + positive_only);
            var cleave_var = new Cleave($field, {
                numeral: true,
                numeralThousandsGroupStyle: 'thousand',
                numeralDecimalScale: decimal_scale, // Scale/places; be sure it is compatible with DB storage(in models.py)
                numeralDecimalMark: js_locale_definitions['dec_sep'],  // The decimal separator was already adjusted by MyDecimalField for the current locale
                delimiter: js_locale_definitions['th_delim'],           // idem
                numeralPositiveOnly: positive_only,
                //prefix: '$',                 // COULD have a currency symbol (check business requirements)  
            });	
            
        }          

        //console.log("End of function handleMaskedFields()");
        
    }
    

	// ----------------------------------------------------------
	// Trigger for option change will change input element name
	// ----------------------------------------------------------
    function changeOperation(e, $el, name) {
        $in = $el.find('.filter_val');
        $in.attr('name','_flt_' + e.val + '_' + name);
    }


    $('a.filter').click(function() {
        var name = $(this).attr('name')
        addFilter(name);
    });
    
    addActiveFilters();

};

