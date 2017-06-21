Generic Data Sources
====================

This feature is still beta, but you can already use it, it allows you to use alternative/generic datasources.
With it you can use python libraries, systems commands or whatever with the framework as if they were
SQLAlchemy models.

PS Command example
------------------

Already on the framework, and intended to be an example, is a data source that holds the output from
the linux 'ps -ef' command, and shows it as if it were a SQLA model.

Your own generic data source must subclass from **GenericSession** and implement at least the **all** method

The **GenericSession** mimics a subset of SQLA **Session** class and it's query feature, so if you
override the all method you will implement the data generation at it's heart.

On our example you must first define the **Model** you will represent::

    from flask_appbuilder.models.generic import GenericModel, GenericSession, GenericColumn

    class PSModel(GenericModel):
        UID = GenericColumn(str)
        PID = GenericColumn(int, primary_key=True)
        PPID = GenericColumn(int)
        C = GenericColumn(int)
        STIME = GenericColumn(str)
        TTY = GenericColumn(str)
        TIME = GenericColumn(str)
        CMD = GenericColumn(str)

As you can see, we are subclassing from **GenericModel** and use **GenericColumn** much like SQLAlchemy.
except type are really python types. No type obligation is implemented, but you should respect it when
implementing your own data generation

For your data generation, and regarding our example::

    class PSSession(GenericSession):
        regexp = "(\w+) +(\w+) +(\w+) +(\w+) +(\w+:\w+|\w+) (\?|tty\w+) +(\w+:\w+:\w+) +(.+)\n"

        def _add_object(self, line):
            import re

            group = re.findall(self.regexp, line)
            if group:
                model = PSModel()
                model.UID = group[0][0]
                model.PID = int(group[0][1])
                model.PPID = int(group[0][2])
                model.C = int(group[0][3])
                model.STIME = group[0][4]
                model.TTY = group[0][5]
                model.TIME = group[0][6]
                model.CMD = group[0][7]
                self.add(model)

        def get(self, pk):
            self.delete_all(PSModel())
            out = os.popen('ps -p {0} -f'.format(pk))
            for line in out.readlines():
                self._add_object(line)
            return super(PSSession, self).get(pk)


        def all(self):
            self.delete_all(PSModel())
            out = os.popen('ps -ef')
            for line in out.readlines():
                self._add_object(line)
            return super(PSSession, self).all()

So each time the framework queries the data source, it will **delete_all** records, and
call 'ps -ef' for a query all records, or 'ps -p <PID>' for a single record.

The **GenericSession** class will implement by itself the Filters and order by methods
to be applied prior to your *all* method. So that everything works much like SQLAlchemy.

I implemented this feature out of the necessity of representing LDAP queries, but of course
you can use it to wherever your imagination/necessity drives you.

Finally you can use it on the framework like this::

    sess = PSSession()


    class PSView(ModelView):
        datamodel = GenericInterface(PSModel, sess)
        base_permissions = ['can_list', 'can_show']
        list_columns = ['UID', 'C', 'CMD', 'TIME']
        search_columns = ['UID', 'C', 'CMD']

And then register it like a normal ModelView.


You can try this example on `quickhowto2 example <https://github.com/dpgaspar/Flask-AppBuilder/tree/master/examples/quickhowto2>`

I know this is still a short doc for such a complex feature, any doubts you may have just open an issue.
