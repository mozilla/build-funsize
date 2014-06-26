from setuptools import setup

PACKAGE_NAME = 'senbonzakura'
PACKAGE_VERSION = '0.1'

setup(name=PACKAGE_NAME,
      version=PACKAGE_VERSION,
      description='partial mar webservice prototype',
      long_description='https://wiki.mozilla.org/User:Ffledgling/Senbonzakura',
      classifiers=[], #what does this do?
      author='Anhad Jai Singh',
      author_email='ffledgling@gmail.com',
      url='https://wiki.mozilla.org/User:Ffledgling/Senbonzakura', #Change this
      license='MPL',
      install_requires=[
        'Flask==0.10.1',
        #'Flask-WTF==0.9.5',
        'SQLAlchemy==0.9.4',
        'amqp==1.4.5',
        'celery==3.1.11',
        'nose==1.3.3',
        'redo==1.0',
        'requests==2.2.1',
        ],
      packages=[
        'senbonzakura',
        'senbonzakura.backend',
        'senbonzakura.cache',
        'senbonzakura.database',
        'senbonzakura.frontend',
        'senbonzakura.utils',
        ],
      tests_require=[
        'nose',
        'mock'
        ],
      )

      

