import traceback
import sys

try:
    import torch_directml
    import whisper
    import numpy as np

    print("Loading model on DirectML...")
    device = torch_directml.device()
    model = whisper.load_model('small', device=device)
    print("Model loaded successfully.")

    print("Attempting to transcribe a dummy audio...")
    # Create a dummy audio waveform (1 second of silence at 16000 Hz)
    audio = np.zeros(16000, dtype=np.float32)

    result = model.transcribe(audio, fp16=False, language="zh")
    print("Transcription successful!")
except Exception as e:
    print("Exception occurred:")
    print(traceback.format_exc())
