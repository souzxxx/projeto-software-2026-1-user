import os
from functools import wraps

import jwt
from flask import current_app, jsonify, request

AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN", "dev-dmenygalfla4soba.us.auth0.com")
AUTH0_AUDIENCE = os.environ.get(
    "AUTH0_AUDIENCE", "https://dev-dmenygalfla4soba.us.auth0.com/api/v2/"
)
AUTH0_ISSUER = f"https://{AUTH0_DOMAIN}/"
JWKS_URL = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"

_jwks_client = jwt.PyJWKClient(JWKS_URL)


def _unauthorized(message):
    return jsonify({"error": "unauthorized", "message": message}), 401


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_app.config.get("AUTH_DISABLED"):
            return f(*args, **kwargs)

        auth_header = request.headers.get("Authorization", "")
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return _unauthorized("missing or malformed Authorization header")

        token = parts[1]
        try:
            signing_key = _jwks_client.get_signing_key_from_jwt(token).key
            jwt.decode(
                token,
                signing_key,
                algorithms=["RS256"],
                audience=AUTH0_AUDIENCE,
                issuer=AUTH0_ISSUER,
            )
        except jwt.PyJWTError as e:
            return _unauthorized(str(e))

        return f(*args, **kwargs)

    return decorated
