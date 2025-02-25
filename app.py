import streamlit as st
import pandas as pd
import requests
import json

# 🔹 config.json 파일에서 데이터 불러오기
def load_config():
    with open("config.json", "r") as f:
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
    if response.status_code == 200:
        commits = response.json()
        df = pd.DataFrame([
            {"SHA": c["sha"], "Author": c["commit"]["author"]["name"], "Date": c["commit"]["author"]["date"], "Message": c["commit"]["message"]}
            for c in commits
        ])
        df["Date"] = pd.to_datetime(df["Date"]).dt.date
        st.subheader(f"📝 최근 커밋 내역 ({repo_owner}/{repo_name})")
        st.dataframe(df)  # 결과 표시
    else:
        st.error(f"GitHub API 요청 실패: {response.status_code}")
