var AdminFilters = function(element, labels, form, filters) {
    var $root = $(element);
    var $container = $('.filters', $root);
    var lastCount = 0;

    function removeFilter() {
        $(this).closest('tr').remove();
        $('button', $root).show();

        return false;
    }

	function addRemoveFilter($el, name, label)
	{
		$el.append(
                $('<td/>').append(
                    $('<a href="#" class="btn remove-filter" />')
                        .append($('<span class="close-icon">&times;</span>'))
                        .append('&nbsp;')
                        .append(label)
                        .click(removeFilter)
                    )
            );
	}
	
	
	
	function addFilterOptions($el, name)
	{
		var $select = $('<select class="filter-op my_select2" />')                     

		cx = 1;
        $(filters[name]).each(function() {
           	$select.append($('<option/>').attr('value', cx).text(this));
           	cx += 1;
        });

        $el.append(
               $('<td/>').append($select)
        );
        $select.select2();
        $select.change(function(e) {
        	changeOperation(e, name)
    	});
    	
	}


    function addFilter(name, filter) {
        var $el = $('<tr />').appendTo($container);
		
		addRemoveFilter($el, name, labels[name]);

        if ($(filters[name]).length > 0) {
			addFilterOptions($el, name);
			var $field = $(form[name]).attr('name', '_flt_0_' + name);
			
			$field.attr('class', ' filter_val ' + $field.attr('class'));
			$el.append(
                $('<td/>').append($field)
        	);
        
        }
        else {
            var $select = $(form[name]).attr('name', '_flt_' + name);
            $el.append(
                $('<td/>').append($select)
            );
            $select.select2({placeholder: "Select a State", allowClear: true});
        }
        
        lastCount += 1;        
        
    };

	function changeOperation(e, name) {
        alert(e.val);
        $input = $(e).next();
        alert($input.attr('name'));
    }

	

    $('a.filter').click(function() {
        var name = $(this).attr('name')
        addFilter(name);
    });
    
    

};
