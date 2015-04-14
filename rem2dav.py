#!/usr/bin/env python
# Python library to convert between Remind and iCalendar
#
# Copyright (C) 2015  Jochen Sprickerhof
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Python tool to sync between Remind and CalDAV"""

from argparse import ArgumentParser
from caldav import DAVClient
from datetime import date
from dateutil.parser import parse
from dateutil.tz import gettz
from getpass import getpass
from netrc import netrc
from os.path import basename, expanduser, splitext
from remind import Remind
from urlparse import urlparse
from sys import stdin
from vobject import iCalendar
# pylint: disable=maybe-no-member


def main():
    """Command line tool to upload a Remind file to CalDAV"""

    parser = ArgumentParser(description='Command line tool to upload a Remind file to CalDAV')
    parser.add_argument('-z', '--zone', default='Europe/Berlin',
                        help='Timezone of Remind file (default: Europe/Berlin)')
    parser.add_argument('-s', '--startdate', type=lambda s: parse(s).date(),
                        default=date.today(), help='Start offset for remind call')
    parser.add_argument('-m', '--month', type=int, default=15,
                        help='Number of month to generate calendar beginning wit stadtdate (default: 15)')
    parser.add_argument('-d', '--delete', type=bool, default=False,
                        help='Delete old events')
    parser.add_argument('-r', '--davurl', required=True, help='The URL of the calDAV server')
    parser.add_argument('-u', '--davuser', help='The username for the calDAV server')
    parser.add_argument('infile', nargs='?', default=expanduser('~/.reminders'),
                        help='The Remind file to process (default: ~/.reminders)')
    args = parser.parse_args()

    zone = gettz(args.zone)
    # Manually set timezone name to generate correct ical files
    # (python-vobject tests for the zone attribute)
    zone.zone = args.zone

    if args.infile == '-':
        remind = Remind(args.infile, zone, args.startdate, args.month)
        vobject = remind.stdin_to_vobject(stdin.read().decode('utf-8'))
    else:
        remind = Remind(args.infile, zone, args.startdate, args.month)
        vobject = remind.to_vobject()

    ldict = {event.uid.value: event for event in vobject.vevent_list}

    try:
        (user, _, passwd) = netrc().authenticators(urlparse(args.davurl).netloc)
    except (IOError, TypeError):
        if not args.davuser:
            print "rem2dav: error: argument -u/--davuser is required"
            return 2
        user = args.davuser
        passwd = getpass()

    client = DAVClient(args.davurl, username=user, password=passwd)
    principal = client.principal()
    calendar = principal.calendars()[0]

    rdict = {splitext(basename(event.canonical_url))[0].replace('%40', '@'): event for event in calendar.events()}

    local = ldict.viewkeys() - rdict.viewkeys()
    for uid in local:
        ncal = iCalendar()
        ncal.add(ldict[uid])
        calendar.add_event(ncal.serialize())

    if args.delete:
        remote = rdict.viewkeys() - ldict.viewkeys()
        for uid in remote:
            rdict[uid].delete()

if __name__ == '__main__':
    main()
