import os, json, base64, urllib.request
from nacl import public

token = os.popen("gh auth token").read().strip()
repo = "mewmewmow/github-bot-army"

# Get repo public key
req = urllib.request.Request(
    f"https://api.github.com/repos/{repo}/actions/secrets/public-key",
    headers={"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}
)
pub_key_data = json.loads(urllib.request.urlopen(req).read())
key_id = pub_key_data["key_id"]
public_key = public.PublicKey(base64.b64decode(pub_key_data["key"]))
sealed_box = public.SealedBox(public_key)

# All secrets to set
secrets = {
    "SMTP_HOST": "smtp.gmail.com",
    "SMTP_PORT": "587",
    "SMTP_USER": "caasiyatnilab@gmail.com",
    "SMTP_PASS": "thankyou#77",
}

for name, value in secrets.items():
    encrypted = sealed_box.encrypt(value.encode())
    encrypted_b64 = base64.b64encode(encrypted).decode()
    data = json.dumps({"encrypted_value": encrypted_b64, "key_id": key_id}).encode()
    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/actions/secrets/{name}",
        data=data,
        headers={"Authorization": f"token {token}", "Accept": "application/vnd.github+json", "Content-Type": "application/json"},
        method="PUT"
    )
    resp = urllib.request.urlopen(req)
    print(f"✅ {name} set (status: {resp.status})")

# Trigger all bots
data = json.dumps({"ref": "main"}).encode()
req = urllib.request.Request(
    f"https://api.github.com/repos/{repo}/actions/workflows/start-all.yml/dispatches",
    data=data,
    headers={"Authorization": f"token {token}", "Accept": "application/vnd.github+json", "Content-Type": "application/json"},
    method="POST"
)
urllib.request.urlopen(req)
print("🚀 All bots triggered!")
print("\n🎉 COMPLETE! Check https://github.com/mewmewmow/github-bot-army/actions")
