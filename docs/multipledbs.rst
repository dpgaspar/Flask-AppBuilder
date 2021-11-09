Multiple Databases
==================

Because you can use Flask-SQLAlchemy (using the framework SQLA class) multiple databases is supported.

You can configure them the following way, first setup config.py::

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')

    SQLALCHEMY_BINDS = {
        'my_sql1': 'mysql://root:password@localhost/quickhowto',
        'my_sql2': 'mysql://root:password@externalserver.domain.com/quickhowto2'
    }

The **SQLALCHEMY_DATABASE_URI** is the default connection this is where the framework's
security tables will be created. The **SQLALCHEMY_BINDS** are the extra binds.

Now you can configure which models reside on which database using the __bind_key__ property ::

    class Model1(Model):
        __bind_key__ = 'my_sql1'
        id = Column(Integer, primary_key=True)
        name =  Column(String(150), unique = True, nullable=False)


    class Model2(Model):
        __bind_key__ = 'my_sql2'
        id = Column(Integer, primary_key=True)
        name =  Column(String(150), unique = True, nullable=False)


    class Model3(Model):
        id = Column(Integer, primary_key=True)
        name =  Column(String(150), unique = True, nullable=False)

On this example:
    -  Model1 will be on the local MySql instance with db 'quickhowto'.
    -  Model2 will be on the externalserver.domain.com MySql instance with db 'quickhowto2'.
    -  Model3 will be on the default connection using sqlite.


