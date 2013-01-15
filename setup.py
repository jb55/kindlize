try:
    from setuptools import setup
except:
    from distutils.core import setup

setup(
    name='kindlize',
    version='0.0.1',
    author='Ying Zu',
    author_email='zuying@gmail.com',
    url='http://bitbucket.org/nye17/kindlize',
    py_modules=['kindlize'],
    packages=['kindlize_src'],
    package_data={'kindlize_src': ['clslib/*']},
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'kindlize = kindlize:_main',
        ],
    },
)
