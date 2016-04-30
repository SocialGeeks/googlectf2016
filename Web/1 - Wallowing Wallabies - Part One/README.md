Wallowing Wallabies provides enterprise contract management - we'd like to find
out how easy it is to perform corporate espionage against them. Visit them
here.

Please note Please do not run automated scanners against the target - that's
not the intended solution. Instead, perhaps look up "xss cookie catching", "xss
cookie stealing" and other documents along those lines. Thanks!

https://wallowing-wallabies.ctfcompetition.com/

----

robots.txt revealed pages

User-agent: *
Disallow: /deep-blue-sea/
Disallow: /deep-blue-sea/team/
# Yes, these are alphabet puns :)
Disallow: /deep-blue-sea/team/characters
Disallow: /deep-blue-sea/team/paragraphs
Disallow: /deep-blue-sea/team/lines
Disallow: /deep-blue-sea/team/runes
Disallow: /deep-blue-sea/team/vendors

vendors was vulnerable to an XSS attack that allowed us to steal the admin
cookie.
