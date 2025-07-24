import pandas as pd
import gspread
import streamlit as st
from google.oauth2.service_account import Credentials
import datetime
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter

# --- 페이지 설정 ---
st.set_page_config(
    page_title="전자 출석부",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS 스타일링 ---
st.markdown("""
<style>
    /* 전체 레이아웃 */
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    /* 카드 스타일 */
    .info-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    
    .success-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .stat-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-top: 3px solid #667eea;
    }
    
    /* 로그인 폼 */
    .login-container {
        max-width: 400px;
        margin: 2rem auto;
        padding: 2rem;
        background: white;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    /* 버튼 스타일 */
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* 사이드바 스타일 */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* 데이터프레임 스타일 */
    .dataframe {
        border: none !important;
    }
    
    .dataframe th {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        font-weight: 600 !important;
    }
    
    /* 메트릭 카드 */
    .metric-container {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        text-align: center;
        margin-bottom: 1rem;
    }
    
    /* 알림 스타일 */
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    
    .info-message {
        background: #d1ecf1;
        color: #0c5460;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #17a2b8;
        margin: 1rem 0;
    }
    
    .warning-message {
        background: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

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

# --- 유틸리티 함수 ---
def show_success_message(message):
    st.markdown(f'<div class="success-message">✅ {message}</div>', unsafe_allow_html=True)

def show_info_message(message):
    st.markdown(f'<div class="info-message">ℹ️ {message}</div>', unsafe_allow_html=True)

def show_warning_message(message):
    st.markdown(f'<div class="warning-message">⚠️ {message}</div>', unsafe_allow_html=True)

def create_metric_card(title, value, delta=None):
    delta_html = f'<p style="color: green; margin: 0; font-size: 0.9rem;">📈 {delta}</p>' if delta else ''
    return f"""
    <div class="metric-container">
        <h3 style="margin: 0; color: #667eea;">{value}</h3>
        <p style="margin: 0.5rem 0; color: #666;">{title}</p>
        {delta_html}
    </div>
    """

# --- 데이터 처리 함수 ---
@st.cache_data(ttl=600)
def load_data(sheet_name):
    """구글 시트에서 원본 데이터를 불러옵니다."""
    try:
        with st.spinner('📊 데이터를 불러오는 중...'):
            scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
            
            creds = Credentials.from_service_account_info(
                st.secrets["gcp_service_account"],
                scopes=scopes
            )
            
            client = gspread.authorize(creds)
            worksheet = client.open(sheet_name).sheet1
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
        st.error(f"❌ 데이터 로딩 중 오류 발생: {e}")
        return pd.DataFrame()

def get_attendance_stats(df, username=None):
    """출석 통계를 계산합니다."""
    if username:
        df = df[df['성함'] == username]
    
    total_days = len(df['날짜'].unique()) if not df.empty else 0
    total_records = len(df)
    
    # 최근 7일 출석률
    recent_dates = df['날짜'].unique()
    if len(recent_dates) > 0:
        recent_7_days = sorted(recent_dates)[-7:]
        recent_records = len(df[df['날짜'].isin(recent_7_days)])
        recent_rate = (recent_records / len(recent_7_days)) * 100 if recent_7_days else 0
    else:
        recent_rate = 0
    
    return {
        'total_days': total_days,
        'total_records': total_records,
        'recent_rate': recent_rate
    }

# --- UI 페이지 함수들 ---
def show_app_header():
    """앱 헤더를 표시합니다."""
    st.markdown(f"""
    <div class="main-header">
        <h1>{st.session_state.app_title}</h1>
        <p>📅 {datetime.date.today().strftime('%Y년 %m월 %d일')} | 스마트 출석 관리 시스템</p>
    </div>
    """, unsafe_allow_html=True)

def login_page():
    """개선된 로그인 UI를 표시합니다."""
    show_app_header()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        st.markdown("### 🔐 로그인")
        st.markdown("---")
        
        with st.form("login_form"):
            username = st.text_input(
                "👤 이름", 
                placeholder="이름을 입력하세요",
                help="등록된 이름을 정확히 입력해주세요"
            ).strip()
            
            password = st.text_input(
                "🔑 비밀번호", 
                type="password",
                placeholder="비밀번호를 입력하세요"
            )
            
            col_login, col_help = st.columns([2, 1])
            
            with col_login:
                login_submitted = st.form_submit_button("🚀 로그인", use_container_width=True)
            
            with col_help:
                if st.form_submit_button("❓ 도움말"):
                    st.info("👨‍🎓 학생: 등록된 이름과 비밀번호로 로그인\n👨‍💼 관리자: '관리자' / 'adminpw'")
        
        if login_submitted:
            user_info = st.session_state.users.get(username)
            if user_info and user_info["password"] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = user_info["role"]
                show_success_message(f"환영합니다, {username}님!")
                st.balloons()
                st.rerun()
            else:
                st.error("❌ 이름 또는 비밀번호가 올바르지 않습니다.")
                st.info("💡 입력한 정보를 다시 확인해주세요.")
        
        st.markdown('</div>', unsafe_allow_html=True)

def show_sidebar():
    """개선된 사이드바를 표시합니다."""
    with st.sidebar:
        # 사용자 정보 카드
        st.markdown(f"""
        <div class="success-card">
            <h3>👋 안녕하세요!</h3>
            <h2>{st.session_state.username}</h2>
            <p>{'🛡️ 관리자' if st.session_state.role == 'admin' else '👨‍🎓 학생'}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # 날짜 선택
        st.markdown("### 📅 날짜 선택")
        selected_date = st.date_input(
            "조회할 날짜",
            datetime.date.today(),
            help="출석 기록을 확인할 날짜를 선택하세요"
        )

        st.markdown("---")

        # 빠른 액션 버튼들
        st.markdown("### ⚡ 빠른 실행")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 새로고침", use_container_width=True):
                st.cache_data.clear()
                st.rerun()
        
        with col2:
            if st.button("📊 통계", use_container_width=True):
                st.session_state.show_stats = not st.session_state.get('show_stats', False)

        st.markdown("---")

        # 로그아웃 버튼
        if st.button("🚪 로그아웃", use_container_width=True, type="secondary"):
            for key in list(st.session_state.keys()):
                if key not in ['users', 'app_title']:
                    del st.session_state[key]
            st.session_state.logged_in = False
            st.rerun()

        return selected_date

def change_password_student(username):
    """개선된 학생용 비밀번호 변경 UI"""
    with st.expander("🔒 비밀번호 변경", expanded=False):
        st.markdown("비밀번호를 안전하게 변경하세요.")
        
        with st.form("change_password_form", clear_on_submit=True):
            current_password = st.text_input("현재 비밀번호", type="password")
            new_password = st.text_input("새 비밀번호", type="password")
            confirm_password = st.text_input("새 비밀번호 확인", type="password")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                submitted = st.form_submit_button("✅ 변경하기", use_container_width=True)
            with col2:
                st.form_submit_button("❌ 취소", use_container_width=True)

            if submitted:
                user_info = st.session_state.users.get(username)
                if user_info["password"] != current_password:
                    st.error("❌ 현재 비밀번호가 일치하지 않습니다.")
                elif new_password != confirm_password:
                    st.error("❌ 새 비밀번호가 일치하지 않습니다.")
                elif len(new_password) < 4:
                    st.error("❌ 비밀번호는 4자 이상이어야 합니다.")
                else:
                    st.session_state.users[username]["password"] = new_password
                    show_success_message("비밀번호가 성공적으로 변경되었습니다!")

def show_attendance_chart(df, username=None):
    """출석 현황 차트를 표시합니다."""
    if df.empty:
        return
    
    # 날짜별 출석 현황
    if username:
        chart_data = df[df['성함'] == username]
        title = f"{username}님의 출석 현황"
    else:
        chart_data = df
        title = "전체 출석 현황"
    
    if not chart_data.empty:
        daily_counts = chart_data.groupby('날짜').size().reset_index(name='출석수')
        
        fig = px.line(
            daily_counts, 
            x='날짜', 
            y='출석수',
            title=title,
            markers=True
        )
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Arial, sans-serif")
        )
        fig.update_traces(line_color='#667eea', marker_color='#764ba2')
        
        st.plotly_chart(fig, use_container_width=True)

def show_student_page(raw_df, username, selected_date):
    """개선된 학생 페이지를 표시합니다."""
    
    # 통계 정보
    stats = get_attendance_stats(raw_df, username)
    
    # 메트릭 카드들
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(create_metric_card("총 출석일", f"{stats['total_days']}일"), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_metric_card("총 출석 기록", f"{stats['total_records']}회"), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_metric_card("최근 출석률", f"{stats['recent_rate']:.1f}%"), unsafe_allow_html=True)

    st.markdown("---")

    # 선택된 날짜의 출결 기록
    st.markdown(f"### 📋 {selected_date.strftime('%Y년 %m월 %d일')} 출석 기록")

    student_dated_data = raw_df[(raw_df['성함'] == username) & (raw_df['날짜'] == selected_date)]

    if student_dated_data.empty:
        show_info_message("해당 날짜의 출석 기록이 없습니다.")
    else:
        st.dataframe(
            student_dated_data, 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "타임스탬프": st.column_config.DatetimeColumn("출석 시간"),
                "성함": st.column_config.TextColumn("이름"),
            }
        )

    # 차트 표시 (통계 토글이 활성화된 경우)
    if st.session_state.get('show_stats', False):
        st.markdown("---")
        st.markdown("### 📊 나의 출석 통계")
        show_attendance_chart(raw_df, username)

    st.markdown("---")

    # 부가 기능들
    tab1, tab2 = st.tabs(["📚 전체 기록", "⚙️ 설정"])
    
    with tab1:
        student_all_data = raw_df[raw_df['성함'] == username]
        if student_all_data.empty:
            show_info_message("기록된 출석 데이터가 없습니다.")
        else:
            st.dataframe(student_all_data, use_container_width=True, hide_index=True)
    
    with tab2:
        change_password_student(username)

def create_user_admin():
    """개선된 관리자용 신규 수강생 계정 생성 UI"""
    with st.expander("👥 신규 수강생 계정 생성", expanded=False):
        st.markdown("새로운 수강생 계정을 생성합니다.")
        
        with st.form("create_user_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                new_username = st.text_input("👤 새 수강생 이름", placeholder="이름을 입력하세요")
            
            with col2:
                new_password = st.text_input("🔑 초기 비밀번호", type="password", placeholder="4자 이상")
            
            submitted = st.form_submit_button("✅ 계정 생성", use_container_width=True)

            if submitted:
                if not new_username:
                    st.error("❌ 이름을 입력해주세요.")
                elif new_username in st.session_state.users:
                    st.error(f"❌ 이미 존재하는 이름입니다: {new_username}")
                elif len(new_password) < 4:
                    st.error("❌ 비밀번호는 4자 이상이어야 합니다.")
                else:
                    st.session_state.users[new_username] = {"password": new_password, "role": "student"}
                    show_success_message(f"'{new_username}'님의 계정이 생성되었습니다!")

def rename_user_admin():
    """개선된 관리자용 수강생 이름 변경 UI"""
    with st.expander("✏️ 수강생 이름 변경", expanded=False):
        student_list = [name for name, info in st.session_state.users.items() if info["role"] == "student"]
        
        if not student_list:
            show_info_message("이름을 변경할 수강생이 없습니다.")
            return

        with st.form("rename_user_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                selected_student = st.selectbox("👤 수강생 선택", student_list)
            
            with col2:
                new_name = st.text_input("📝 새 이름", value=selected_student)
            
            submitted = st.form_submit_button("✅ 이름 변경", use_container_width=True)

            if submitted:
                if not new_name:
                    st.error("❌ 새 이름을 입력해주세요.")
                elif new_name in st.session_state.users:
                    st.error(f"❌ 이미 존재하는 이름입니다: {new_name}")
                else:
                    user_data = st.session_state.users.pop(selected_student)
                    st.session_state.users[new_name] = user_data
                    show_success_message(f"'{selected_student}'님의 이름이 '{new_name}'으로 변경되었습니다!")
                    show_warning_message("계정 이름 변경은 현재 세션에만 적용됩니다.")
                    st.rerun()

def reset_password_admin():
    """개선된 관리자용 비밀번호 초기화 UI"""
    with st.expander("🔓 비밀번호 초기화", expanded=False):
        student_list = [name for name, info in st.session_state.users.items() if info["role"] == "student"]
        
        if not student_list:
            show_info_message("비밀번호를 초기화할 수강생이 없습니다.")
            return

        with st.form("reset_password_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                selected_student = st.selectbox("👤 수강생 선택", student_list)
            
            with col2:
                new_password = st.text_input("🔑 새 비밀번호", type="password", placeholder="4자 이상")
            
            submitted = st.form_submit_button("✅ 비밀번호 초기화", use_container_width=True)

            if submitted:
                if len(new_password) < 4:
                    st.error("❌ 비밀번호는 4자 이상이어야 합니다.")
                else:
                    st.session_state.users[selected_student]["password"] = new_password
                    show_success_message(f"'{selected_student}'님의 비밀번호가 초기화되었습니다!")

def edit_title_admin():
    """개선된 관리자용 앱 제목 변경 UI"""
    with st.expander("📝 앱 제목 변경", expanded=False):
        with st.form("edit_title_form"):
            new_title = st.text_input("📊 새 앱 제목", value=st.session_state.app_title)
            submitted = st.form_submit_button("✅ 제목 변경", use_container_width=True)
            
            if submitted:
                st.session_state.app_title = new_title
                show_success_message("앱 제목이 변경되었습니다!")
                st.rerun()

def show_admin_page(raw_df, selected_date):
    """개선된 관리자 페이지를 표시합니다."""
    
    # 전체 통계
    stats = get_attendance_stats(raw_df)
    
    # 메트릭 카드들
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_metric_card("총 수강생", f"{len([u for u, i in st.session_state.users.items() if i['role'] == 'student'])}명"), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_metric_card("총 출석일", f"{stats['total_days']}일"), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_metric_card("총 출석 기록", f"{stats['total_records']}회"), unsafe_allow_html=True)
    
    with col4:
        today_records = len(raw_df[raw_df['날짜'] == datetime.date.today()])
        st.markdown(create_metric_card("오늘 출석", f"{today_records}회"), unsafe_allow_html=True)

    st.markdown("---")

    # 선택된 날짜의 출결 현황
    st.markdown(f"### 📋 {selected_date.strftime('%Y년 %m월 %d일')} 전체 출석 현황")
    
    dated_df = raw_df[raw_df['날짜'] == selected_date]
    if dated_df.empty:
        show_info_message("해당 날짜에 기록된 데이터가 없습니다.")
    else:
        # 출석 현황 요약
        attendance_summary = dated_df.groupby('성함').size().reset_index(name='출석횟수')
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.dataframe(dated_df, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("#### 📊 출석 요약")
            st.dataframe(attendance_summary, use_container_width=True, hide_index=True)

    # 차트 표시
    if st.session_state.get('show_stats', False):
        st.markdown("---")
        st.markdown("### 📊 출석 통계 차트")
        show_attendance_chart(raw_df)

    st.markdown("---")

    # 탭으로 구성된 기능들
    tab1, tab2, tab3 = st.tabs(["👥 수강생 관리", "📊 상세 데이터", "⚙️ 시스템 설정"])
    
    with tab1:
        # 수강생별 데이터 조회
        st.markdown("#### 👨‍🎓 수강생별 출석 기록")
        student_list = sorted([name for name, info in st.session_state.users.items() if info["role"] == "student"])
        
        if student_list:
            selected_student = st.selectbox("🔍 조회할 수강생 선택", ["전체"] + student_list)
            
            if selected_student == "전체":
                display_df = raw_df
            else:
                display_df = raw_df[raw_df['성함'] == selected_student]
            
            if display_df.empty:
                show_warning_message(f"'{selected_student}'의 출석 기록이 없습니다.")
            else:
                st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
            show_info_message("등록된 수강생이 없습니다.")
    
    with tab2:
        st.markdown("#### 📋 전체 원본 데이터")
        if not raw_df.empty:
            st.dataframe(raw_df, use_container_width=True, hide_index=True)
            
            # 데이터 다운로드 버튼
            csv = raw_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 CSV 다운로드",
                data=csv,
                file_name=f'출석부_{datetime.date.today()}.csv',
                mime='text/csv'
            )
        else:
            show_info_message("표시할 데이터가 없습니다.")
    
    with tab3:
        st.markdown("#### ⚙️ 시스템 관리")
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
        st.session_state.app_title = "📊 스마트 전자 출석부"
    if "show_stats" not in st.session_state:
        st.session_state.show_stats = False

    if not st.session_state.logged_in:
        login_page()
    else:
        show_app_header()
        
        # 사이드바
        selected_date = show_sidebar()

        # 메인 페이지
        raw_df = load_data(SPREADSHEET_NAME)

        if raw_df is not None and '성함' in raw_df.columns:
            if st.session_state.role == "admin":
                show_admin_page(raw_df, selected_date)
            else:
                show_student_page(raw_df, st.session_state.username, selected_date)
        else:
            st.error("❌ 출석부 데이터를 불러오지 못했거나 '성함' 열이 없습니다.")
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("🔄 데이터 다시 불러오기", use_container_width=True):
                    st.cache_data.clear()
                    st.rerun()

if __name__ == "__main__":
    main()
