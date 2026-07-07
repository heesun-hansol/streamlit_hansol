import streamlit as st
from openai import OpenAI
import urllib.parse

st.set_page_config(
    page_title="🎵 AI 노래 추천 서비스",
    page_icon="🎵",
    layout="centered"
)

st.markdown("""
<style>
    .main { background-color: #0e0e1a; }
    .stApp { background-color: #0e0e1a; color: #ffffff; }
    h1, h2, h3 { color: #a78bfa; }
    .song-card {
        background: linear-gradient(135deg, #1e1e3a, #2d2d5a);
        border: 1px solid #a78bfa44;
        border-radius: 12px;
        padding: 16px 20px;
        margin: 10px 0;
        transition: all 0.3s;
    }
    .song-card:hover { border-color: #a78bfa; }
    .youtube-btn {
        display: inline-block;
        background: #ff0000;
        color: white !important;
        text-decoration: none !important;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: bold;
        margin-top: 8px;
    }
    .youtube-btn:hover { background: #cc0000; }
    .reason-text { color: #c4b5fd; font-size: 14px; margin-top: 4px; }
    .stSelectbox label, .stSlider label, .stRadio label { color: #e2e8f0 !important; }
    .api-section {
        background: #1a1a2e;
        border: 1px solid #4c1d95;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎵 AI 노래 추천 서비스")
st.markdown("설문에 답하면 AI가 딱 맞는 노래를 추천해드려요!")

# API Key 입력
with st.expander("🔑 OpenAI API 키 설정", expanded=("openai_api_key" not in st.session_state)):
    st.markdown('<div class="api-section">', unsafe_allow_html=True)
    api_key_input = st.text_input(
        "OpenAI API Key",
        type="password",
        placeholder="sk-...",
        help="OpenAI API 키를 입력하세요. 키는 브라우저 세션에만 저장됩니다."
    )
    if st.button("✅ API 키 저장", use_container_width=True):
        if api_key_input.startswith("sk-"):
            st.session_state["openai_api_key"] = api_key_input
            st.success("API 키가 저장되었습니다!")
            st.rerun()
        else:
            st.error("올바른 API 키를 입력해주세요 (sk- 로 시작)")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# 설문 조사
st.subheader("📋 취향 설문")

col1, col2 = st.columns(2)

with col1:
    mood = st.selectbox(
        "1. 지금 기분이 어때요?",
        ["😊 행복하고 신나는", "😌 차분하고 편안한", "😢 슬프고 감성적인", "💪 힘차고 에너지 넘치는", "🤔 생각이 많은", "💕 설레고 로맨틱한"]
    )

    genre = st.selectbox(
        "2. 선호하는 장르는?",
        ["팝 (Pop)", "K-POP", "R&B / 소울", "록 (Rock)", "힙합 / 랩", "재즈 / 블루스", "클래식 / 어쿠스틱", "EDM / 일렉트로닉", "인디 / 얼터너티브"]
    )

    language = st.selectbox(
        "3. 노래 언어 선호도",
        ["한국어 (K-POP/발라드)", "영어", "둘 다 괜찮아요", "일본어 (J-POP)", "기타 언어도 OK"]
    )

with col2:
    activity = st.selectbox(
        "4. 지금 무엇을 하고 있나요?",
        ["🏃 운동 / 러닝", "📚 공부 / 작업", "🚗 드라이브", "😴 휴식 / 잠들기 전", "🍽️ 식사 중", "🎉 파티 / 모임", "💆 혼자 여유 즐기기"]
    )

    tempo = st.radio(
        "5. 원하는 템포는?",
        ["🐢 느리고 잔잔한", "🐇 빠르고 신나는", "🎯 중간 정도"],
        horizontal=True
    )

    era = st.selectbox(
        "6. 선호하는 시대는?",
        ["최신곡 (2022~현재)", "2010년대", "2000년대", "1990년대", "시대 상관없음"]
    )

era_text = era
num_songs = st.slider("🎼 추천받을 노래 수", min_value=3, max_value=10, value=5)

extra = st.text_area(
    "✏️ 추가로 원하는 분위기나 아티스트가 있다면 자유롭게 적어주세요 (선택)",
    placeholder="예: 아이유 스타일, 드라이브할 때 듣기 좋은 노래, BTS 같은 느낌...",
    height=80
)

st.markdown("---")

# 추천 버튼
if st.button("🎵 노래 추천받기", use_container_width=True, type="primary"):
    if "openai_api_key" not in st.session_state:
        st.error("먼저 OpenAI API 키를 입력해주세요!")
        st.stop()

    prompt = f"""당신은 음악 전문가입니다. 사용자의 취향에 맞는 노래를 추천해주세요.

사용자 정보:
- 현재 기분: {mood}
- 선호 장르: {genre}
- 언어 선호: {language}
- 현재 활동: {activity}
- 원하는 템포: {tempo}
- 선호 시대: {era_text}
- 추가 요청: {extra if extra else "없음"}

위 정보를 바탕으로 노래 {num_songs}곡을 추천해주세요.

반드시 다음 형식으로 정확히 답변하세요. 각 노래는 번호로 구분하고, 아래 형식을 정확히 지켜주세요:

1. 곡명: [곡명]
   아티스트: [아티스트명]
   추천 이유: [2-3문장으로 이 사용자에게 추천하는 이유]

2. 곡명: [곡명]
   아티스트: [아티스트명]
   추천 이유: [2-3문장으로 이 사용자에게 추천하는 이유]

(이하 동일한 형식으로 계속)

실제 존재하는 곡만 추천하고, 아티스트명도 정확하게 기재해주세요."""

    with st.spinner("🎵 AI가 당신만을 위한 노래를 고르고 있어요..."):
        try:
            client = OpenAI(api_key=st.session_state["openai_api_key"])
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "당신은 음악 전문가로, 사용자의 취향에 딱 맞는 노래를 추천해주는 역할을 합니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=2000
            )
            result = response.choices[0].message.content
            st.session_state["recommendations"] = result
        except Exception as e:
            st.error(f"오류가 발생했습니다: {str(e)}")
            st.stop()

# 추천 결과 표시
if "recommendations" in st.session_state:
    st.subheader("🎶 추천 노래 목록")
    st.markdown("노래를 클릭하면 YouTube에서 바로 들을 수 있어요!")

    raw = st.session_state["recommendations"]
    lines = raw.strip().split("\n")

    songs = []
    current = {}
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line and line[0].isdigit() and ". " in line[:4]:
            if current:
                songs.append(current)
            current = {}
            # 숫자. 곡명: ... 형식 처리
            rest = line.split(". ", 1)[-1]
            if rest.startswith("곡명:"):
                current["title"] = rest.replace("곡명:", "").strip()
        elif line.startswith("곡명:"):
            current["title"] = line.replace("곡명:", "").strip()
        elif line.startswith("아티스트:"):
            current["artist"] = line.replace("아티스트:", "").strip()
        elif line.startswith("추천 이유:"):
            current["reason"] = line.replace("추천 이유:", "").strip()
    if current:
        songs.append(current)

    if songs:
        for i, song in enumerate(songs, 1):
            title = song.get("title", "")
            artist = song.get("artist", "")
            reason = song.get("reason", "")

            if not title:
                continue

            query = f"{title} {artist} official"
            yt_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"

            st.markdown(f"""
<div class="song-card">
    <strong style="color:#e2e8f0; font-size:16px;">🎵 {i}. {title}</strong><br>
    <span style="color:#a78bfa;">🎤 {artist}</span><br>
    <p class="reason-text">💬 {reason}</p>
    <a href="{yt_url}" target="_blank" class="youtube-btn">▶ YouTube에서 듣기</a>
</div>
""", unsafe_allow_html=True)
    else:
        st.info("추천 결과를 파싱하는 중 문제가 발생했습니다. 아래 원본 결과를 확인하세요.")
        st.markdown(raw)

    if st.button("🔄 다시 추천받기", use_container_width=True):
        del st.session_state["recommendations"]
        st.rerun()
