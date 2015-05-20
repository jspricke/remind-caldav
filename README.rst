CalDAV client to sync to Remind
===============================

Needs python-remind, python-caldav, python-dateuil and vobject libraries

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
