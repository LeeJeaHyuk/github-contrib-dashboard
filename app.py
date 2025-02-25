import streamlit as st
import pandas as pd
import requests
import json
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import platform
from font_utils import set_korean_font  # 🔹 외부 파일에서 함수 가져오기

# 한글 폰트 적용
set_korean_font()

# 🔹 config.json 파일에서 데이터 불러오기
def load_config():
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)

config = load_config()  # 설정 파일 로드
repo_options = [f"{repo['repo_owner']}/{repo['repo_name']}" for repo in config["repositories"]]

# 🔹 Streamlit UI
st.title("📊 GitHub Commit Activity Dashboard")
st.write("🔍 GitHub 리포지토리를 분석하고 기여도를 확인하세요.")

# 🔹 사용자가 분석할 리포지토리를 선택할 수 있도록 selectbox 추가
selected_repo = st.selectbox("분석할 리포지토리 선택", repo_options)

# 🔹 선택된 값을 분리하여 repo_owner와 repo_name 추출
selected_repo_data = next(repo for repo in config["repositories"] if f"{repo['repo_owner']}/{repo['repo_name']}" == selected_repo)
repo_owner = selected_repo_data["repo_owner"]
repo_name = selected_repo_data["repo_name"]

# 🔹 GitHub Personal Access Token 입력 요청 (비공개 리포지토리 지원)
token = st.text_input("🔑 GitHub Personal Access Token 입력 (프라이빗 리포지토리 필요)", type="password")

if st.button("데이터 가져오기"):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/commits"
    headers = {"Authorization": f"token {token}"} if token else {}

    response = requests.get(url, headers=headers)
    response.encoding = "utf-8"  # 🔹 UTF-8 인코딩 설정

    if response.status_code == 200:
        data = response.content.decode("utf-8")  # 🔹 UTF-8로 강제 디코딩
        commits = json.loads(data)  # JSON 파싱

        # 📌 커밋 데이터 가공
        df = pd.DataFrame([
            {
                "SHA": c["sha"],
                "Author": c["commit"]["author"]["name"],  # 한글 처리됨
                "Date": c["commit"]["author"]["date"],
                "Message": c["commit"]["message"]
            }
            for c in commits
        ])
        df["Date"] = pd.to_datetime(df["Date"]).dt.date  # 날짜 형식 변환

        # 📝 최근 커밋 내역 출력
        st.subheader(f"📝 최근 커밋 내역 ({repo_owner}/{repo_name})")
        st.dataframe(df)

        # 📊 사용자별 커밋 수 집계
        commits_by_author = df["Author"].value_counts().reset_index()
        commits_by_author.columns = ["Author", "Commit Count"]

        # 📌 📊 시각화 1: 사용자별 커밋 횟수 막대 그래프
        st.subheader("📊 사용자별 커밋 횟수")
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(commits_by_author["Author"], commits_by_author["Commit Count"], color="blue")
        plt.xticks(rotation=45)
        plt.xlabel("사용자")
        plt.ylabel("커밋 수")
        plt.title("사용자별 커밋 기여도")
        st.pyplot(fig)

        # 📌 📊 시각화 2: 기여도 파이 차트
        st.subheader("👥 사용자별 기여도 비율")
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.pie(commits_by_author["Commit Count"], labels=commits_by_author["Author"], autopct="%1.1f%%", startangle=90)
        plt.title("사용자별 기여도")
        st.pyplot(fig)

    else:
        st.error(f"GitHub API 요청 실패: {response.status_code}")
