

//---------------------------------------
// Function for keeping tab focus
// after page reload, uses cookies
//---------------------------------------
$(function() 
{ 
$('a[data-toggle="tab"]').on('shown.bs.tab', function () {
//save the latest tab; use cookies if you like 'em better:
    localStorage.setItem('lastTab', $(this).attr('href'));
});

//go to the latest tab, if it exists:
var lastTab = localStorage.getItem('lastTab');
if (lastTab) {
    $('a[href=' + lastTab + ']').tab('show');
}
else
{
// Set the first tab if cookie do not exist
    $('a[data-toggle="tab"]:first').tab('show');
}
});

