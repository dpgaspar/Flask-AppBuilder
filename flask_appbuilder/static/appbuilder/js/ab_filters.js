var AdminFilters = function(element, form, filters) {
    var $root = $(element);
    var $container = $('.filters', $root);
    var lastCount = 0;

    function removeFilter() {
        $(this).closest('tr').remove();
        $('button', $root).show();

        return false;
    }

    function addFilter(name, filter) {
        var $el = $('<tr />').appendTo($container);

        $el.append(
                $('<td/>').append(
                    $('<a href="#" class="btn remove-filter" />')
                        .append($('<span class="close-icon">&times;</span>'))
                        .append('&nbsp;')
                        .append(name)
                        .click(removeFilter)
                    )
            );

        // Filter type
        if ($(filters[name]).length > 0) {
        var $select = $('<select class="filter-op my_select2" />')
                      .attr('name', '_opt_' + name);

        $(filters[name]).each(function() {
            $select.append($('<option/>').attr('value', this).text(this));
        });

        $el.append(
                $('<td/>').append($select)
            );
        
        // Filter list
        $el.append(
                $('<td/>').append(form[name])
        );
        $select.select2();
        
        }
        else {
            var $select = $(form[name]);
            $el.append(
                $('<td/>').append($select)
            );
            $select.select2();
        }
        
        lastCount += 1;
        alert(lastCount);
        
    };

    $('a.filter').click(function() {
        var name = $(this).text().trim();
        addFilter(name);
    });
    
    $(".my_select2").select2({placeholder: "Select a State", allowClear: true});

};
