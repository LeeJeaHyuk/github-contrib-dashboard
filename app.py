import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt

# GitHub 커밋 데이터 가져오기 함수
def fetch_commits(repo_owner, repo_name, token):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/commits"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        commits = response.json()
        commit_data = []
        for commit in commits:
            sha = commit["sha"]
            author = commit["commit"]["author"]["name"]
            date = commit["commit"]["author"]["date"]
            message = commit["commit"]["message"]
            commit_data.append({"SHA": sha, "Author": author, "Date": date, "Message": message})

        df = pd.DataFrame(commit_data)
        df["Date"] = pd.to_datetime(df["Date"]).dt.date
        return df
    else:
        st.error(f"GitHub API 요청 실패: {response.status_code}")
        return pd.DataFrame()

# Streamlit UI
st.title("📊 GitHub Commit Activity Dashboard")
repo_owner = st.text_input("GitHub 사용자 또는 조직명", "your_org_or_username")
repo_name = st.text_input("GitHub 리포지토리 이름", "your_repository")
token = st.text_input("GitHub 토큰 (필요한 경우)", type="password")

if st.button("데이터 가져오기"):
    df = fetch_commits(repo_owner, repo_name, token)

    if not df.empty:
        commits_per_day = df.groupby("Date").size().reset_index(name="Commit Count")
        commits_by_author = df["Author"].value_counts().reset_index()
        commits_by_author.columns = ["Author", "Commit Count"]

        # 최근 커밋 내역 표시
        st.subheader("📝 최근 커밋 내역")
        st.dataframe(df.sort_values("Date", ascending=False))

        # 날짜별 커밋 수 그래프
        st.subheader("📆 날짜별 커밋 수")
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.bar(commits_per_day["Date"], commits_per_day["Commit Count"], color="blue")
        plt.xticks(rotation=45)
        st.pyplot(fig)

        # 팀원별 기여도 (파이차트)
        st.subheader("👥 팀원별 기여도")
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.pie(commits_by_author["Commit Count"], labels=commits_by_author["Author"], autopct="%1.1f%%", startangle=90)
        st.pyplot(fig)
