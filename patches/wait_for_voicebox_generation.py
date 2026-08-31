from pathlib import Path

path = Path('/MoneyPrinterTurbo/app/services/voice.py')
text = path.read_text(encoding='utf-8')

old = '''        audio = requests.get(\n            f"{base_url}/audio/{generation_id}",\n            timeout=timeout,\n            auth=get_voicebox_auth(),\n        )\n        audio.raise_for_status()\n'''

new = '''        # Voicebox queues generation asynchronously. POST /generate returns the\n        # generation row immediately with status=generating, so wait for a\n        # terminal state before requesting /audio/{id}.\n        deadline = time.monotonic() + timeout\n        while True:\n            history_response = requests.get(\n                f"{base_url}/history/{generation_id}",\n                timeout=min(timeout, 30),\n                auth=get_voicebox_auth(),\n            )\n            history_response.raise_for_status()\n            history_data = history_response.json()\n            status = str(history_data.get("status", "") or "").strip().lower()\n\n            if status == "completed":\n                break\n            if status == "failed":\n                error = history_data.get("error") or "Voicebox generation failed"\n                logger.error(f"Voicebox generation failed: {error}")\n                return None\n            if time.monotonic() >= deadline:\n                logger.error(\n                    f"Voicebox generation timed out after {timeout}s: {generation_id}"\n                )\n                return None\n            time.sleep(1.0)\n\n        audio = requests.get(\n            f"{base_url}/audio/{generation_id}",\n            timeout=timeout,\n            auth=get_voicebox_auth(),\n        )\n        audio.raise_for_status()\n'''

if old not in text:
    raise RuntimeError('Voicebox audio fetch block not found')

path.write_text(text.replace(old, new, 1), encoding='utf-8')
print('Voicebox async generation wait patch applied successfully')
