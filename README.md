# SQLAlchemyDatabase

## Introduction

SQLAlchemyDatabase abstracts and simplifies the parts of SQLAlchemy that are
required for every database connection (binding the engine, creating a Session
object, etc.). It also abstracts connections to different database types
(currently SQLite and PostgreSQL) to simplify the startup process.

## Simple Usage Examples

```python
from sqlalchemydatabase3 import Database, SQLiteDatabase, PostgreSQLDatabase

# SQLite database using an RFC 3986 URI, all tables dropped and (re)created.
sdb = SQLiteDatabase(uri='sqlite:///database.sqlite', reinitialize=True)

# PostgreSQL database using parameters, all SQL commands echoed to console.
pdb = PostgreSQLDatabase(
	hostname='mymachine.domain',
	port='5432',
	username='user',
	password='mypassw0rd',
	database='pdb',
	echo=True
)

# A database who's connection type is determined by URI at run-time.
db = Database.new(uri='sqlite:///database.sqlite')
```

## A More Complicated Example 

```python
import click
from sqlalchemy import Column, Integer, String
from sqlalchemydatabase3 import Database

class User(Database.Base):
	__tablename__ == 'users'

	id = Column(Integer, primary_key=True)
	name = Column(String, unique=True)
	password = Column(String)

	def __init__(self, id, name, password):
		self.id = id
		self.name = name
		self.password = password

	def __repr__(self):
		return '{}:{}:{}'.format(self.id, self.name, self.password)

	def copy(self):
		'''
		Create a copy of the User, stripping association with a particular
		SQLAlchemy session.
		'''
		return User(self.id, self.name, self.password)


@click.command()
@click.argument(
	'src'
)
@click.argument(
	'dst'
)
@click.argument(
	'tables',
	nargs=-1
)
def main(src, dst, tables):
	'''
	Migrate tables from src database to dst.
	'''

	src['db'] = Database.new(uri=src)
	src['session'] = src_db.Session()

	dst['db'] = Database.new(uri=dst, reinitialize=True)
	dst['session'] = dst_db.Session()

	for table in tables:
		records = src['session'].query(table).all()
		for record in records:
			dst['session'].add(record.copy())
		dst['session'].commit()


if __name__ == "__main__":
	main()
```
