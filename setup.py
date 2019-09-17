from setuptools import setup, find_packages


setup(
    name='sqlalchemydatabase3',
    version='1.0',
    description='Abstraction classes for SQLAlchemy connections using Python 3.',
    author='Blair Craft',
    author_email='blair@blaircraft.net',
    url='https://github.com/blaircraft/SQLAlchemyDatabase3',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'SQLAlchemy',
    ],
)
