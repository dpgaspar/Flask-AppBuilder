// This js work is based on:
// Copyright (c) 2014, Serge S. Koval and contributors. See AUTHORS
// for more details.
//

var AdminActions = function() {

    var chkAllFlag = true;

    this.execute_multiple = function(name, confirmation) {
        var selected = $('input.action_check:checked').size();

        if (selected == 0) {
            alert('No row selected');
            return false;
        }

        if (!!confirmation) {
            $('#modal-confirm').modal('show');
            if (!confirm(confirmation)) {
                return false;
            }
        }

        // Update hidden form and submit it
        var form = $('#action_form');
        $('#action', form).val(name);

        $('input.action_check', form).remove();
        $('input.action_check:checked').each(function() {
            form.append($(this).clone());
        });

        form.submit();

        return false;
    };

    this.execute_single = function(url, confirmation) {
        if (!!confirmation) {
            if (!confirm(confirmation)) {
                return false;
            }
        }

        window.location.href = url;
    };

    $('.action_check_all').click(function() {
        $('.action_check').prop('checked', chkAllFlag);
        chkAllFlag = !chkAllFlag;
    });

};
