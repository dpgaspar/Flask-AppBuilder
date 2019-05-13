import datetime
from flask import url_for, Markup, current_app
from mongoengine import Document
from mongoengine import DateTimeField, StringField, ReferenceField, ListField, FileField, ImageField

from flask_appbuilder.urltools import prefixed_url

mindate = datetime.date(datetime.MINYEAR, 1, 1)


class ContactGroup(Document):
    name = StringField(max_length=60, required=True, unique=True)

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return self.name


class Gender(Document):
    name = StringField(max_length=60, required=True, unique=True)

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class Tags(Document):
    name = StringField(max_length=60, required=True, unique=True)

    def __unicode__(self):
        return self.name


class Contact(Document):
    name = StringField(max_length=60, required=True, unique=True)
    address = StringField(max_length=60)
    birthday = DateTimeField()
    personal_phone = StringField(max_length=20)
    personal_celphone = StringField(max_length=20)
    contact_group = ReferenceField(ContactGroup, required=True)
    gender = ReferenceField(Gender, required=True)
    tags = ListField(ReferenceField(Tags))
    file = FileField()
    image = ImageField(size=(350, 250, True), thumbnail_size=(30, 30, True))


    def month_year(self):
        date = self.birthday or mindate
        return datetime.datetime(date.year, date.month, 1) or mindate

    def year(self):
        date = self.birthday or mindate
        return datetime.datetime(date.year, 1, 1)

    def __repr__(self):
        return "%s : %s\n" % (self.name, self.contact_group)

    def file_show(self):
        if self.file:
            return Markup(
                '<a href="' + prefixed_url(url_for('ContactModelView.mongo_download', pk=str(self.id))) + '">Download {0}</a>'.format(self.file.name))
        else:
            return Markup('')

    def image_show(self):
        if self.image:
            return Markup('<a href="' + prefixed_url(url_for('ContactModelView.show',pk=str(self.id))) + \
                      '" class="thumbnail"><img src="' + prefixed_url(url_for('ContactModelView.img', pk=str(self.id))) + \
                      '" alt="Photo" class="img-rounded img-responsive"></a>')
        else:
            return Markup('')

    def image_thumb_show(self):
        if self.image:
            return Markup('<a href="' + prefixed_url(url_for('ContactModelView.show',pk=str(self.id))) + \
                      '" class="thumbnail"><img src="' + prefixed_url(url_for('ContactModelView.img_thumb', pk=str(self.id))) + \
                      '" alt="Photo" class="img-rounded img-responsive"></a>')
        else:
            return Markup('')
