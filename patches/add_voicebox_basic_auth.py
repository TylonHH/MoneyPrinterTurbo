from pathlib import Path

path = Path('/MoneyPrinterTurbo/app/services/voice.py')
text = path.read_text(encoding='utf-8')

marker = '''def get_voicebox_voices() -> list[str]:\n'''
helper = '''def get_voicebox_auth():\n    \"\"\"Return HTTP Basic Auth credentials for self-hosted Voicebox.\n\n    Credentials are read from environment variables first so secrets never need\n    to be stored in config.toml or the repository. Config values remain an\n    optional fallback for non-container deployments.\n    \"\"\"\n    username = str(\n        os.getenv(\"VOICEBOX_AUTH_USERNAME\", \"\")\n        or config.voicebox.get(\"auth_username\", \"\")\n        or \"\"\n    ).strip()\n    password = str(\n        os.getenv(\"VOICEBOX_AUTH_PASSWORD\", \"\")\n        or config.voicebox.get(\"auth_password\", \"\")\n        or \"\"\n    )\n    if username or password:\n        return (username, password)\n    return None\n\n\n'''
if helper not in text:
    if marker not in text:
        raise RuntimeError('Voicebox profile function marker not found')
    text = text.replace(marker, helper + marker, 1)

text = text.replace(
    'response = requests.get(f"{base_url}/profiles", timeout=timeout)',
    'response = requests.get(f"{base_url}/profiles", timeout=timeout, auth=get_voicebox_auth())',
)
text = text.replace(
    '            json=payload,\n            timeout=timeout,\n        )',
    '            json=payload,\n            timeout=timeout,\n            auth=get_voicebox_auth(),\n        )',
    1,
)
text = text.replace(
    '            f"{base_url}/audio/{generation_id}",\n            timeout=timeout,\n        )',
    '            f"{base_url}/audio/{generation_id}",\n            timeout=timeout,\n            auth=get_voicebox_auth(),\n        )',
    1,
)

path.write_text(text, encoding='utf-8')
print('Voicebox Basic Auth patch applied successfully')
