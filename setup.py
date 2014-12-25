from setuptools import setup, find_packages

PACKAGE_VERSION = '0.1'

setup(name="funsize",
      version=PACKAGE_VERSION,
      description="Partial MAR webservice",
      long_description="https://wiki.mozilla.org/User:Ffledgling/Senbonzakura",
      author='Anhad Jai Singh',
      author_email='ffledgling@gmail.com',
      url='https://github.com/mozilla/build-funsize',
      license='MPL',
      packages=find_packages(),
      install_requires=[
          'celery==3.1.11',
          'Flask==0.10.1',
          'requests==2.2.1',
          'boto==2.33.0',
          'sh==1.09',
          'mar>=1.0',
      ],
      )
