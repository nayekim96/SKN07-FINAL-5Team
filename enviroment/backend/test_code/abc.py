import streamlit as st
import sounddevice as sd
import numpy as np
import threading
import time

#RMS → dB 계산 함수
def get_rms_db(audio_chunk):
    rms = np.sqrt(np.mean(np.square(audio_chunk)))
    if rms > 0:
        db = 20 * np.log10(rms)
    else:
        db = -100.0  # silence
    return db


#오디오 감지 함수 (백그라운드용)
def monitor_audio_stream(threshold_db, status_placeholder, stop_flag):
    samplerate = 16000
    duration = 0.5  # 0.5초 단위 측정
    channels = 1

    while not stop_flag['stop']:
        audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=channels, dtype='float32')
        sd.wait()

        db = get_rms_db(audio)

        if db > threshold_db:
            status_placeholder.success(f"🎙️ 음성 감지됨! (볼륨: {db:.1f} dB)")
        else:
            status_placeholder.info(f"🤫 조용함 (볼륨: {db:.1f} dB)")

        time.sleep(0.1)

#Streamlit UI
st.title("🎧 실시간 음성 감지 (Volume 기반)")

threshold = st.slider("감지 임계 데시벨 (dB)", -80, -20, -50)
status_placeholder = st.empty()

if "monitoring" not in st.session_state:
    st.session_state.monitoring = False
    st.session_state.stop_flag = {"stop": False}

start = st.button("🎙️ 감지 시작")
stop = st.button("🛑 감지 중지")

if start and not st.session_state.monitoring:
    st.session_state.stop_flag = {"stop": False}
    threading.Thread(
        target=monitor_audio_stream,
        args=(threshold, status_placeholder, st.session_state.stop_flag),
        daemon=True
    ).start()
    st.session_state.monitoring = True
    st.success("마이크 감지를 시작했습니다!")

if stop and st.session_state.monitoring:
    st.session_state.stop_flag['stop'] = True
    st.session_state.monitoring = False
    st.info("감지를 중지했습니다.")