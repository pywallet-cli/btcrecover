#!/usr/bin/env python

# btcrecover.py -- Bitcoin wallet password recovery tool
# Copyright (C) 2014-2017 Christopher Gurnee
#
# This program is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version
# 2 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/

# If you find this program helpful, please consider a small
# donation to the developer at the following Bitcoin address:
#
#           bc1qqtspvvyl5nv2dwffd0zwppledlmct7sydpd9l5
#
#                      Thank You!

# PYTHON_ARGCOMPLETE_OK - enables optional bash tab completion

import compatibility_check

from btcrecover import btcrpass
import sys, multiprocessing

if __name__ == "__main__":
	print()
	print("Starting", btcrpass.full_version(),
		  file=sys.stderr if any(a.startswith("--listp") for a in sys.argv[1:]) else sys.stdout)  # --listpass

	btcrpass.parse_arguments(sys.argv[1:])
	(password_found, not_found_msg) = btcrpass.main()

	if isinstance(password_found, str):
		print()
		print("If this tool helped you to recover funds, please consider donating 1% of what you recovered, in your crypto of choice to:")
		print("BTC: bc1qqtspvvyl5nv2dwffd0zwppledlmct7sydpd9l5 ")
		print()
		print("Find me on Reddit @ https://www.reddit.com/user/Crypto-Guide")
		print()
		print("You may also consider donating to Gurnec, who created and maintained this tool until late 2017 @ 3Au8ZodNHPei7MQiSVAWb7NB2yqsb48GW4")
		print()
		btcrpass.safe_print("Password found: '" + password_found + "'")
		if any(ord(c) < 32 or ord(c) > 126 for c in password_found):
			print("HTML Encoded Password:   '" + password_found.encode("ascii", "xmlcharrefreplace").decode() + "'")
		retval = 0

	elif not_found_msg:
		print(not_found_msg, file=sys.stderr if btcrpass.args.listpass else sys.stdout)
		retval = 0

	else:
		retval = 1  # An error occurred or Ctrl-C was pressed

	# Wait for any remaining child processes to exit cleanly (to avoid error messages from gc)
	for process in multiprocessing.active_children():
		process.join(1.0)

	sys.exit(retval)
