########################
# Sparks IRC framework
# CAP negotiation
# Provides a mechanism to enable/disable capabilities
# from the IRC CAP protocol as specified here:
#	<http://www.leeh.co.uk/draft-mitchell-irc-capabilities-02.html>
# Author: Josh "SnoFox" Johnson
# License:
# Copyright (c) 2012, Josh Johnson <snofox@snofox.net>
#
# Permission to use, copy, modify, and/or distribute this 
# software for any purpose with or without fee is hereby 
# granted, provided that the above copyright notice and 
# this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS 
# ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL 
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO
# EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER
# RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN
# AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION,
# ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE
# OF THIS SOFTWARE.
########################

def event_preconnect( irc ):
	irc.cap = [False] # Assume the IRCd doesn't support CAP
	irc.push( 'CAP LS' )

def sr_451( irc, client, target, params ):
	# :logik.nj.us.synirc.net 451 CAP :You have not registered
	# When requesting CAP before registering on old-Unreal
	if params[0] == 'CAP':
		print "Your IRCd doesn't support CAP. It will probably desync the userlist. :("

def sr_421( irc, client, target, params ):
	# :void.ext3.net 421 netcat ASFD :Unknown command
	if params[0] == 'CAP':
		print "Your IRCd doesn't support CAP. It will probably desync the userlist. :("


def sr_cap( irc, client, target, params ):
	subcmd = params[0].upper()
	
	if subcommand == "LS":
        # that's great. who requested CAP LS and why? We don't care,
        # Should we?
        pass

