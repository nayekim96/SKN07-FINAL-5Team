import streamlit as st
import numpy as np
import soundfile as sf
import io
import time
import threading

st.set_page_config(page_title="🔁 음성 감지 with 입력 중단 알림", layout="centered")
st.title("🎧 실시간 음성 감지 + 입력 중단 감지")

THRESHOLD_DB = -50
SILENCE_TIMEOUT = 5   # 무음 지속 시간
NO_INPUT_TIMEOUT = 5  # 오디오 자체가 수신되지 않은 시간
CYCLE_SECONDS = 1     # 백그라운드 루프 주기

# 초기 상태값 설정
if "last_voice_time" not in st.session_state:
    st.session_state.last_voice_time = time.time()

if "last_audio_received" not in st.session_state:
    st.session_state.last_audio_received = time.time()

if "alerted_voice" not in st.session_state:
    st.session_state.alerted_voice = False

if "alerted_input" not in st.session_state:
    st.session_state.alerted_input = False

status_placeholder = st.empty()
alert_placeholder = st.empty()

def get_rms_db(audio_data):
    rms = np.sqrt(np.mean(np.square(audio_data)))
    if rms > 0:
        db = 20 * np.log10(rms)
    else:
        db = -100.0
    return db

# 🎯 백그라운드 모니터링 스레드
def audio_volume_monitor():
    while True:
        current_time = time.time()

        # 🎤 오디오가 들어왔는지 확인
        if "latest_audio" in st.session_state:
            try:
                audio_bytes = st.session_state.latest_audio
                data, samplerate = sf.read(io.BytesIO(audio_bytes))
                db = get_rms_db(data)

                # 🔊 음성이 있는 경우
                if db > THRESHOLD_DB:
                    st.session_state.last_voice_time = current_time
                    st.session_state.alerted_voice = False
                    status_placeholder.success(f"🎙️ 음성 감지됨! (볼륨: {db:.1f} dB)")
                    alert_placeholder.empty()

                # 🤫 무음이지만 오디오는 있음
                else:
                    status_placeholder.info(f"🤫 무음 상태 (볼륨: {db:.1f} dB)")

                # 🧭 무음이 지속되면 알림
                if current_time - st.session_state.last_voice_time > SILENCE_TIMEOUT:
                    if not st.session_state.alerted_voice:
                        alert_placeholder.warning("🛑 음성이 입력되지 않고 있습니다!")
                        st.session_state.alerted_voice = True

                # 최신 오디오 수신 시간 초기화
                st.session_state.last_audio_received = current_time
                st.session_state.alerted_input = False

            except Exception as e:
                status_placeholder.error(f"🎧 분석 중 오류 발생: {e}")

        # ❌ 오디오가 완전히 끊긴 경우
        elif current_time - st.session_state.last_audio_received > NO_INPUT_TIMEOUT:
            if not st.session_state.alerted_input:
                alert_placeholder.error("🚫 오디오 입력이 완전히 중단되었습니다!")
                st.session_state.alerted_input = True
                status_placeholder.empty()

        time.sleep(CYCLE_SECONDS)

# 🔁 Streamlit 루프
st.markdown("매 1초마다 음성을 녹음하고, 별도 스레드에서 실시간으로 감지합니다.")

audio_input = st.audio_input("🎤 짧게 녹음해보세요 (1초)", key="recorder")

if audio_input:
    st.audio(audio_input)
    st.session_state.latest_audio = audio_input.read()

# 🔁 백그라운드 스레드 실행 (최초 1회만)
if "monitor_started" not in st.session_state:
    threading.Thread(target=audio_volume_monitor, daemon=True).start()
    st.session_state.monitor_started = True