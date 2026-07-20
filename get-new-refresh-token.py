#!/usr/bin/env python3
import base64
import json
import os
import secrets
import string
import requests


DATADIR = os.getenv("SF_DATADIR")
IDSECRETFN = os.getenv("SF_IDSECRETFN")
REFRESHTOKENFN = os.getenv("SF_REFRESHTOKENFN_MRMOBI")

ACCOUNTAPIROOT = "https://accounts.spotify.com"

SCOPE = "playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public user-library-read user-library-modify"
DEFAULT_REDIRECT_URI = "https://127.0.0.1:8888/callback"


def b64encode_idsecret(client_id, client_secret):
    return base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()


def get_client_creds():
    print("How to get Client Credentials:")
    print("  1. Go to https://developer.spotify.com/dashboard")
    print("  2. Open your App -> Settings")
    print("  3. Copy Client ID and Client Secret\n")

    use_existing = input(f"Read from existing file \"{DATADIR}{IDSECRETFN}\"? [Y/n]: ").strip().lower()

    if use_existing in ("", "y", "yes"):
        try:
            with open(f"{DATADIR}{IDSECRETFN}", "r") as f:
                idsecret64 = "".join(f.readlines()).strip()
            print("  > Loaded from file.\n")
            return idsecret64, None, None
        except Exception as e:
            print(f"  > Could not read file: {e}\n")

    client_id = input("Enter Client ID: ").strip()
    client_secret = input("Enter Client Secret: ").strip()

    if not client_id or not client_secret:
        print("[ERROR] Client ID and Client Secret are required.")
        exit(1)

    idsecret64 = b64encode_idsecret(client_id, client_secret)
    print("  > Base64 encoded.\n")
    return idsecret64, client_id, client_secret


def build_authorize_url(client_id, redirect_uri):
    state = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))
    url = (
        f"{ACCOUNTAPIROOT}/authorize"
        f"?client_id={client_id}"
        f"&response_type=code"
        f"&redirect_uri={redirect_uri}"
        f"&state={state}"
        f"&scope={SCOPE.replace(' ', '%20')}"
    )
    return url, state


def exchange_code(idsecret64, code, redirect_uri):
    url = f"{ACCOUNTAPIROOT}/api/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {idsecret64}"
    }
    body = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
    }

    res = requests.post(url=url, headers=headers, data=body)

    if not res.ok:
        print(f"[ERROR] Spotify API returned {res.status_code}: {res.text}")
        exit(1)

    return json.loads(res.text)


##### START ###############

print("--- Spotify: Get New Refresh Token ---\n")

idsecret64, client_id, client_secret = get_client_creds()

# If we only have the base64 string, decode it for the authorize URL
if client_id is None:
    try:
        decoded = base64.b64decode(idsecret64).decode()
        client_id, client_secret = decoded.split(":", 1)
    except Exception:
        print("[ERROR] Could not decode existing idsecret file. Enter credentials manually next time.")
        exit(1)

redirect_uri = input(f"Enter Redirect URI [{DEFAULT_REDIRECT_URI}]: ").strip()
if not redirect_uri:
    redirect_uri = DEFAULT_REDIRECT_URI

print("\n--- Step 1: Authorize in Browser ---")
auth_url, state = build_authorize_url(client_id, redirect_uri)
print(f"\nOpen this URL in your browser:\n{auth_url}\n")
print("Log in, authorize the app.")
print("You will be redirected to a URL like:")
print(f"  {redirect_uri}?code=...&state=...\n")

code = input("Paste the full callback URL (or just the 'code' parameter value): ").strip()

# Extract code if user pasted the full URL
if "code=" in code:
    from urllib.parse import parse_qs, urlparse
    parsed = urlparse(code)
    params = parse_qs(parsed.query)
    code = params.get("code", [code])[0]

print("\n--- Step 2: Exchange Code for Refresh Token ---")
token_data = exchange_code(idsecret64, code, redirect_uri)

refresh_token = token_data.get("refresh_token")
if not refresh_token:
    print(f"[ERROR] No refresh_token in response: {json.dumps(token_data, indent=2)}")
    exit(1)

print(f"  > Got refresh token: {refresh_token[:40]}...")

try:
    os.makedirs(DATADIR, exist_ok=True)
    with open(f"{DATADIR}{REFRESHTOKENFN}", "w") as f:
        f.write(refresh_token)
    print(f"  > Written to \"{DATADIR}{REFRESHTOKENFN}\"")
except Exception as e:
    print(f"[ERROR] Could not write refresh token: {e}")
    exit(1)

print("\nDone. New refresh token saved.")
