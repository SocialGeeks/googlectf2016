There are a variety of client side machines that have access to certain
websites we'd like to access. We have a system in place, called "Opabina
Regalis" where we can intercept and modify HTTP requests on the fly. Can you
implement some attacks to gain access to those websites?

Opabina Regalis makes use of Protocol Buffers to send a short snippet of the
HTTP request for modification.

https://developers.google.com/protocol-buffers/

Here's the protocol buffer definition used:

package main;

message Exchange {
        enum VerbType {
                GET = 0;
                POST = 1;
        }

        message Header {
                required string key = 1;
                required string value = 2;
        }

        message Request {
                required VerbType ver = 1; // GET
                required string uri = 2; // /blah
                repeated Header headers = 3; // Accept-Encoding: blah
                optional bytes body = 4;
        }

        message Reply {
                required int32 status = 1; // 200 or 302
                repeated Header headers = 2;
                optional bytes body = 3;
        }

        oneof type {
                Request request = 1;
                Reply reply = 2;
        }
}
The network protocol uses a 32-bit little endian integer representing the
length of the marshalled protocol buffer, followed by the marshalled protocol
buffer.

Listening on port 1876 on ssl-added-and-removed-here.ctfcompetition.com
