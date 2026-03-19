import sys
import traceback

try:
    import torch
    import torch_directml
    import whisper
    import numpy as np

    print("DirectML is available:", torch_directml.is_available())
    device = torch_directml.device()
    print("DirectML device:", device)
    
    print("Loading model...")
    model = whisper.load_model("small", device=device)
    print("Model loaded.")
    
    print("Transcribing...")
    audio = np.zeros(16000, dtype=np.float32)
    model.transcribe(audio, fp16=False, language="zh")
    print("Success")
except Exception as e:
    print("Caught Python exception:")
    print(traceback.format_exc())
