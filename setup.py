from setuptools import setup

setup(name='remind-caldav',
      version='0.1.0',
      description='''
       Remind CalDAV tools
       ''',
      author='Jochen Sprickerhof',
      author_email='remind@jochen.sprickerhof.de',
      license='GPLv3+',
      url='https://github.com/jspricke/remind-caldav',
      keywords=['Remind'],
      classifiers=[
          'Programming Language :: Python',
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
          'Topic :: Office/Business :: Scheduling',
          ],

      install_requires=['remind', 'caldav', 'python-dateutil', 'vobject'],
      py_modules=['rem2dav', 'dav2rem'],

      entry_points={
          'console_scripts': [
              'rem2dav = rem2dav:main',
              'dav2rem = dav2rem:main',
              ]
          },)
