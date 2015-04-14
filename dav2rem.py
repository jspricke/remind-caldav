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
from getpass import getpass
from netrc import netrc
from os.path import basename, expanduser, splitext
from remind import Remind
from urlparse import urlparse
# pylint: disable=maybe-no-member


def main():
    """Command line tool to download from CalDAV to Remind"""

    parser = ArgumentParser(description='Command line tool to download from CalDAV to Remind')
    parser.add_argument('-d', '--delete', type=bool, default=False,
                        help='Delete old events')
    parser.add_argument('-r', '--davurl', required=True, help='The URL of the calDAV server')
    parser.add_argument('-u', '--davuser', help='The username for the calDAV server')
    parser.add_argument('remfile', nargs='?', default=expanduser('~/.reminders'),
                        help='The Remind file to process (default: ~/.reminders)')
    args = parser.parse_args()

    rem = Remind(args.remfile)
    ldict = set(rem.get_uids())

    try:
        (user, _, passwd) = netrc().authenticators(urlparse(args.davurl).netloc)
    except (IOError, TypeError):
        if not args.davuser:
            print "dav2rem: error: argument -u/--davuser is required"
            return 2
        user = args.davuser
        passwd = getpass()

    client = DAVClient(args.davurl, username=user, password=passwd)
    principal = client.principal()
    calendar = principal.calendars()[0]

    rdict = {splitext(basename(event.canonical_url))[0].replace('%40', '@'): event for event in calendar.events()}

    if args.delete:
        local = ldict - rdict.viewkeys()
        for uid in local:
            rem.remove(uid)

    remote = rdict.viewkeys() - ldict
    for uid in remote:
        vevent = rdict[uid]
        vevent.load()
        rem.append(vevent.data)

if __name__ == '__main__':
    main()
