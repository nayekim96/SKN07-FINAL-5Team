import streamlit as st
import time
import cv2
import numpy as np
from PIL import Image
import threading
from streamlit.runtime.scriptrunner import add_script_run_ctx
from audio_recorder_streamlit import audio_recorder
import asyncio
import os
import uuid

root_path = os.path.dirname(os.path.abspath(__file__))
onecycle_second = 90
CAM_FPS = 10
CAM_FRAME_SIZE = (400, 250)

def time_format(seconds):
    return (str(seconds // 60) + ':'  if seconds >= 60 else '' )  + str(seconds % 60)

def countdown_timer(seconds, clock_count):
    st.session_state.timer_running = True
    while seconds > 0:
#    for second in range(seconds, 0 , -1):
        time.sleep(1)
        seconds -= 1
        clock_count += 1
        time_placeholder.title(f':clock{clock_count}: {time_format(seconds)}')
        if clock_count == 12:
            clock_count = 0

    time_placeholder.markdown("""<h2 style="text-align: center">종료</h2>""", unsafe_allow_html=True)
    st.session_state.timer_running = False  # 타이머 종료

def audio_record_start():
    audio_bytes = audio_recorder( icon_size="0px",    # 아이콘 숨김
                                  recording_color="#00000000",  # 완전 투명
                                  neutral_color="#00000000",
                                  icon_name="",
                                  text="",
                                  as_bytes=True)


# 타이머, 오디오 쓰레드 생성
timer_thread = threading.Thread(target=countdown_timer, args=(onecycle_second + 1, 0, ), daemon=True)
audio_thread = threading.Thread(target=audio_record_start, daemon=True)

# 쓰레드 컨텍스트 추가
add_script_run_ctx(timer_thread)  
add_script_run_ctx(audio_thread)


def interview_done(btn_placeholder):
    if btn_placeholder.button('면접 종료'):
        pass

def webcam_save():
    st.error('save start')
    if st.session_state.frame_data and len(st.session_state.frame_data) > 0:
        st.error('if in')
        uid = uuid.uuid1()
        tmp_path = f'{uid.hex}.mp4'
        st.error(f'path:{tmp_path}')
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(tmp_path, fourcc , CAM_FPS, CAM_FRAME_SIZE)
        for _frame in st.session_state.frame_data:
            writer.write(_frame)
        st.error('작업 끝') 
        writer.release()
        st.error('release() 끝')

def get_cv2_writer():
    uid = uuid.uuid1()
    tmp_path = f'../tmp/{uid.hex}.mp4'
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(tmp_path, fourcc , CAM_FPS, CAM_FRAME_SIZE)

    return writer

async def webcam_start(frame_placeholder):
    background_image = Image.open(root_path+"/background_interviewer1.png")
    if background_image is not None and st.session_state.streaming_running == False \
       and st.session_state.interview_done == False:
        # 배경 이미지 로드 및 변환
        # bg_image = Image.open("images/background_interviewer1.png")
        bg_image = np.array(background_image)

        # 웹캠 설정
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FPS, CAM_FPS)  # FPS 속성 설정 (지원하는 경우)
        #frame_placeholder = st.image([])  # 스트리밍을 위한 빈 공간

        # 웹캠 크기 설정
        cam_width, cam_height = CAM_FRAME_SIZE  # 웹캠 크기 조정
        margin_x, margin_y = 30, 30  # 오른쪽 상단 여백
        
        if st.session_state.timer_running == False:
            timer_thread.start()


        st.session_state.streaming_running = True
        # webcam_writer = get_cv2_writer()
        while st.session_state.streaming_running:
            ret, frame = cap.read()
            if not ret:
                st.error("웹캠을 불러올 수 없습니다.")
                break
            
            # 웹캠 크기 조정
            frame = cv2.resize(frame, (cam_width, cam_height))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # BGR → RGB 변환
            #webcam_writer.write(frame)
            st.session_state.frame_data.append(frame)
            # 배경 이미지에 웹캠 영상 오버레이
            overlay_image = bg_image.copy()  # 원본 이미지 복사
            h, w, _ = overlay_image.shape  # 배경 이미지 크기

            # 웹캠을 오른쪽 상단에 위치
            y1, y2 = margin_y, margin_y + cam_height
            x1, x2 = w - margin_x - cam_width, w - margin_x

            # 웹캠 프레임을 배경 위에 배치
            overlay_image[y1:y2, x1:x2] = frame  
            # qa_placeholder.write(st.session_state.qa_text) 
            # 이미지 업데이트
            frame_placeholder.image(overlay_image, use_container_width =True)
            #await time.sleep(0.1)  # 루프 지연 추가
            await asyncio.sleep(0.1)

        cap.release()
    else:
        st.error('테스트!')
        if st.session_state.interview_done:
            st.error("저장시작!")
            webcam_save()
        # webcam_writer.release()
        #cv2.destroyAllWindows()

async def main_loop(frame_placeholder):
    await asyncio.gather(webcam_start(frame_placeholder))

st.set_page_config(layout="wide",
                   initial_sidebar_state="collapsed")

# 타이머 상태 저장
if "timer_running" not in st.session_state:
    st.session_state.timer_running = False

# 스트리밍 상태 저장
if "streaming_running" not in st.session_state:
    st.session_state.streaming_running = False

# 질문 상태 저장 
if "qa_text" not in st.session_state:
    st.session_state.qa_text = ""

# 프레임 저장
if "frame_data" not in st.session_state:
    st.session_state.frame_data = []

# 인터뷰 상태 저장
if "interview_done" not in st.session_state:
    st.session_state.interview_done = False

hide_sidebar = """
    <style>
        .stAppHeader {
            background-color: rgba(255, 255, 255, 0.0);  /* Transparent background */
            visibility: visible;  /* Ensure the header is visible */
        }

        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
            padding-left: 5rem;
            padding-right: 5rem;
        }
        [data-testid="stSidebar"] {
            display: none;
        }
        .st-emotion-cache-l1ktzw e486ovb18 {
            display: none;
        }
        .qa_wrap {
            width: 100%;
            height: 80px;
            border: 1px solid black;
        }
         div[data-testid="stColumn"]:nth-of-type(1)
        {
            border:1px solid yellow;
        } 

        div[data-testid="stColumn"]:nth-of-type(2)
        {
            border:1px solid blue;
            text-align: end;
        }

        div[data-testid="stColumn"]:nth-child(3) {
            text-align:right;
            border: 1px solid red;
        }
    </style>
"""
st.markdown(hide_sidebar, unsafe_allow_html=True)


if __name__ == "__main__":
    time_placeholder = None
    empty1, con1_1, con1_2 ,empty2 = st.columns([0.3,1.5, 1.5, 0.3])
    empty1, con2_1, empty2 = st.columns([0.3,1, 0.3])
    empty1, con3_1 ,empty2 = st.columns([0.3,1.5, 0.3])
    empty1, con4_1 ,empty2 = st.columns([0.3,1 ,0.3])
    frame_placeholder = None 

    with empty1:
        pass

    with con1_1:
        st.markdown(""" <div>
                            <h2> 실전면접 </h2>
                        </div>""", unsafe_allow_html=True)
    
    with con1_2:
        time_placeholder = st.empty()


    with con2_1:
        with st.container(border=True):
            global qa_placeholder
            qa_placeholder = st.empty()

    with con3_1:
        frame_placeholder = st.empty()

    with con4_1:
        if st.button('면접종료'):
            st.session_state.streaming_running = False
            st.session_state.interview_done = True 
            # time.sleep(2)
            st.write('시작했습니다') 
            # st.switch_page('pages/his1.py')

    with empty2:
        pass
    

    asyncio.run(main_loop(frame_placeholder))













