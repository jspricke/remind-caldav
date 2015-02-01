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
from os.path import basename, expanduser, splitext
from remind import Remind
# pylint: disable=maybe-no-member

def main():
    """Command line tool to download from CalDAV to Remind"""

    parser = ArgumentParser(description='Command line tool to download from CalDAV to Remind')
    parser.add_argument('infile', nargs='?', default=expanduser('~/.reminders'),
                        help='The Remind file to process (default: ~/.reminders)')
    parser.add_argument('davurl', help='The URL of the calDAV server')
    parser.add_argument('davuser', help='The username for the calDAV server')
    parser.add_argument('davcal', help='The calendar name on the calDAV server')
    args = parser.parse_args()

    rem = Remind(args.infile)

    ldict = {uid: None for uid in rem.get_uids(args.infile)}

    passwd = getpass()
    client = DAVClient(args.davurl, username=args.davuser, password=passwd)
    principal = client.principal()
    calendar = principal.calendars()[args.davcal]

    rdict = {splitext(basename(event.canonical_url))[0] : event for event in calendar.events()}

    local = ldict.viewkeys() - rdict.viewkeys()

    for uid in local:
        rem.remove(uid, rem.get_filesnames()[0])

    remote = rdict.viewkeys() - ldict.viewkeys()

    for uid in remote:
        vevent = rdict[uid]
        vevent.load()
        rem.append(vevent.data, rem.get_filesnames()[0])

if __name__ == '__main__':
    main()
