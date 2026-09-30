from pathlib import Path
def transcribe_audio(path:str|Path,model_size="small",language=None):
    try:
        from faster_whisper import WhisperModel
    except ImportError as e:
        raise RuntimeError("Para transcrição local opcional, instale faster-whisper.") from e
    model=WhisperModel(model_size,device="auto",compute_type="int8")
    segments,_=model.transcribe(str(path),language=language)
    return "\n".join(s.text.strip() for s in segments)
