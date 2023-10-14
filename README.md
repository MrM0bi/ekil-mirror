# ekil-mirror

A script to sync liked tracks on Spotify to a specific Playlist


### Basic Instructions
Before beeing able to use this a Spotify User needs to do the following

1. Create a "Spotify-App" in the Spotify Developer Dashboard
2. Get a normal Access Token using the API
3. Create a URL to open in the Browser where the user Authorizes the App to access his account
4. Then exchange a value returned by the Browser (in the URL) with a permanent "Refresh Token" that is specific for this user (API)

> Spotify API Reference: https://developer.spotify.com/documentation/web-api/tutorials/getting-started


### Envoirement Variables

- **TGB_MRMOBOT** = Telegram Bot Token for Alerts
- **TGC_OCLT_ALERT** = Telegram Group Chat ID for the Alerts
- **SF_DATADIR** = Directory where the Token/Secret Files are located
- **SF_IDSECRETFN** = Filename for the file containig a base64 encoded version of <clientid>:<clientsecret>
- **SF_REFRESHTOKENFN_MRMOBI** = Filename for the file containing the user specific refresh Token
- **SF_CURRENTACCESSTOKENFN_MRMOBI** = Filename for the file containing the current Access-Token
- **SF_LIKEMIRRORPLAYLISTID_MRMOBI** = The Spotify Playlist-ID where the Likes should be syncronized to
