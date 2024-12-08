#!/usr/bin/env python3

"""
Current - testing JWT validation.
"""
import jwt
from json import loads
from os import environ
from datetime import datetime
from flask import (Flask, request)

jwk =  loads(open("jwks.json", "r").read())

def jwtDecode(inp):
    header = jwt.get_unverified_header(inp)
    for i in jwk["keys"]:
        if header["kid"] == i["kid"]:
            pubkey = jwt.algorithms.RSAAlgorithm.from_jwk(i)
            #TODO - when converting to flask endpoint, verify token claims
            try:
                out = jwt.decode(inp, pubkey, algorithms=["RS256"],
                                 options={"require": ["exp", "iss", "client_id"],
                                          "verify_exp": datetime.now()},
                                 iss=f"https://cognito-idp.{environ['AWS_REGION']}.amazonaws.com/{environ['COGNITO_POOL_ID']}")
                return out if out["client_id"] in [environ["COGNITO_CLIENT_ID"]] and \
                    out["token_use"]=="access" else None
            except:
                return None
    return None

app = Flask(__name__)

@app.route("/userData", methods=["GET"])
def userData():
    if "x-access-tokens" not in request.headers:
        return "No bearer token supplied", 401