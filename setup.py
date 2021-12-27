from os import path

from setuptools import setup

ROOTDIR = path.abspath(path.dirname(__file__))
with open(path.join(ROOTDIR, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="remind-caldav",
    version="0.8.0",
    description="""
       Remind CalDAV tools
       """,
    long_description=long_description,
    long_description_content_type="text/x-rst",
    author="Jochen Sprickerhof",
    author_email="remind@jochen.sprickerhof.de",
    license="GPLv3+",
    url="https://github.com/jspricke/remind-caldav",
    keywords=["Remind"],
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Topic :: Office/Business :: Scheduling",
    ],
    install_requires=["remind", "caldav", "python-dateutil", "vobject"],
    py_modules=["rem2dav", "dav2rem"],
    entry_points={
        "console_scripts": [
            "rem2dav = rem2dav:main",
            "dav2rem = dav2rem:main",
        ]
    },
)
