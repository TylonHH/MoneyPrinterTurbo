from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"patch marker not found in {path}: {old[:120]!r}")
    p.write_text(text.replace(old, new, 1), encoding="utf-8")


# ---------------------------------------------------------------------------
# app/config/config.py
# ---------------------------------------------------------------------------
replace_once(
    "/MoneyPrinterTurbo/app/config/config.py",
    '        config_to_save["chatterbox"] = dict(chatterbox)\n        config_to_save["fish_audio"] = dict(fish_audio)',
    '        config_to_save["chatterbox"] = dict(chatterbox)\n        config_to_save["voicebox"] = dict(voicebox)\n        config_to_save["fish_audio"] = dict(fish_audio)',
)
replace_once(
    "/MoneyPrinterTurbo/app/config/config.py",
    'chatterbox = _SynchronizedConfig(_cfg.get("chatterbox", {}))\nfish_audio = _SynchronizedConfig(_cfg.get("fish_audio", {}))',
    'chatterbox = _SynchronizedConfig(_cfg.get("chatterbox", {}))\nvoicebox = _SynchronizedConfig(_cfg.get("voicebox", {}))\nfish_audio = _SynchronizedConfig(_cfg.get("fish_audio", {}))',
)

# ---------------------------------------------------------------------------
# app/services/voice.py
# ---------------------------------------------------------------------------
voicebox_helpers = r'''

def get_voicebox_voices() -> list[str]:
    """Fetch reusable voice profiles from a self-hosted Voicebox instance."""
    base_url = str(
        config.voicebox.get("base_url", "http://srv-captain--voicebox")
        or "http://srv-captain--voicebox"
    ).rstrip("/")
    timeout = float(config.voicebox.get("timeout", 30) or 30)
    try:
        response = requests.get(f"{base_url}/profiles", timeout=timeout)
        response.raise_for_status()
        profiles = response.json()
        if not isinstance(profiles, list):
            logger.warning("Voicebox profiles response is not a list")
            return []
        result = []
        for profile in profiles:
            if not isinstance(profile, dict):
                continue
            profile_id = str(profile.get("id", "") or "").strip()
            name = str(profile.get("name", "") or profile_id).strip()
            if profile_id:
                result.append(f"voicebox:{profile_id}:{name}")
        return result
    except Exception as exc:
        logger.warning(f"Voicebox voices fetch failed: {exc}")
        return []


def is_voicebox_voice(voice_name: str) -> bool:
    return (voice_name or "").startswith("voicebox:")


def voicebox_tts(
    text: str,
    profile_id: str,
    voice_file: str,
    voice_rate: float = 1.0,
    voice_volume: float = 1.0,
):
    """Generate speech through Voicebox and save it in MoneyPrinterTurbo's target format."""
    base_url = str(
        config.voicebox.get("base_url", "http://srv-captain--voicebox")
        or "http://srv-captain--voicebox"
    ).rstrip("/")
    timeout = float(config.voicebox.get("timeout", 600) or 600)
    language = str(config.voicebox.get("language", "de") or "de").strip()

    payload = {
        "profile_id": profile_id,
        "text": text,
        "language": language,
    }
    engine = str(config.voicebox.get("engine", "") or "").strip()
    model_size = str(config.voicebox.get("model_size", "") or "").strip()
    instruct = str(config.voicebox.get("instruct", "") or "").strip()
    if engine:
        payload["engine"] = engine
    if model_size:
        payload["model_size"] = model_size
    if instruct:
        payload["instruct"] = instruct

    try:
        generation = requests.post(
            f"{base_url}/generate",
            json=payload,
            timeout=timeout,
        )
        generation.raise_for_status()
        generation_data = generation.json()
        generation_id = str(generation_data.get("id", "") or "").strip()
        if not generation_id:
            logger.error(f"Voicebox response has no generation id: {generation_data}")
            return None

        audio = requests.get(
            f"{base_url}/audio/{generation_id}",
            timeout=timeout,
        )
        audio.raise_for_status()
        if not audio.content:
            logger.error("Voicebox returned an empty audio file")
            return None

        target_dir = os.path.dirname(voice_file)
        if target_dir:
            os.makedirs(target_dir, exist_ok=True)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio.content)
            temp_audio = tmp.name

        try:
            ffmpeg = utils.get_ffmpeg_binary() or "ffmpeg"
            filters = []
            rate = float(voice_rate or 1.0)
            volume = float(voice_volume or 1.0)
            if abs(rate - 1.0) > 0.001:
                filters.append(f"atempo={max(0.5, min(2.0, rate))}")
            if abs(volume - 1.0) > 0.001:
                filters.append(f"volume={max(0.0, volume)}")

            command = [ffmpeg, "-y", "-i", temp_audio, "-vn"]
            if filters:
                command.extend(["-filter:a", ",".join(filters)])
            command.append(voice_file)
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            if result.returncode != 0:
                logger.error(
                    "Voicebox audio conversion failed: "
                    + result.stderr.decode("utf-8", errors="ignore")
                )
                return None
        finally:
            try:
                os.remove(temp_audio)
            except OSError:
                pass

        return voice_file if os.path.isfile(voice_file) else None
    except Exception as exc:
        logger.error(f"Voicebox TTS failed: {exc}")
        return None
'''

replace_once(
    "/MoneyPrinterTurbo/app/services/voice.py",
    '\ndef get_chatterbox_voices() -> list[str]:',
    voicebox_helpers + '\n\ndef get_chatterbox_voices() -> list[str]:',
)

replace_once(
    "/MoneyPrinterTurbo/app/services/voice.py",
    '    elif is_chatterbox_voice(voice_name):\n',
    '    elif is_voicebox_voice(voice_name):\n'
    '        parts = voice_name.split(":", 2)\n'
    '        if len(parts) >= 2 and parts[1].strip():\n'
    '            return voicebox_tts(\n'
    '                text, parts[1].strip(), voice_file, voice_rate, voice_volume\n'
    '            )\n'
    '        logger.error(f"Invalid Voicebox voice name format: {voice_name}")\n'
    '        return None\n'
    '    elif is_chatterbox_voice(voice_name):\n',
)

# ---------------------------------------------------------------------------
# webui/Main.py
# ---------------------------------------------------------------------------
replace_once(
    "/MoneyPrinterTurbo/webui/Main.py",
    '    "chatterbox": config.chatterbox,\n    "elevenlabs": config.elevenlabs,',
    '    "chatterbox": config.chatterbox,\n    "voicebox": config.voicebox,\n    "elevenlabs": config.elevenlabs,',
)
replace_once(
    "/MoneyPrinterTurbo/webui/Main.py",
    '                ("chatterbox", "Chatterbox TTS"),\n                ("fish_audio", "Fish Audio TTS"),',
    '                ("chatterbox", "Chatterbox TTS"),\n                ("voicebox", "Voicebox TTS"),\n                ("fish_audio", "Fish Audio TTS"),',
)
replace_once(
    "/MoneyPrinterTurbo/webui/Main.py",
    '            elif selected_tts_server == "chatterbox":\n                # 自托管 Chatterbox 服务的预置音色（来自 [chatterbox] voices 配置）\n                _sync_chatterbox_config_from_session_state()\n                filtered_voices = voice.get_chatterbox_voices()\n            elif selected_tts_server == "fish_audio":',
    '            elif selected_tts_server == "chatterbox":\n                # 自托管 Chatterbox 服务的预置音色（来自 [chatterbox] voices 配置）\n                _sync_chatterbox_config_from_session_state()\n                filtered_voices = voice.get_chatterbox_voices()\n            elif selected_tts_server == "voicebox":\n                filtered_voices = voice.get_voicebox_voices()\n            elif selected_tts_server == "fish_audio":',
)
replace_once(
    "/MoneyPrinterTurbo/webui/Main.py",
    '                if voice.is_chatterbox_voice(v):\n                    name = v.split(":", 1)[1] if ":" in v else v\n                    return name.replace("-Female", "").replace("-Male", "")\n                if voice.is_minimax_voice(v):',
    '                if voice.is_chatterbox_voice(v):\n                    name = v.split(":", 1)[1] if ":" in v else v\n                    return name.replace("-Female", "").replace("-Male", "")\n                if voice.is_voicebox_voice(v):\n                    parts = v.split(":", 2)\n                    return parts[2] if len(parts) >= 3 else v\n                if voice.is_minimax_voice(v):',
)

# Add documentation defaults to the example config inside the custom image.
config_example = Path("/MoneyPrinterTurbo/config.example.toml")
example_text = config_example.read_text(encoding="utf-8")
if "[voicebox]" not in example_text:
    example_text += '''\n\n# -----------------------------------------------------------------------------\n# Voicebox (self-hosted TTS)\n# -----------------------------------------------------------------------------\n[voicebox]\nbase_url = "http://srv-captain--voicebox"\nlanguage = "de"\ntimeout = 600\n# Optional overrides. Leave empty to use Voicebox defaults.\nengine = ""\nmodel_size = ""\ninstruct = ""\n'''
    config_example.write_text(example_text, encoding="utf-8")

print("Voicebox integration patch applied successfully")
