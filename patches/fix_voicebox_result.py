from pathlib import Path

path = Path("/MoneyPrinterTurbo/app/services/voice.py")
text = path.read_text(encoding="utf-8")
old = '''        return voice_file if os.path.isfile(voice_file) else None
    except Exception as exc:
        logger.error(f"Voicebox TTS failed: {exc}")
        return None
'''
new = '''        if not os.path.isfile(voice_file):
            return None

        audio_clip = AudioFileClip(voice_file)
        try:
            audio_duration = float(audio_clip.duration or 0.0)
        finally:
            audio_clip.close()

        sub_maker = ensure_legacy_submaker_fields(SubMaker())
        logger.success(f"Voicebox TTS succeeded: {voice_file}")
        return populate_legacy_submaker_with_full_text(
            sub_maker=sub_maker,
            text=text,
            audio_duration_seconds=audio_duration,
        )
    except Exception as exc:
        logger.error(f"Voicebox TTS failed: {exc}")
        return None
'''
if old not in text:
    raise RuntimeError("Voicebox result patch marker not found")
path.write_text(text.replace(old, new, 1), encoding="utf-8")
print("Voicebox subtitle result patch applied successfully")
