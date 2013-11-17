Quick How to
============

The Base Skeleton Application
-----------------------------

If your working with the base skeleton application (see 3 step instalation)

you now have the following directory structure::

    <your project name>/
        config.py : All the applications configuration
        run.py    : A runner mainly for debug
        app/
            __init__.py : Application's initialization
            models.py : Declare your database models here
            views.py  : Implement your views here

    
It's very easy and fast to create an application out of the box, with detailed security.

Please take a look at github examples on:

https://github.com/dpgaspar/Flask-AppBuilder/tree/master/examples


Define your models (models.py)
..............................

::

        class Group(BaseMixin, db.Model):
            id = db.Column(db.Integer, primary_key=True)
            name = db.Column(db.String(50), unique = True, nullable=False)

            def __repr__(self):
                return self.name

        class Contact(AuditMixin, db.Model):
            id = db.Column(db.Integer, primary_key=True)
            name = db.Column(db.String(150), unique = True, nullable=False)
            address = db.Column(db.String(564))
            birthday = db.Column(db.Date)
            photo = db.Column(ImageColumn, nullable=False )
            group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
            group = db.relationship("Group")
            
            def photo_img(self):
                im = ImageManager()
                if self.photo:
                    return Markup('<a href="/persons/show/' + str(self.id) + 
                    '" class="thumbnail"><img src="' + 
                    im.get_url(self.photo) + 
                    '" alt="Photo" class="img-rounded img-responsive"></a>')
                else:
                    return Markup('<a href="/persons/show/' + str(self.id) + 
                    '" class="thumbnail"><img src="//:0" alt="Photo" class="img-responsive"></a>')
        

            def __repr__(self):
                return self.name



Define your Views (views.py)
............................

Notice the 'fieldset' that is only defined on the show view.
You can define them to add or edit also, in any diferent way.

Notice also the 'related_views', will show a master/detail on
the 'group show view' and 'edit show view' listing the related contacts

::
  
        class GroupGeneralView(GeneralView):
            route_base = '/groups'
            datamodel = SQLAModel(Group, db.session)
            related_views = [ContactGeneralView()]

            list_title = 'List Groups'
            show_title = 'Show Group'
            add_title = 'Add Group'
            edit_title = 'Edit Group'

            label_columns = { 'name':'Name'}
            list_columns = ['name']
            show_columns = ['name']
            order_columns = ['name']
            search_columns = ['name']
    
        class ContactGeneralView(GeneralView):
            route_base = '/contacts'
            datamodel = SQLAModel(Contact, db.session)

            list_title = 'List Contacts'
            show_title = 'Show Contacts'
            add_title = 'Add Contact'
            edit_title = 'Edit Contact'

            label_columns = {'name':'Name',
                        'photo':'Photo',
                        'photo_img':'Photo',
                        'address':'Address',
                        'birthday':'Birthday',
                        'group':'belongs to group'}                
            description_columns = {'name':'The Contacts Name'}
            list_columns = ['name','group']
            show_fieldsets = [
                 ('Summary',{'fields':['photo_img','name','address','group']}),
                 ('Personal Info',{'fields':['birthday'],'expanded':False}),
                 ]
            order_columns = ['name']
            search_columns = ['name']

        genapp = General(app)
        genapp.add_view(GroupGeneralView, "List Groups","/groups/list","th-large","Contacts")
        genapp.add_view(ContactGeneralView, "List Contacts","/contacts/list","earphone","Contacts")

