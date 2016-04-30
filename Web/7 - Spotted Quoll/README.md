This blog on Zombie research looks like it might be interesting - can you break
into the /admin section?

https://spotted-quoll.ctfcompetition.com/

----

The base64 data that is set in the cookie is a Python pickle object.  Use the
repickle.py script to change the user to admin and then paste the output back
into the cookie.

Your flag is CTF{but_wait,theres_more.if_you_call} ... but is there more(1)? or
less(1)?
