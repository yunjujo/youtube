import streamlit as st
from googleapiclient.discovery import build
import pandas as pd
from datetime import datetime
import isodate

# 1. API 키 설정 (Streamlit Secrets에서 호출)
# Secrets 설정법: 관리자 페이지 -> Settings -> Secrets에 아래 형식으로 입력
# YOUTUBE_API_KEY = "내_API_키_값"
try:
    API_KEY = st.secrets["YOUTUBE_API_KEY"]
except KeyError:
    st.error("Secrets에 'YOUTUBE_API_KEY'가 설정되지 않았습니다.")
    st.stop()

# 2. 유투브 API 빌드
youtube = build("youtube", "v3", developerKey=API_KEY)

def get_video_id(url):
    """유튜브 URL에서 비디오 ID 추출"""
    if "youtu.be/" in url:
        return url.split("/")[-1]
    elif "v=" in url:
        return url.split("v=")[1].split("&")[0]
    return None

# --- UI 레이아웃 ---
st.set_page_config(page_title="YouTube 마스터 분석기", layout="wide")

st.title("🚀 YouTube 영상 데이터 요약기")
st.markdown("URL을 입력하면 영상의 상세 정보와 통계를 한눈에 정리해 드립니다.")

video_url = st.text_input("분석할 유튜브 영상 URL을 입력하세요", placeholder="https://www.youtube.com/watch?v=...")

if video_url:
    video_id = get_video_id(video_url)
    
    if video_id:
        try:
            # API 호출
            response = youtube.videos().list(
                part="snippet,statistics,contentDetails",
                id=video_id
            ).execute()

            if response['items']:
                data = response['items'][0]
                snippet = data['snippet']
                stats = data['statistics']
                
                # 데이터 가공
                title = snippet['title']
                channel = snippet['channelTitle']
                published_at = datetime.strptime(snippet['publishedAt'], "%Y-%m-%dT%H:%M:%SZ")
                views = int(stats.get('viewCount', 0))
                comments = int(stats.get('commentCount', 0))
                likes = int(stats.get('likeCount', 0))
                thumbnail_url = snippet['thumbnails']['high']['url']

                # --- 결과 출력 ---
                st.divider()
                
                # 상단: 썸네일과 주요 지표
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.subheader("🖼️ 썸네일")
                    st.image(thumbnail_url, use_container_width=True)
                    st.markdown(f"**[🔗 썸네일 원본 보기 및 다운로드]({thumbnail_url})**")

                with col2:
                    st.subheader("📊 핵심 데이터 (한눈에 보기)")
                    m1, m2 = st.columns(2)
                    m1.metric("총 조회 수", f"{views:,}회")
                    m2.metric("총 댓글 수", f"{comments:,}개")
                    
                    m3, m4 = st.columns(2)
                    m3.metric("좋아요 수", f"{likes:,}개")
                    m4.metric("게시 날짜", published_at.strftime('%Y-%m-%d'))

                # 하단: 상세 요약 표
                st.subheader("📝 영상 요약 정리")
                df_summary = pd.DataFrame({
                    "항목": ["영상 제목", "채널명", "업로드 일시", "영상 ID"],
                    "상세 내용": [title, channel, published_at.strftime('%Y년 %m월 %d일 %H:%M'), video_id]
                })
                st.table(df_summary)

            else:
                st.warning("영상을 찾을 수 없습니다. URL을 다시 확인해주세요.")
                
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
    else:
        st.error("유효한 유튜브 URL 형식이 아닙니다.")
