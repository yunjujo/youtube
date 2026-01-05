import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd
from datetime import datetime
import isodate

# 페이지 설정
st.set_page_config(page_title="YouTube Video Analyzer", page_icon="📊", layout="wide")

# 사이드바에서 API 키 입력 받기
st.sidebar.title("Settings ⚙️")
api_key = st.sidebar.text_input("YouTube API Key를 입력하세요", type="password")

def get_video_id(url):
    """유튜브 URL에서 Video ID 추출"""
    if "youtu.be/" in url:
        return url.split("/")[-1]
    elif "v=" in url:
        return url.split("v=")[1].split("&")[0]
    else:
        return None

def get_video_details(youtube, video_id):
    """영상 상세 정보 가져오기"""
    request = youtube.videos().list(
        part="snippet,statistics,contentDetails",
        id=video_id
    )
    response = request.execute()
    return response['items'][0] if response['items'] else None

# 메인 UI
st.title("📺 YouTube 영상 데이터 분석기")
st.markdown("영상 URL을 입력하면 상세 통계와 썸네일을 확인할 수 있습니다.")

url = st.text_input("분석할 유튜브 영상 URL을 입력하세요", placeholder="https://www.youtube.com/watch?v=...")

if url and api_key:
    try:
        youtube = build("youtube", "v3", developerKey=api_key)
        video_id = get_video_id(url)
        
        if video_id:
            video_data = get_video_details(youtube, video_id)
            
            if video_data:
                snippet = video_data['snippet']
                stats = video_data['statistics']
                
                # 데이터 정리
                title = snippet['title']
                published_at = datetime.strptime(snippet['publishedAt'], "%Y-%m-%dT%H:%M:%SZ")
                view_count = int(stats.get('viewCount', 0))
                comment_count = int(stats.get('commentCount', 0))
                like_count = int(stats.get('likeCount', 0))
                thumbnail_url = snippet['thumbnails']['high']['url']
                
                st.divider()
                
                # 1. 썸네일 섹션
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.subheader("🖼️ Thumbnail")
                    st.image(thumbnail_url, use_container_width=True)
                    st.markdown(f"[🔗 썸네일 고화질 다운로드]({thumbnail_url})")
                
                # 2. 통계 지표 (한눈에 보기)
                with col2:
                    st.subheader("📊 핵심 지표")
                    m1, m2 = st.columns(2)
                    m1.metric("조회 수", f"{view_count:,}회")
                    m2.metric("댓글 수", f"{comment_count:,}개")
                    
                    m3, m4 = st.columns(2)
                    m3.metric("좋아요 수", f"{like_count:,}개")
                    m4.metric("게시일", published_at.strftime('%Y-%m-%d'))

                # 3. 요약 정보 정리 테이블
                st.subheader("📝 영상 요약 정보")
                summary_df = pd.DataFrame({
                    "항목": ["영상 제목", "채널명", "게시 날짜", "조회 수", "댓글 수"],
                    "내용": [title, snippet['channelTitle'], published_at.strftime('%Y-%m-%d %H:%M'), 
                             f"{view_count:,}회", f"{comment_count:,}개"]
                })
                st.table(summary_df)
                
            else:
                st.error("영상 정보를 불러올 수 없습니다. ID를 확인해주세요.")
        else:
            st.error("올바른 유튜브 URL 형식이 아닙니다.")
            
    except HttpError as e:
        st.error(f"API 오류 발생: {e}")
    except Exception as e:
        st.error(f"오류 발생: {e}")
else:
    if not api_key:
        st.info("왼쪽 사이드바에 YouTube API Key를 입력해주세요.")
