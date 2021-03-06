from flask import Flask, request, abort
import json
from functools import wraps
from jose import jwt
from urllib.request import urlopen

# https://starpad.eu.auth0.com/authorize?audience=http://localhost:5000&response_type=token&client_id=MuqhweOPpjjzJVyw2C9BoHjUbrNF2NDz&redirect_uri=http://localhost:5000
# eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkRrM21iVlFWUEloZUpRdEFLOTVkRCJ9.eyJpc3MiOiJodHRwczovL3N0YXJwYWQuZXUuYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfDYwMTgyMDhjNTIzOGZiMDA2OTYzNTRhOCIsImF1ZCI6Imh0dHA6Ly9sb2NhbGhvc3Q6NTAwMCIsImlhdCI6MTYxMjI4MzQ4NSwiZXhwIjoxNjEyMjkwNjg1LCJhenAiOiJNdXFod2VPUHBqanpKVnl3MkM5Qm9IalVick5GMk5EeiIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOltdfQ.QsT4vTK6BWgNRXD-2vg1on8VfkiB_YfbAGGrJ1FuPZyC8wPs8XralRKXdpLqBPPpqaqvneEmKOPnfu4gooLjlH0B3hL2ljUtSzm0iIIrZF37tY__vngcRVVBkj2iLWbvsRxM84RReTxwEvgRxpgEtFxqKw0Xi-geDiQ4PtoCzSHFS4tx_h_d-9GJ5tFijMwKrFVwqBrltYXwmEkYyH7kk-WPFqS1u_9oCWe2Vc-dlVULU32plxiahutmOp6Yj3d4t2oajnVtfntWCvdrWsTO1n-CaQ-BIZnjCqS10Ny3TZzpo4Iwfazb7WM4fgo1RWPoHZAcbLeeC5_MDV1ZjgIsdw

app = Flask(__name__)

AUTH0_DOMAIN = 'starpad.eu.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'http://localhost:5000'


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.headers.get('Authorization', None)
    if not auth:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)

    parts = auth.split()
    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)

    elif len(parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found.'
        }, 401)

    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
        }, 401)

    token = parts[1]
    return token


def verify_decode_jwt(token):
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
            }, 400)

def check_permissions(permission, payload):
    if 'permissions' not in payload:
        abort(400)

    if permission not in payload['permissions']:
        abort(403)

def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            try:
                payload = verify_decode_jwt(token)
            except:
                abort(401)

            check_permissions(permission, payload)

            return f(payload, *args, **kwargs)
        return wrapper
    return requires_auth_decorator

@app.route('/image')
@requires_auth('get:images')
def headers(payload):

    print(payload)
    return 'Access Granted'