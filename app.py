import streamlit as st
import pandas as pd
import requests
import json

# 🔹 config.json 파일에서 기본값 불러오기
def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

config = load_config()  # 설정 파일 로드
default_repo_owner = config["repo_owner"]
default_repo_name = config["repo_name"]

# 🔹 Streamlit UI
st.title("📊 GitHub Commit Activity Dashboard")
st.write("🔍 GitHub 리포지토리를 분석하고 기여도를 확인하세요.")

# 🔹 사용자 입력 (기본값 제공 + 수정 가능)
repo_owner = st.text_input("GitHub 사용자 또는 조직명", default_repo_owner)
repo_name = st.text_input("GitHub 리포지토리 이름", default_repo_name)

# 🔹 사용자에게 GitHub 토큰 입력 요청 (선택 사항)
token = st.text_input("GitHub 토큰 입력 (필요한 경우)", type="password")

if st.button("데이터 가져오기"):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/commits"
    headers = {"Authorization": f"token {token}"} if token else {}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        commits = response.json()
        df = pd.DataFrame([
            {"SHA": c["sha"], "Author": c["commit"]["author"]["name"], "Date": c["commit"]["author"]["date"], "Message": c["commit"]["message"]}
            for c in commits
        ])
        df["Date"] = pd.to_datetime(df["Date"]).dt.date
        st.subheader("📝 최근 커밋 내역")
        st.dataframe(df)  # 결과 표시
    else:
        st.error(f"GitHub API 요청 실패: {response.status_code}")
