import sys
from flask_appbuilder import SQLA, AppBuilder, ModelView, Model
from flask_appbuilder.models.sqla.interface import SQLAInterface
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from flask import Flask
from flask_appbuilder.actions import action

config = {
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db',
    'CSRF_ENABLED': True,
    'SECRET_KEY': '\2\1thisismyscretkey\1\2\e\y\y\h',
    'APP_NAME': 'Example of Filtering Many-to-many Relationships on a single field.'
}

app = Flask('single_filter_multi_value')
app.config.update(config)
db = SQLA(app)
appbuilder = AppBuilder(app, db.session)


program_registration = Table(
    'program_registration',
    Model.metadata,
    Column('program_id', Integer, ForeignKey('program.id')),
    Column('student_id', Integer, ForeignKey('student.id')))


course_registration = Table(
    'course_registration',
    Model.metadata,
    Column('course_id', Integer, ForeignKey('course.id')),
    Column('student_id', Integer, ForeignKey('student.id')))


class Teacher(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    def __repr__(self):
        return self.name


class Program(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    def __repr__(self):
        return self.name


class Student(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    program = relationship(Program, secondary=program_registration,
                           backref='students')

    def __repr__(self):
        return self.name


class Course(Model):
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    teacher_id = Column(Integer, ForeignKey('teacher.id'), nullable=False)
    teacher = relationship(Teacher, backref='courses')
    students = relationship(Student, secondary=course_registration,
                            backref='courses')

    def __repr__(self):
        return self.title


class CourseView(ModelView):
    datamodel = SQLAInterface(Course)

    list_columns = ['title', 'teacher']
    show_columns = ['title', 'teacher']

    @action("muldelete", "Delete", "Delete all Really?", "fa-rocket",
            single=False)
    def muldelete(self, items):
        self.datamodel.delete_all(items)
        self.update_redirect()
        return redirect(self.get_redirect())


class ProgramView(ModelView):
    datamodel = SQLAInterface(Program)
    list_columns = ['name']
    show_columns = ['name', 'students']
    add_columns = ['name']

    @action("muldelete", "Delete", "Delete all Really?", "fa-rocket",
            single=False)
    def muldelete(self, items):
        self.datamodel.delete_all(items)
        self.update_redirect()
        return redirect(self.get_redirect())


class StudentView(ModelView):
    datamodel = SQLAInterface(Student)
    related_views = [CourseView, ProgramView]

    list_columns = ['name', 'courses']

    @action("muldelete", "Delete", "Delete all Really?", "fa-rocket",
            single=False)
    def muldelete(self, items):
        self.datamodel.delete_all(items)
        self.update_redirect()
        return redirect(self.get_redirect())


class TeacherView(ModelView):
    datamodel = SQLAInterface(Teacher)
    related_views = [StudentView]

    list_columns = ['name']

    @action("muldelete", "Delete", "Delete all Really?", "fa-rocket",
            single=False)
    def muldelete(self, items):
        self.datamodel.delete_all(items)
        self.update_redirect()
        return redirect(self.get_redirect())


db.create_all()

appbuilder.add_view(TeacherView, 'Teachers')
appbuilder.add_view(CourseView, 'Courses')
appbuilder.add_view(StudentView, 'Students')
appbuilder.add_view(ProgramView, 'Programs')

def add_data():

    db.session.add(Program(name="Bachelor of Science IT"))
    db.session.add(Program(name="Bachelor of Science Computer Science"))
    mr_smith = Teacher(name='Jonathan Smith')
    db.session.add(mr_smith)
    rod = Student(name='Rod')
    jane = Student(name='Jane')
    freddy = Student(name='Freddy')
    db.session.add(rod)
    db.session.add(jane)
    db.session.add(freddy)

    db.session.add(Course(title="Introduction to Programming using Pyhon",
                          teacher=mr_smith,
                          students=[rod, jane, freddy]))
    db.session.add(Course(title="Mathematics I",
                          teacher=mr_smith,
                          students=[rod, jane]))
    db.session.commit()


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--add_data':
        add_data()
    else:
        app.run(debug=True)
