from setuptools import setup, find_packages

version = '0.0.2'

setup(
    name = 'isotoma.zope.groupreadableblobstorage',
    version = version,
    url = "http://github.com/isotoma/isotoma.zope.groupreadableblobstorage",
    maintainer = "John Carr",
    maintainer_email = "john.carr@isotoma.com",
    description = "Make blob storage group readable",
    long_description = open('README.rst').read(),
    package_data = {
        '': ['README.rst', ],
    },
    packages = find_packages(exclude=['ez_setup']),
    namespace_packages = ['isotoma', 'isotoma.zope'],
    include_package_data = True,
    zip_safe = False,
    install_requires = [
        'setuptools',
    ],
    entry_points="""
        # -*- Entry points: -*-
       [z3c.autoinclude.plugin]
       target = plone
       """,
)
