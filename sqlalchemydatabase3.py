from sqlalchemy import create_engine
from sqlalchemy.exc import ArgumentError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


class Database(object):
    """
    Abstract class for SQLAlchemy database connections. Does not actually connect to a database.
    """
    Base = declarative_base()

    def __init__(self):
        """
        Initialize the newly instantiated object.

        :return: None
        """
        self.engine = None
        self.Session = None

    def connect(self, uri, echo=False, reinitialize=False):
        """
        Connect the SQLAlchemy engine, create a Session object (via sessionmaker())
        and initialize the schema.

        :param uri: RFC 3968 URI.
        :param echo: echo SQL commands to the console as they are executed by SQLAlchemy.
        :param reinitialize: drop all tables before (re)creating them
        :return: None
        """
        try:
            self.engine = create_engine(uri, echo=echo)
            self.Session = sessionmaker(bind=self.engine)
            self.initialize(reinitialize)
        except ArgumentError as error:
            print('Problem connecting to the database: {}'.format(error))

    def execute(self, sql):
        """
        Execute a raw SQL statement.
        :param sql: raw text string representing the SQL statement.
        :return: A SQLAlchemy result
        """
        conn = self.engine.connect()
        result = conn.execute(sql)
        return result

    def initialize(self, reinitialize=False):
        """
        (Optionally) drop all tables and recreate them in the schema.

        :param reinitialize: if true, drop all tables.
        :return: None
        """
        if reinitialize:
            self.drop_tables()
        self.create_tables()

    def create_tables(self):
        """
        Create all tables in the schema.

        :return: None
        """
        self.Base.metadata.create_all(self.engine)

    def drop_tables(self):
        """
        Drop all tables in the schema.

        :return: None
        """
        self.Base.metadata.drop_all(self.engine)

    def delete(self, table):
        """
        Delete all records in <table>.

        :param table: a SQLAlchemy model
        :return: None
        """
        session = self.Session()
        session.query(table).delete()
        session.commit()

    @staticmethod
    def new(uri, reinitialize=False, echo=False):
        """
        Factory method for instantiating a database object from a URI. For URI
        specifications, see SQLiteDatabase, PostgreSQLDatabase.

        :param echo: echo SQL commands to the console as they are executed by SQLAlchemy.
        :param reinitialize: drop all tables before (re)creating them
        :param uri: an RFC 3986 URI pointing to the database
        :return: An initialized database object or raise an ArgumentError if the
        URI was not recognizable.
        """
        if uri.startswith('postgresql+psycopg2://'):
            return PostgreSQLDatabase(uri=uri, reinitialize=reinitialize, echo=echo)
        if uri.startswith('postgresql://'):
            return PostgreSQLDatabase(uri=uri, reinitialize=reinitialize, echo=echo)
        elif uri.startswith('sqlite://'):
            return SQLiteDatabase(uri=uri, reinitialize=reinitialize, echo=echo)
        else:
            raise ArgumentError('database URI ({}) not recognized.'.format(uri))


class PostgreSQLDatabase(Database):
    """
    Class for SQLAlchemy connections to PostgreSQL databases.
    """

    def __init__(
            self,
            database=None,
            username=None,
            password=None,
            host=None,
            port=5432,
            echo=False,
            reinitialize=False,
            uri=None
    ):
        """
        Configure the newly instantiated PostgreSQL database connection. Can use a fully formed
        RFC 3986 URI or specify options (username, password, hostname, etc.) for a Unix domain
        or TCP connection.

        Valid URIs:
            postgresql+psycopg2://username:password@hostname[:port]/database (TCP connections)
            postgresql+psycopg2://username:password@database (Unix domain connections)


        :param database: database name
        :param username: username on host with privileges to access database
        :param password: user password on host
        :param host: hostname of PostgreSQL server
        :param port: port on hostname on which PostgreSQL server is listening
        :param echo: echo SQL commands to the console as they are executed by SQLAlchemy.
        :param reinitialize: drop all tables before (re)creating them
        :param uri: RFC 3986 URI pointing to the PostgreSQL database
        :return: None
        """
        Database.__init__(self)

        if uri is None:
            # format user string
            if password is None:
                user_string = username
            else:
                user_string = '{}:{}'.format(username, password)

            # format host string
            if host is None:
                # Unix domain connection
                db_string = database
            else:
                # TCP connection
                db_string = '{}:{}/{}'.format(host, port, database)
            self.db_uri = 'postgresql+psycopg2://{}@{}'.format(user_string, db_string)
        else:
            self.db_uri = uri
            self.echo = echo
            self.reinitialize = reinitialize

        self.connect(self.db_uri, echo, reinitialize)


class SQLiteDatabase(Database):
    """
    Class for SQLAlchemy connections to SQLite databases.
    """

    def __init__(self, db_file=None, echo=False, reinitialize=False, uri=None):
        """
        Configure the newly instantiated SQLite database connection. Can use a fully formed
        RFC 3986 URI or specify a file name to open.

        Valid URIs:
            sqlite:///relative/path/to/database.sqlite - ./relative/path/to/database.sqlite
            sqlite:////absolute/path/to/database.sqlite - /absolute/path/to/database.sqlite

        :param db_file: file name of file containing database
        :param echo: echo SQL commands to the console as they are executed by SQLAlchemy.
        :param reinitialize: drop all tables before (re)creating them
        :param uri: RFC 3986 URI pointing to the SQLite database
        :return: None
        """
        Database.__init__(self)

        if uri is None:
            self.db_uri = 'sqlite:///' + db_file
        else:
            self.db_uri = uri
        self.echo = echo
        self.reinitialize = reinitialize

        self.connect(self.db_uri, echo=self.echo, reinitialize=self.reinitialize)
