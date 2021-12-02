==========
Issue #789
==========

Description
-----------

Although Flask-AppBuilder supported many-to-many relationships between objects
this was not reflected in the list view when searching on such relationships as
described in issue_789_

.. _issue_789: https://github.com/dpgaspar/Flask-AppBuilder/issues/789

The 'enhancement' contributed in branch single_filter_multiple_values patches
the Search functionality of the list view such that it takes into account all
values supplied in the 'relationship' field rather than ignoring those beyond
the first.

This demo illustrates the issue and the fix for it.

Running the Demo
----------------

To illustrate the issue described in issue_789:

1. run app.py in an environment that has Flask-AppBuilder <= 1.12.3 installed.
#. open http://localhost:5000 in a web browser
#. login using the username ```admin``` with password ```admin```
#. navigate to the 'Students' view (note that there are 3 Students)
#. open the 'Search' panel
#. click 'Add filter'
#. select 'Courses'
#. select both Courses in the filter box
#. click the 'Search' button
#. note that all three Students remain even though Freddy is not enrolled in
   the course 'Mathematics I'
#. open the 'Search' panel and note that only the first course remains in the
   filter box even though both values are present in the page URI


To verify the fix:

1. Run this version of Flask-AppBuilder
#. repeat steps 2 ~ 8 above
#. note that Freddy is no longer visible as he is not enrolled in the 'Mathematics I' course
#. open the 'Search' panel
#. note that both courses remain in the filter box

