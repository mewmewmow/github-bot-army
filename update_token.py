import json, base64, urllib.request
from nacl import public

repo = "mewmewmow/github-bot-army"
# Use current auth to get public key, then set new token as secret
current_token = open("/root/.gh_token_backup", "r").read().strip() if False else None

# Read token from environment
import os
token = os.environ.get("CURRENT_GH_TOKEN", "")

# Get repo public key using current token
req = urllib.request.Request(
    f"https://api.github.com/repos/{repo}/actions/secrets/public-key",
    headers={"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}
)
pub_key_data = json.loads(urllib.request.urlopen(req).read())
key_id = pub_key_data["key_id"]
public_key = public.PublicKey(base64.b64decode(pub_key_data["key"]))
sealed_box = public.SealedBox(public_key)

# New token to set
new_token = os.environ.get("NEW_GH_TOKEN", "")
encrypted = sealed_box.encrypt(new_token.encode())
encrypted_b64 = base64.b64encode(encrypted).decode()

data = json.dumps({"encrypted_value": encrypted_b64, "key_id": key_id}).encode()
req = urllib.request.Request(
    f"https://api.github.com/repos/{repo}/actions/secrets/GH_PAT",
    data=data,
    headers={"Authorization": f"token {token}", "Accept": "application/vnd.github+json", "Content-Type": "application/json"},
    method="PUT"
)
resp = urllib.request.urlopen(req)
print(f"✅ GH_PAT updated (status: {resp.status})")
