from setuptools import setup, find_packages

PACKAGE_VERSION = '0.1'
requirements = open("requirements.txt").readlines()

setup(name="funsize",
      version=PACKAGE_VERSION,
      description="Partial MAR webservice",
      long_description="https://wiki.mozilla.org/User:Ffledgling/Senbonzakura",
      author='Anhad Jai Singh',
      author_email='ffledgling@gmail.com',
      url='https://github.com/mozilla/build-funsize',
      license='MPL',
      packages=find_packages(),
      install_requires=requirements,
      )
