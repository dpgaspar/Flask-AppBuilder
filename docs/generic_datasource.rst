Generic Data Sources
====================

This feature allows you to use alternative/generic datasources.
With it you can use python libraries, external APIs or any custom data with the framework
as if they were SQLAlchemy models.

Book catalog example
--------------------

As an example, here is a data source that holds a simple in-memory book catalog
and exposes it as if it were a SQLA model.

Your own generic data source must subclass from **GenericSession** and implement at least the **all** method.

The **GenericSession** mimics a subset of SQLA **Session** class and its query feature, so if you
override the all method you will implement the data generation at its heart.

First define the **Model** you will represent::

    from flask_appbuilder.models.generic import GenericModel, GenericSession, GenericColumn

    class BookModel(GenericModel):
        id = GenericColumn(int, primary_key=True)
        title = GenericColumn(str)
        author = GenericColumn(str)
        year = GenericColumn(int)
        genre = GenericColumn(str)

As you can see, we are subclassing from **GenericModel** and use **GenericColumn** much like SQLAlchemy,
except types are really python types. No type obligation is implemented, but you should respect it when
implementing your own data generation.

For your data generation::

    class BookSession(GenericSession):

        BOOKS = [
            {"id": 1, "title": "1984", "author": "George Orwell", "year": 1949, "genre": "Dystopian"},
            {"id": 2, "title": "Brave New World", "author": "Aldous Huxley", "year": 1932, "genre": "Dystopian"},
            {"id": 3, "title": "Dune", "author": "Frank Herbert", "year": 1965, "genre": "Science Fiction"},
        ]

        def _load_books(self):
            self.delete_all(BookModel())
            for entry in self.BOOKS:
                book = BookModel()
                book.id = entry["id"]
                book.title = entry["title"]
                book.author = entry["author"]
                book.year = entry["year"]
                book.genre = entry["genre"]
                self.add(book)

        def get(self, pk):
            self._load_books()
            return super(BookSession, self).get(pk)

        def all(self):
            self._load_books()
            return super(BookSession, self).all()

Each time the framework queries the data source, it will reload the data.
In a real application, the ``all`` and ``get`` methods could fetch data from an external API,
read from a file, query LDAP, or any other source.

The **GenericSession** class will implement by itself the Filters and order by methods
to be applied prior to your *all* method. So that everything works much like SQLAlchemy.

Finally you can use it on the framework like this::

    sess = BookSession()


    class BookView(ModelView):
        datamodel = GenericInterface(BookModel, sess)
        base_permissions = ['can_list', 'can_show']
        list_columns = ['title', 'author', 'year', 'genre']
        search_columns = ['title', 'author', 'genre']

And then register it like a normal ModelView.

I know this is still a short doc for such a complex feature, any doubts you may have just open an issue.
