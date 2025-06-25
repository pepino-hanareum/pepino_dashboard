import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(page_title="페피노의 게임상자", page_icon="🏱")
st.title("🐰🎀페피노의 게임상자🎀🐰")

# 사이드바 스타일 설정
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Do+Hyeon&display=swap');

    [data-testid="stSidebar"] {
        background-color: #ffeef2;
        width: 300px !important;
    }

    .sidebar-title {
        font-family: 'Do Hyeon', sans-serif;
        font-size: 22px;
        font-weight: bold;
        color: #e75480;
        margin-bottom: 20px;
    }

    section[data-testid="stSidebar"] button {
        background-color: white !important;
        border: 2px solid #FFD700 !important;
        color: black !important;
    }

    section[data-testid="stSidebar"] button:focus:not(:active) {
        border-color: #ff5a36 !important;
        box-shadow: 0 0 0 0.2rem rgba(255, 90, 54, 0.25) !important;
    }
    </style>
""", unsafe_allow_html=True)

# 사이드바 타이틀 마크 추가
st.sidebar.markdown("<div class='sidebar-title'>🩷 페피노의 게임 대시보드</div>", unsafe_allow_html=True)

# 회원 로그인 (간단한 닉네임 입력)
if "nickname" not in st.session_state:
    with st.form("login_form"):
        nickname = st.text_input("닉네임을 입력해주세요")
        submitted = st.form_submit_button("로그인")
        if submitted and nickname:
            st.session_state.nickname = nickname
            st.success(f"{nickname}님 환영합니다 🐰")
    st.stop()
else:
    st.sidebar.markdown(f"🐰 **{st.session_state.nickname}** 님")

# 보기 메뉴 버튼 (사이드바에서 모두 보여주기)
if st.sidebar.button("🧑‍💻 마이페이지"):
    st.session_state.view_option = "마이페이지"

if st.sidebar.button("🏠 전체 게임 보기"):
    st.session_state.view_option = "전체"

# 기본 보기 옵션 설정
if "view_option" not in st.session_state:
    st.session_state.view_option = "전체"

view_option = st.session_state.view_option

# Excel 파일 로드
try:
    df = pd.read_excel("D:/pepino/페피노의 게임상자.xlsx")
except FileNotFoundError:
    st.error("페피노의 게임상자.xlsx 파일이 포함되지 않았어요. 파일을 건너주세요.")
    st.stop()

# 필수 컬럼 확인
required_columns = {'게임 이름', '상태', '카테고리'}
if not required_columns.issubset(df.columns):
    st.error(f"필수 컬럼이 없습니다. 다음 컬럼들이 필요합니다: {required_columns}")
    st.stop()

# 상태 라벨
status_labels = {
    '진행': '⏰ 진행 중인 게임',
    '예정': '🗓️ 진행 예정 게임',
    '유기': '💤 유기한 게임',
    '완료': '✅ 완료한 게임'
}

# 🧺 전체 보기일 때만 요약 블럭 보여주기
if view_option != "마이페이지":
    total_count = len(df)
    status_summary = df['상태'].value_counts().to_dict()
    summary_block = f"🧺 <strong>페피노 게임 개수</strong>: {total_count}개<br>"

    for key in status_labels:
        count = status_summary.get(key, 0)
        summary_block += f"{status_labels[key]}: {count}개<br>"

    st.markdown(
        f"""
        <div style='
            background-color:#fff0f5;
            padding: 15px;
            border-radius: 12px;
            margin-bottom: 20px;
            border: 2px solid #ffc0cb;
            font-size: 16px;
            line-height: 1.8;
        '>
        {summary_block}
        </div>
        """, unsafe_allow_html=True
    )





# 전체 게임 상태 필터 UI (사이드바에 항상 표시)
with st.sidebar.expander("🗃️ 게임 필터", expanded=True):
    status_options = list(status_labels.keys())
    selected_status = st.selectbox("게임 상태", status_options)

    filtered_by_status = df[df['상태'] == selected_status]
    available_categories = sorted(filtered_by_status['카테고리'].dropna().unique())
    selected_category = st.selectbox("카테고리", ["전체"] + available_categories)

# 마이페이지 뷰
if view_option == "마이페이지" and '루핀즈' in df.columns:
    user_gifts = df[df['루핀즈'] == st.session_state.nickname]
    if user_gifts.empty:
        st.info("선물한 게임이 없습니다.")
    else:
        st.subheader("🎁 내가 선물한 게임")
        my_tabs = st.tabs([status_labels[k] for k in status_labels.keys()])

        for i, status in enumerate(status_labels.keys()):
            with my_tabs[i]:
                filtered_gifts = user_gifts[user_gifts['상태'] == status]

                if filtered_gifts.empty:
                    st.info(f"{status_labels[status]}이 없습니다.")
                else:
                    for _, row in filtered_gifts.iterrows():
                        game_title = row["게임 이름"]
                        category = row["카테고리"]
                        description = row["설명"] if "설명" in row and pd.notna(row["설명"]) else ""
                        link = row["링크"] if "링크" in row and pd.notna(row["링크"]) else None

                        with st.container():
                            col1, col2 = st.columns([1, 4])
                            with col1:
                                st.markdown("🎁")
                            with col2:
                                title_display = f"[{game_title}]({link})" if link else game_title
                                st.markdown(f"**{title_display}**  \n`{category}`")
                                if description:
                                    st.markdown(f"<span style='font-size:13px; color:gray'>{description}</span>", unsafe_allow_html=True)
                            st.markdown("---")

        # 전체 선물한 게임 기준 차트
        cat_gift_counts = user_gifts['카테고리'].value_counts().reset_index()
        cat_gift_counts.columns = ['카테고리', '게임 수']
        st.subheader("📈 내가 선물한 게임 카테고리 분포")
        fig2 = px.pie(cat_gift_counts, names='카테고리', values='게임 수', title='내가 선물한 게임 카테고리 비율')
        st.plotly_chart(fig2)

        status_gift_counts = user_gifts['상태'].value_counts().reset_index()
        status_gift_counts.columns = ['상태', '게임 수']
        st.subheader("📊 내가 선물한 게임 상태 분포")
        fig3 = px.bar(status_gift_counts, x='상태', y='게임 수', title='내가 선물한 게임 상태별 개수', color='상태')
        st.plotly_chart(fig3)

# 전체 게임 보기 뷰 (마이페이지가 아닌 경우에만 표시)
if view_option != "마이페이지":
    # 상태 + 카테고리 필터 적용
    if selected_category == "전체":
        filtered = filtered_by_status
    else:
        filtered = filtered_by_status[filtered_by_status['카테고리'] == selected_category]

    # 게임 목록 표시
    st.subheader(f"{status_labels[selected_status]} 목록")

    if filtered.empty:
        st.info("조건에 맞는 게임이 없습니다.")
    else:
        for _, row in filtered.iterrows():
            game_title = row["게임 이름"]
            category = row["카테고리"]
            description = row["설명"] if "설명" in row and pd.notna(row["설명"]) else ""
            link = row["링크"] if "링크" in row and pd.notna(row["링크"]) else None

            with st.container():
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.markdown("🎮")
                with col2:
                    title_display = f"[{game_title}]({link})" if link else game_title
                    st.markdown(f"**{title_display}**  \n`{category}`")
                    if description:
                        st.markdown(f"<span style='font-size:13px; color:gray'>{description}</span>", unsafe_allow_html=True)
                st.markdown("---")

    # 파이차트 (진행 + 예정)
    st.subheader("📊 진행 + 예정 게임 카테고리 비율")

    pie_df = df[df['상태'].isin(['진행', '예정'])]
    if not pie_df.empty:
        cat_counts = pie_df['카테고리'].value_counts().reset_index()
        cat_counts.columns = ['카테고리', '게임 수']
        fig = px.pie(cat_counts, names='카테고리', values='게임 수', title='진행 + 예정 게임 카테고리 비율')
        st.plotly_chart(fig)
    else:
        st.info("진행 중이거나 예정된 게임이 없어 파이차트를 그릴 수 없습니다.")

st.caption("with love, 루핀즈 🐰")