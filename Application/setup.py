from setuptools import setup, find_packages
from DocuTrace import __version__

setup(name="DocuTrace", 
    version=__version__,
    url='https://github.com/friedforfun/DocumentTracking',
    author='Sam Fay-hunt',
    author_email='sf52@hw.ac.uk',
    scripts=['docutrace'],
    packages=find_packages()
)
