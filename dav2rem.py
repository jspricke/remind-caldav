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
from getpass import getpass
from netrc import netrc
from os.path import basename, expanduser, splitext
from sys import exit
from urllib.parse import urlparse

from caldav import Calendar, DAVClient
from remind import Remind
from vobject import readOne

# pylint: disable=maybe-no-member


def main():
    """Command line tool to download from CalDAV to Remind."""
    parser = ArgumentParser(
        description="Command line tool to download from CalDAV to Remind"
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
        "remfile",
        nargs="?",
        default=expanduser("~/.reminders"),
        help="The Remind file to process (default: ~/.reminders)",
    )
    args = parser.parse_args()

    # create empty file if it does not exist
    open(args.remfile, "a")

    rem = Remind(args.remfile)
    ldict = set(rem.get_uids())

    if args.davuser and args.davpass:
        user = args.davuser
        passwd = args.davpass
    else:
        try:
            (user, _, passwd) = netrc().authenticators(urlparse(args.davurl).netloc)
        except (IOError, TypeError):
            if not args.davuser:
                print("dav2rem: Error, argument -u/--davuser or netrc is required")
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

    if args.delete:
        local = ldict - rdict.keys()
        for uid in local:
            rem.remove(uid)

    remote = rdict.keys() - ldict
    for uid in remote:
        vevent = rdict[uid]
        rem.append_vobject(readOne(vevent.data))


if __name__ == "__main__":
    main()
