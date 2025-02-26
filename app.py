import streamlit as st
import requests
import json

# 🔹 최근 사용한 리포지토리를 저장할 파일
CONFIG_FILE = "recent_repos.json"

# 🔹 최근 사용한 리포지토리를 저장하는 함수
def save_recent_repos(repo_list):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(repo_list, f, indent=4)

# 🔹 최근 사용한 리포지토리를 불러오는 함수
def load_recent_repos():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# 🔹 최근 사용한 리포지토리 불러오기
recent_repos = load_recent_repos()

# 🔹 Streamlit UI
st.title("📊 GitHub Commit Activity Dashboard")
st.write("🔍 직접 입력 또는 최근 사용한 리포지토리 선택 가능")

# 🔹 최근 사용한 리포지토리 선택 or 직접 입력
selected_option = st.radio(
    "리포지토리 선택 방법", 
    ["최근 사용한 리포지토리 선택", "직접 입력"],
    key="repo_selection_option"  # ✅ 고유 key 추가
)

if selected_option == "최근 사용한 리포지토리 선택" and recent_repos:
    selected_repo = st.selectbox("🔹 최근 사용한 리포지토리", recent_repos, key="recent_repo")
    repo_owner, repo_name = selected_repo.split("/")
else:
    repo_owner = st.text_input("🔹 GitHub 사용자 또는 조직명 입력", "your-username", key="repo_owner_input")
    repo_name = st.text_input("🔹 GitHub 리포지토리 이름 입력", "your-repository", key="repo_name_input")

token = st.text_input("🔑 GitHub Personal Access Token 입력 (비공개 리포지토리 필요)", type="password", key="github_token")

if st.button("데이터 가져오기", key="fetch_data_button"):
    # 📌 API 요청 URL
    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/commits"
    headers = {"Authorization": f"token {token}"} if token else {}

    # 🔹 리포지토리 존재 여부 먼저 확인
    repo_check_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
    check_response = requests.get(repo_check_url, headers=headers)

    if check_response.status_code == 404:
        st.error(f"🚨 404 오류: `{repo_owner}/{repo_name}`를 찾을 수 없습니다.")
        st.stop()
    elif check_response.status_code == 403:
        st.error("🚨 403 오류: 접근 권한이 없습니다. 올바른 토큰을 입력하세요.")
        st.stop()

    # 🔹 커밋 데이터 가져오기
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        commits = response.json()
        st.success(f"✅ {repo_owner}/{repo_name}의 커밋 데이터를 성공적으로 불러왔습니다!")

        # 🔹 최근 사용한 리포지토리 저장 (중복 방지)
        new_repo = f"{repo_owner}/{repo_name}"
        if new_repo not in recent_repos:
            recent_repos.insert(0, new_repo)
            if len(recent_repos) > 5:  # 최근 사용한 리포지토리 5개까지만 저장
                recent_repos.pop()
            save_recent_repos(recent_repos)

        # 🔹 최근 커밋 데이터 표시
        st.write(commits[:5])  # 최근 5개 커밋 출력
    else:
        st.error(f"❌ GitHub API 요청 실패: {response.status_code}")
