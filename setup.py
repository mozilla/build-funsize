from setuptools import setup

PACKAGE_NAME = 'funsize'
PACKAGE_VERSION = '0.1'

setup(name=PACKAGE_NAME,
      version=PACKAGE_VERSION,
      description='partial mar webservice prototype',
      long_description='https://wiki.mozilla.org/User:Ffledgling/Senbonzakura',
      classifiers=[],
      author='Anhad Jai Singh',
      author_email='ffledgling@gmail.com',
      url='https://wiki.mozilla.org/User:Ffledgling/Senbonzakura',
      license='MPL',
      install_requires=[
            'Flask==0.10.1',
            'SQLAlchemy==0.9.4',
            'amqp==1.4.6',
            'celery==3.1.11',
            'nose==1.3.3',
            'redo==1.0',
            'requests==2.2.1',
      ],
      packages=[
            'funsize',
            'funsize.backend',
            'funsize.cache',
            'funsize.database',
            'funsize.frontend',
            'funsize.utils',
      ],
      tests_require=[
            'nose',
            'mock'
      ],
      )
