
var AdminFilters = function(element, search_filters) {
    var $root = $(element);
    var $container = $('.filters', $root);
    var lastCount = 0;


    function addFilter(name, filter) {
        var $el = $('<tr />').appendTo($container);

        // Filter list
        $el.append(name);
    };

    $('a.filter').click(function() {
        var name = $(this).text().trim();
        alert(name);
        addFilter(name, search_filters[name]);
        
    });

};
