import sounddevice as sd
from scipy.io.wavfile import write

# 설정
samplerate = 16000  # CD 품질
duration = 90       # 녹음 길이 (초)
filename = "./data/recorded_audio.wav"

print("녹음 시작...")
recording = sd.rec(int(samplerate * duration), samplerate=samplerate, channels=1, dtype='int16')
sd.wait()  # 녹음이 끝날 때까지 대기
write(filename, samplerate, recording)
print(f"녹음 완료, {filename}에 저장됨.")
