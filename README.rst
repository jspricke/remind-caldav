CalDAV client to sync to Remind
===============================

Tools to sync from CalDAV to Remind (``dav2rem.py``) and the other way round (``rem2dav.py``).

Installation
------------

You need to have the Remind command line tool installed.
For Debian/Ubuntu use::

  $ sudo apt-get install remind

Using pip
~~~~~~~~~

::

  $ pip install remind-caldav

This will install all Python dependencies as well.

Using python-setuptools
~~~~~~~~~~~~~~~~~~~~~~~

::

  $ python setup.py install

Providing the Password
----------------------

There are a number of options how to provide the CalDAV password:

* Use a `netrc(5) <http://linux.die.net/man/5/netrc>`_ file (<domain> being the
  domain part of the CalDAV URL):

::

  machine <domain> login <user> password <password>

* Use `python-keyring <https://pypi.python.org/pypi/keyring>`_ with the CalDAV
  URL as the service.
* Providing a password on the command line. Note that this leaks into the
  environment.
* If no password is provided, the tools will ask for one.


How to connect to Google
------------------------

Go to https://www.google.com/settings/security/lesssecureapps and enable
"Access for less secure apps". This enables basic HTTP authentication as OAuth2
is not supported by python-caldav.

URL: https://www.google.com/calendar/dav/calid/user

  Where calid should be replaced by the "calendar ID" of the calendar to be
  accessed. This can be found through the Google Calendar web interface as
  follows: in the pull-down menu next to the calendar name, select Calendar
  Settings. On the resulting page the calendar ID is shown in a section labelled
  Calendar Address. The calendar ID for a user's primary calendar is the same as
  that user's email address.

https://developers.google.com/google-apps/calendar/caldav/v2/guide
