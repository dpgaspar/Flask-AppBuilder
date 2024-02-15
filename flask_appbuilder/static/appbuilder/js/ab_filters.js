var AdminFilters = function (element, labels, form, filters, active_filters) {
    // Admin filters will deal with the adding and removing of search filters
    // :param labels:
    //      {'col','label'}
    // :param active_filters:
    //      [['col','filter name','value'],[...],...]

    let $root = $(element);
    let $container = $('.filters', $root);
    let lastCount = 0;

    function removeFilter() {
        $(this).closest('tr').remove();
        $('button', $root).show();

        return false;
    }

    function addActiveFilters() {
        $(active_filters).each(function () {
            if (Array.isArray(this[2])) {
                // Multiple values applied for the same filter.
                for (var i = 0; i < this[2].length; i++) {
                    addActiveFilter(this[0], this[1], this[2][i]);
                }
            } else {
                addActiveFilter(this[0], this[1], this[2]);
            }
        });
    }

    function addActiveFilter(name, filter_name, value) {
        let $el = $('<tr />').appendTo($container);

        addRemoveFilter($el, name, labels[name]);
        let i_option = addFilterOptionsValue($el, name, filter_name, false);

        let $field = $(form[name]);
        // if form item complex like <div><input bla></div>, datetime
        if ($("input", $($field)).html() != undefined) {
            $field_inner = $("input", $field)
            $field_inner.attr('name', '_flt_' + i_option + '_' + name);
            $field_inner.val(value);
            $field_inner.attr('class', ' filter_val ' + $field_inner.attr('class'));
        } else {
            if (($field.attr('type')) === 'checkbox') {
                $field.attr('checked', true);
            }
            $field.attr('name', '_flt_' + i_option + '_' + name);
            $field.val(value);
            $field.attr('class', ' filter_val ' + $field.attr('class'));
        }
        $el.append(
            $('<td class="filter"/>').append($field)
        );
    }

    function addRemoveFilter($el, name, label) {
        $el.append(
            $('<td />').append(
                $('<a href="#" class="btn remove-filter" />')
                    .append($('<span class="close-icon">&times;</span>'))
                    .append('&nbsp;')
                    .append(label)
                    .on('click', removeFilter)
            )
        );
    }

    function addFilterOptionsValue($el, name, value, activateSelect2 = true) {
        let $select = $('<select class="filter-op my_select2" />');
        let cx = 0;
        let i_option = -1;
        $(filters[name]).each(function () {
            if (value == this) {
                $select.append($('<option selected="selected"/>').attr('value', cx).text(this));
                i_option = cx;
            } else {
                $select.append($('<option/>').attr('value', cx).text(this));
            }
            cx += 1;
        });
        $el.append(
            $('<td class="filter"/>').append($select)
        );
        // avoids error
        // if (i_option === -1) { $select.select2(); }
        $select.on('select2:select', function (e) {
            changeOperation(e, $el, name);
        });
        if (activateSelect2) {
            $select.select2({
                placeholder: "Select a State",
                allowClear: true,
                theme: "bootstrap"
            });
        }
        return i_option;
    }


    function addFilter(name, filter) {
        let $el = $('<tr />').appendTo($container);

        addRemoveFilter($el, name, labels[name]);

        addFilterOptionsValue($el, name);
        let $field = $(form[name]);

        // if form item complex like <div><input bla></div>, datetime
        if ($("input", $($field)).html() != undefined) {
            $field_inner = $("input", $($field))
            $field_inner.attr('name', '_flt_0_' + name);
            $field_inner.attr('class', ' filter_val ' + $field_inner.attr('class'));
            $field_inner.attr('style', "width: 100%");
        } else {
            $field.attr('name', '_flt_0_' + name);
            $field.attr('class', ' filter_val ' + $field.attr('class'));
        }
        $el.append(
            $('<td class="filter"/>').append($field)
        );
        if ($field.hasClass("my_select2")) {
            $field.select2({
                placeholder: "Select a State",
                allowClear: true,
                theme: "bootstrap"
            });
        }
        if ($field.hasClass("appbuilder_datetime")) {
            $field.datetimepicker();
        }
        if ($field.hasClass("appbuilder_date")) {
            $field.datetimepicker({pickTime: false});
        }
        lastCount += 1;
    }

    // ----------------------------------------------------------
    // Trigger for option change will change input element name
    // ----------------------------------------------------------
    function changeOperation(e, $el, name) {
        let $in = $el.find('.filter_val');
        const data = e.params.data;
        $in.attr('name', '_flt_' + data.id + '_' + name);
    }

    $('a.filter').on('click', function () {
        const name = $(this).attr('name');
        addFilter(name);
    });

    addActiveFilters();
};
