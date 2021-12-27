#!/usr/bin/env python3
# Python library to convert between Remind and iCalendar
#
# Copyright (C) 2015-2020 Jochen Sprickerhof
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

"""Python tool to sync between Remind and CalDAV."""

from argparse import ArgumentParser
from datetime import date, timedelta
from getpass import getpass
from netrc import netrc
from os.path import basename, expanduser, splitext
from sys import exit, stdin
from urllib.parse import urlparse

from caldav import Calendar, DAVClient
from dateutil.parser import parse
from dateutil.tz import gettz
from remind import Remind
from vobject import iCalendar

# pylint: disable=maybe-no-member


def main():
    """Command line tool to upload a Remind file to CalDAV."""
    parser = ArgumentParser(
        description="Command line tool to upload a Remind file to CalDAV"
    )
    parser.add_argument(
        "-z",
        "--zone",
        default="Europe/Berlin",
        help="Timezone of Remind file (default: Europe/Berlin)",
    )
    parser.add_argument(
        "-s",
        "--startdate",
        type=lambda s: parse(s).date(),
        default=date.today() - timedelta(weeks=12),
        help="Start offset for remind call (default: -12 weeks)",
    )
    parser.add_argument(
        "-m",
        "--month",
        type=int,
        default=15,
        help="Number of month to generate calendar beginning wit stadtdate (default: 15)",
    )
    parser.add_argument("-d", "--delete", action="store_true", help="Delete old events")
    parser.add_argument(
        "-r", "--davurl", required=True, help="The URL of the CalDAV server"
    )
    parser.add_argument("-u", "--davuser", help="The username for the CalDAV server")
    parser.add_argument("-p", "--davpass", help="The password for the CalDAV server")
    parser.add_argument(
        "-i", "--insecure", action="store_true", help="Ignore SSL certificate"
    )
    parser.add_argument(
        "infile",
        nargs="?",
        default=expanduser("~/.reminders"),
        help="The Remind file to process (default: ~/.reminders)",
    )
    parser.add_argument(
        "-o",
        "--old",
        default=None,
        help="The old reference Remind file (entries not in the current one will be deleted from dav)",
    )
    args = parser.parse_args()

    zone = gettz(args.zone)
    # Manually set timezone name to generate correct ical files
    # (python-vobject tests for the zone attribute)
    zone.zone = args.zone

    if args.infile == "-":
        remind = Remind(args.infile, zone, args.startdate, args.month)
        vobject = remind.stdin_to_vobject(stdin.read())
    else:
        remind = Remind(args.infile, zone, args.startdate, args.month)
        vobject = remind.to_vobject()

    if hasattr(vobject, "vevent_list"):
        ldict = {event.uid.value: event for event in vobject.vevent_list}
    else:
        ldict = {}

    if args.davuser and args.davpass:
        user = args.davuser
        passwd = args.davpass
    else:
        try:
            (user, _, passwd) = netrc().authenticators(urlparse(args.davurl).netloc)
        except (IOError, TypeError):
            if not args.davuser:
                print("rem2dav: Error, argument -u/--davuser or netrc is required")
                exit(1)
            user = args.davuser
            try:
                from keyring import get_password

                passwd = get_password(urlparse(args.davurl).netloc, user)
            except ImportError:
                passwd = None
            if not passwd:
                passwd = getpass()

    client = DAVClient(
        args.davurl, username=user, password=passwd, ssl_verify_cert=not args.insecure
    )
    calendar = Calendar(client, args.davurl)

    rdict = {
        splitext(basename(event.canonical_url))[0].replace("%40", "@"): event
        for event in calendar.events()
    }

    if args.old:
        old = Remind(args.old, zone, args.startdate, args.month)
        old_vobject = old.to_vobject()

        if hasattr(old_vobject, "vevent_list"):
            odict = {event.uid.value: event for event in old_vobject.vevent_list}
            intersect = rdict.keys() & odict.keys()
            rdict = {key: rdict[key] for key in intersect}
        else:
            rdict = {}

    local = ldict.keys() - rdict.keys()
    for uid in local:
        ncal = iCalendar()
        ncal.add(ldict[uid])
        calendar.add_event(ncal.serialize())

    if args.delete or args.old:
        remote = rdict.keys() - ldict.keys()
        for uid in remote:
            rdict[uid].delete()


if __name__ == "__main__":
    main()
