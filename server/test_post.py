import requests
import io
import wave

# Create mock wav
wav_io = io.BytesIO()
with wave.open(wav_io, 'wb') as wav_file:
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(16000)
    wav_file.writeframes(b'\x00' * 32000) # 1 sec silent audio
wav_bytes = wav_io.getvalue()

print("Sending POST request to /convert with device_pref=gpu...")
try:
    resp = requests.post(
        "http://127.0.0.1:5000/convert",
        data={'target_format': '.txt', 'device_pref': 'gpu', 'keep_name': 'true'},
        files={'file': ('test.wav', wav_bytes, 'audio/wav')}
    )
    print("Status:", resp.status_code)
    if resp.status_code != 200:
        print("Error Payload:", resp.text)
    else:
        print("Success! Got bytes:", len(resp.content))
except Exception as e:
    print("Request failed:", e)
