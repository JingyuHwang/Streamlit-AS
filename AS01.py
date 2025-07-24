import pandas as pd
import gspread
import streamlit as st
from google.oauth2.service_account import Credentials
import datetime

# --- 앱 설정 (상수) ---
SERVICE_ACCOUNT_FILE = 'gspread-project-01.json'
SPREADSHEET_NAME = '출석부'
# 초기 사용자 정보 (역할 정의용)
INITIAL_USERS = {
    "곽우영": {"password": "1234", "role": "student"},
    "김규리": {"password": "1234", "role": "student"},
    "김민재": {"password": "1234", "role": "student"},
    "김영준": {"password": "1234", "role": "student"},
    "김유진": {"password": "1234", "role": "student"},
    "김태우": {"password": "1234", "role": "student"},
    "김호현": {"password": "1234", "role": "student"},
    "김홍은": {"password": "1234", "role": "student"},
    "윤준식": {"password": "1234", "role": "student"},
    "윤지원": {"password": "1234", "role": "student"},
    "윤혜영": {"password": "1234", "role": "student"},
    "이다희": {"password": "1234", "role": "student"},
    "이대현": {"password": "1234", "role": "student"},
    "이수빈": {"password": "1234", "role": "student"},
    "이승은": {"password": "1234", "role": "student"},
    "이우영": {"password": "1234", "role": "student"},
    "이은서": {"password": "1234", "role": "student"},
    "이인규": {"password": "1234", "role": "student"},
    "임정자": {"password": "1234", "role": "student"},
    "정사랑": {"password": "1234", "role": "student"},
    "정주원": {"password": "1234", "role": "student"},
    "구태연": {"password": "1234", "role": "student"},
    "김동현": {"password": "1234", "role": "student"},
    "김아람": {"password": "1234", "role": "student"},
    "김영지": {"password": "1234", "role": "student"},
    "민동일": {"password": "1234", "role": "student"},
    "박광훈": {"password": "1234", "role": "student"},
    "박민지": {"password": "1234", "role": "student"},
    "방지현": {"password": "1234", "role": "student"},
    "안희빈": {"password": "1234", "role": "student"},
    "이승연": {"password": "1234", "role": "student"},
    "이진우": {"password": "1234", "role": "student"},
    "이태빈": {"password": "1234", "role": "student"},
    "이혜민": {"password": "1234", "role": "student"},
    "임정우": {"password": "1234", "role": "student"},
    "장성현": {"password": "1234", "role": "student"},
    "정용훈": {"password": "1234", "role": "student"},
    "하영현": {"password": "1234", "role": "student"},
    "이상윤": {"password": "1234", "role": "student"},
    "고준호": {"password": "1234", "role": "student"},
    "윤병창": {"password": "1234", "role": "student"},
    "관리자": {"password": "adminpw", "role": "admin"}
}

# --- 데이터 처리 함수 ---
@st.cache_data(ttl=600)
def load_data(sheet_name):
    """구글 시트에서 원본 데이터를 불러옵니다."""
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        
        # st.secrets에서 서비스 계정 정보를 직접 가져옵니다.
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],  # "gcp_service_account"는 secrets.toml 파일의 key와 일치해야 합니다.
            scopes=scopes
        )
        
        client = gspread.authorize(creds)
        spreadsheet = client.open(sheet_name)
        worksheet = spreadsheet.worksheet("출석")
        records = worksheet.get_all_records()
        raw_df = pd.DataFrame(records)

        if raw_df.empty:
            return pd.DataFrame()

        # '타임스탬프' 열을 날짜 객체로 변환하여 '날짜' 열 추가
        if '타임스탬프' in raw_df.columns:
            timestamps_english = raw_df['타임스탬프'].str.replace('오전', 'AM', regex=False)
            timestamps_english = timestamps_english.str.replace('오후', 'PM', regex=False)
            date_format = '%Y. %m. %d %p %I:%M:%S'
            raw_df['날짜'] = pd.to_datetime(timestamps_english, format=date_format, errors='coerce').dt.date

        # '성함' 열의 양쪽 공백을 제거하여 데이터 정제
        if '성함' in raw_df.columns:
            raw_df['성함'] = raw_df['성함'].astype(str).str.strip()

        return raw_df
    except Exception as e:
        st.error(f"데이터 로딩 중 오류 발생: {e}")
        return pd.DataFrame()

# --- UI 페이지 함수들 ---

def login_page():
    """로그인 UI를 표시합니다."""
    st.subheader("로그인")
    username = st.text_input("이름").strip()
    password = st.text_input("비밀번호", type="password")
    if st.button("로그인"):
        user_info = st.session_state.users.get(username)
        if user_info and user_info["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = user_info["role"]
            st.rerun()
        else:
            st.error("이름 또는 비밀번호가 올바르지 않습니다.")

def change_password_student(username):
    """학생용 비밀번호 변경 UI 및 로직"""
    with st.expander("비밀번호 변경"):
        with st.form("change_password_form", clear_on_submit=True):
            current_password = st.text_input("현재 비밀번호", type="password")
            new_password = st.text_input("새 비밀번호", type="password")
            confirm_password = st.text_input("새 비밀번호 확인", type="password")
            submitted = st.form_submit_button("변경하기")

            if submitted:
                user_info = st.session_state.users.get(username)
                if user_info["password"] != current_password:
                    st.error("현재 비밀번호가 일치하지 않습니다.")
                elif new_password != confirm_password:
                    st.error("새 비밀번호가 일치하지 않습니다.")
                elif len(new_password) < 4:
                    st.error("비밀번호는 4자 이상이어야 합니다.")
                else:
                    st.session_state.users[username]["password"] = new_password
                    st.success("비밀번호가 성공적으로 변경되었습니다.")

def create_user_admin():
    """관리자용 신규 수강생 계정 생성 UI 및 로직"""
    with st.expander("신규 수강생 계정 생성"):
        with st.form("create_user_form", clear_on_submit=True):
            new_username = st.text_input("새 수강생 이름")
            new_password = st.text_input("초기 비밀번호", type="password")
            submitted = st.form_submit_button("계정 생성")

            if submitted:
                if not new_username:
                    st.error("이름을 입력해주세요.")
                elif new_username in st.session_state.users:
                    st.error(f"이미 존재하는 이름입니다: {new_username}")
                elif len(new_password) < 4:
                    st.error("비밀번호는 4자 이상이어야 합니다.")
                else:
                    st.session_state.users[new_username] = {"password": new_password, "role": "student"}
                    st.success(f"'{new_username}'님의 계정이 생성되었습니다.")

def rename_user_admin():
    """관리자용 수강생 이름 변경 UI 및 로직"""
    with st.expander("수강생 이름 변경"):
        student_list = [name for name, info in st.session_state.users.items() if info["role"] == "student"]
        if not student_list:
            st.info("이름을 변경할 수강생이 없습니다.")
            return

        selected_student = st.selectbox("이름을 변경할 수강생 선택", student_list, key="rename_select")

        with st.form("rename_user_form"):
            new_name = st.text_input("새 이름", value=selected_student)
            submitted = st.form_submit_button("이름 변경하기")

            if submitted:
                if not new_name:
                    st.error("새 이름을 입력해주세요.")
                elif new_name in st.session_state.users:
                    st.error(f"이미 존재하는 이름입니다: {new_name}")
                else:
                    user_data = st.session_state.users.pop(selected_student)
                    st.session_state.users[new_name] = user_data
                    st.success(f"'{selected_student}'님의 이름이 '{new_name}'(으)로 변경되었습니다.")
                    st.warning("계정 이름 변경은 현재 세션에만 적용됩니다. 출결 데이터의 '이름'은 변경되지 않습니다.")
                    st.rerun()

def reset_password_admin():
    """관리자용 비밀번호 초기화 UI 및 로직"""
    with st.expander("수강생 비밀번호 초기화"):
        student_list = [name for name, info in st.session_state.users.items() if info["role"] == "student"]
        if not student_list:
            st.info("비밀번호를 초기화할 수강생이 없습니다.")
            return

        selected_student = st.selectbox("비밀번호를 초기화할 수강생 선택", student_list, key="reset_select")

        with st.form("reset_password_form"):
            new_password = st.text_input(f"'{selected_student}'의 새 비밀번호", type="password")
            submitted = st.form_submit_button("초기화하기")

            if submitted:
                if len(new_password) < 4:
                    st.error("비밀번호는 4자 이상이어야 합니다.")
                else:
                    st.session_state.users[selected_student]["password"] = new_password
                    st.success(f"'{selected_student}'님의 비밀번호가 초기화되었습니다.")

def edit_title_admin():
    """관리자용 앱 제목 변경 UI 및 로직"""
    with st.expander("앱 제목 변경"):
        with st.form("edit_title_form"):
            new_title = st.text_input("새 앱 제목", value=st.session_state.app_title)
            submitted = st.form_submit_button("제목 변경")
            if submitted:
                st.session_state.app_title = new_title
                st.success("앱 제목이 변경되었습니다.")
                st.rerun()

def show_student_page(raw_df, username, selected_date):
    """학생 페이지를 표시합니다."""
    st.subheader(f"🙋 {username}님, 안녕하세요!")

    # --- 데이터 새로고침 버튼 ---
    if st.button("🔄 데이터 새로고침"):
        st.cache_data.clear()
        st.rerun()

    st.divider()

    # --- 선택된 날짜의 출결 기록 ---
    st.subheader(f"📅 {selected_date} 출결 기록")

    # 이름과 날짜로 데이터 필터링
    student_dated_data = raw_df[(raw_df['성함'] == username) & (raw_df['날짜'] == selected_date)]

    if student_dated_data.empty:
        st.info("해당 날짜의 출결 기록이 없습니다.")
    else:
        st.dataframe(student_dated_data, use_container_width=True, hide_index=True)

    st.divider()

    # --- 부가 기능 ---
    with st.expander("나의 전체 출결 기록 보기"):
        student_all_data = raw_df[raw_df['성함'] == username]
        if student_all_data.empty:
            st.info("기록된 출결 데이터가 없습니다.")
        else:
            st.dataframe(student_all_data, use_container_width=True, hide_index=True)

    change_password_student(username)


def show_admin_page(raw_df, selected_date):
    """관리자 페이지를 표시합니다."""
    st.subheader("👨‍💼 관리자 모드")

    # --- 데이터 새로고침 버튼 ---
    if st.button("🔄 데이터 새로고침"):
        st.cache_data.clear()
        st.rerun()

    st.divider()

    # --- 선택된 날짜의 출결 현황 ---
    st.subheader(f"📅 {selected_date} 전체 출결 현황")
    dated_df = raw_df[raw_df['날짜'] == selected_date]
    if dated_df.empty:
        st.info("해당 날짜에 기록된 데이터가 없습니다.")
    else:
        st.dataframe(dated_df, use_container_width=True, hide_index=True)
    st.divider()

    # --- 수강생별 원본 데이터 조회 기능 ---
    st.subheader("📋 수강생별 출결 기록 (원본)")
    student_list = sorted([name for name, info in st.session_state.users.items() if info["role"] == "student"])
    
    if not student_list:
        st.info("등록된 수강생이 없습니다.")
    else:
        selected_student = st.selectbox("조회할 수강생 선택", student_list)
        
        if selected_student:
            student_raw_data = raw_df[raw_df['성함'] == selected_student]
            
            if student_raw_data.empty:
                st.warning(f"'{selected_student}'님의 출결 기록이 없습니다.")
            else:
                st.dataframe(student_raw_data, use_container_width=True, hide_index=True)
    
    st.divider()

    # --- 전체 데이터 및 관리 기능 ---
    with st.expander("전체 원본 데이터 보기"):
        st.dataframe(raw_df, use_container_width=True, hide_index=True)

    edit_title_admin()
    create_user_admin()
    rename_user_admin()
    reset_password_admin()


def main():
    # 세션 상태 초기화
    if "users" not in st.session_state:
        st.session_state.users = INITIAL_USERS.copy()
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "app_title" not in st.session_state:
        st.session_state.app_title = "📊 전자 출석부"

    st.set_page_config(layout="wide")
    st.title(st.session_state.app_title)

    if not st.session_state.logged_in:
        login_page()
    else:
        # --- 사이드바 ---
        with st.sidebar:
            st.write(f"**{st.session_state.username}** ({st.session_state.role})")

            # 날짜 선택 기능
            st.divider()
            selected_date = st.date_input("조회할 날짜 선택", datetime.date.today())
            st.divider()

            if st.button("로그아웃"):
                # 로그아웃 시 필요한 정보만 남기고 세션 정리
                for key in list(st.session_state.keys()):
                    if key not in ['users', 'app_title']:
                        del st.session_state[key]
                st.session_state.logged_in = False
                st.rerun()

        # --- 메인 페이지 ---
        raw_df = load_data(SPREADSHEET_NAME)

        # '성함' 열 존재 여부 확인 후 로직 수행
        if raw_df is not None and '성함' in raw_df.columns:
            # 역할에 따라 페이지 표시
            if st.session_state.role == "admin":
                show_admin_page(raw_df, selected_date)
            else:
                show_student_page(raw_df, st.session_state.username, selected_date)
        else:
            # 데이터 로드 실패 또는 '성함' 열이 없는 경우 에러 메시지 표시
            st.error("출석부 데이터를 불러오지 못했거나 '성함' 열이 없습니다.")
            # 데이터 로드 실패 시에도 새로고침 버튼을 표시하여 재시도 유도
            if st.button("🔄 데이터 다시 불러오기"):
                st.cache_data.clear()
                st.rerun()


if __name__ == "__main__":
    main()
