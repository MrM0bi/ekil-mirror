# ekil-mirror

A script to sync liked tracks on Spotify to a specific Playlist


### Basic Instructions
Before beeing able to use this a Spotify User needs to do the following

1. Create a "Spotify-App" in the Spotify Developer Dashboard
2. Run `get-new-refresh-token.py` to get a user-specific Refresh Token

**NOTE**: The Refresh Token is valid for 180 days (6 months) afterwards it has to be refreshed using the same script.

> Spotify API Reference: https://developer.spotify.com/documentation/web-api/tutorials/getting-started


### get-new-refresh-token.py

Automates the OAuth Authorization Code flow to obtain a new Refresh Token.

1. Run the script: `./get-new-refresh-token.py`
2. Enter Client ID and Client Secret (or reuse existing file)
3. Open the printed URL in a browser, log in, and authorize
4. Paste the callback URL back into the terminal
5. Script saves the Refresh Token to `{SF_DATADIR}{SF_REFRESHTOKENFN_MRMOBI}`

Requires `SF_DATADIR` and `SF_REFRESHTOKENFN_MRMOBI` to be set. Reads
`{SF_DATADIR}{SF_IDSECRETFN}` if available, else prompts for credentials.


### Envoirement Variables

- **TGB_MRMOBOT** = Telegram Bot Token for Alerts
- **TGC_OCLT_ALERT** = Telegram Group Chat ID for the Alerts
- **SF_DATADIR** = Directory where the Token/Secret Files are located
- **SF_IDSECRETFN** = Filename for the file containig a base64 encoded version of <clientid>:<clientsecret>
- **SF_REFRESHTOKENFN_MRMOBI** = Filename for the file containing the user specific refresh Token
- **SF_CURRENTACCESSTOKENFN_MRMOBI** = Filename for the file containing the current Access-Token
- **SF_LIKEMIRRORPLAYLISTID_MRMOBI** = The Spotify Playlist-ID where the Likes should be syncronized to
