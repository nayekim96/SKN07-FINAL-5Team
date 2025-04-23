# streamlit_audio_monitor.py

import streamlit as st
import numpy as np
import soundfile as sf
import io
import time

st.set_page_config(page_title="🔁 반복 오디오 감지", layout="centered")

st.title("🎙️ 짧은 오디오 반복 녹음 → 음성 감지")

# 설정
THRESHOLD_DB = -50  # 데시벨 기준 (값이 낮을수록 더 민감함)
CYCLE_SECONDS = 5   # 몇 초마다 녹음하는지

st.markdown(f"""
- 녹음 후 볼륨(dB)을 측정하여 **음성이 있는지** 감지합니다.
- `{THRESHOLD_DB} dB` 이상이면 음성이 있다고 판단합니다.
""")

audio_input = st.audio_input("🎤 마이크로 짧게 녹음해 주세요")

def get_rms_db(audio_data):
    rms = np.sqrt(np.mean(np.square(audio_data)))
    if rms > 0:
        db = 20 * np.log10(rms)
    else:
        db = -100.0  # silence
    return db

if audio_input:
    st.audio(audio_input)

    # BytesIO → numpy로 변환
    audio_bytes = audio_input.read()
    data, samplerate = sf.read(io.BytesIO(audio_bytes))

    db = get_rms_db(data)
    st.write(f"📊 측정된 볼륨: `{db:.2f} dB`")

    if db > THRESHOLD_DB:
        st.success("✅ 음성 감지됨!")
    else:
        st.warning("🤫 무음 또는 매우 작은 소리입니다.")

    # rerun을 위해 기록
    if "last_rerun" not in st.session_state:
        st.session_state.last_rerun = time.time()

    # CYCLE_SECONDS 초 후 자동 갱신 (단, 사용자가 계속 올려야 함)
    if time.time() - st.session_state.last_rerun > CYCLE_SECONDS:
        st.session_state.last_rerun = time.time()
        st.experimental_rerun()
else:
    st.info("🔁 5초 간격으로 짧게 녹음해보세요.")
