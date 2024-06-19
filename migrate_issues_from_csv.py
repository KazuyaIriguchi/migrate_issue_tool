import os

import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv

# 環境変数を読み込む
load_dotenv()

# GitHub設定
github_base_url = "https://api.github.com"
github_repo = os.getenv("GITHUB_REPO")
github_token = os.getenv("GITHUB_TOKEN")

# ページの設定
st.sidebar.title("GitLab to GitHub Migration")
page = st.sidebar.selectbox("Choose the operation", ["Issues", "Merge Requests"])


def create_github_issue(row, headers, issues_url):
    labels = row["Labels"].split(",") if pd.notna(row["Labels"]) else []
    issue = {
        "title": row["Title"],
        "body": row["Description"],
        "labels": [label.strip() for label in labels],
    }
    response = requests.post(issues_url, json=issue, headers=headers)
    return response.status_code


def create_github_pull_request(row, headers, pulls_url):
    pull_request = {
        "title": row["Title"],
        "body": row["Description"],
        "head": row["Source Branch"],
        "base": row["Target Branch"],
        "draft": "draft" in row["Title"].lower(),
    }
    response = requests.post(pulls_url, json=pull_request, headers=headers)
    return response.status_code


if page == "Issues":
    st.title("GitLab Issues to GitHub Migration")

    # CSVファイルのアップロード
    uploaded_file = st.file_uploader(
        "Upload GitLab exported Issues CSV file", type=["csv"]
    )

    if uploaded_file is not None:
        # CSVファイルを読み込む
        df = pd.read_csv(uploaded_file)

        # CSVファイルの内容を表示
        st.write("CSV File Content:")
        st.dataframe(df)

        # チェックボックスの追加
        to_migrate = st.multiselect("Select Issues to Migrate", df.index)

        if st.button("Migrate Issues to GitHub"):
            # GitHubにIssueを作成
            github_headers = {
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github.v3+json",
            }
            github_issues_url = f"{github_base_url}/repos/{github_repo}/issues"

            success_count = 0
            failure_count = 0

            for index in to_migrate:
                row = df.loc[index]
                status_code = create_github_issue(
                    row, github_headers, github_issues_url
                )
                if status_code == 201:
                    success_count += 1
                else:
                    failure_count += 1

            # 結果を表示
            st.write(
                f"Migration completed: {success_count} issues created successfully, {failure_count} issues failed."
            )

elif page == "Merge Requests":
    st.title("GitLab Merge Requests to GitHub Migration")

    # CSVファイルのアップロード
    uploaded_file = st.file_uploader(
        "Upload GitLab exported Merge Requests CSV file", type=["csv"]
    )

    if uploaded_file is not None:
        # CSVファイルを読み込む
        df = pd.read_csv(uploaded_file)

        # CSVファイルの内容を表示
        st.write("CSV File Content:")
        st.dataframe(df)

        # チェックボックスの追加
        to_migrate = st.multiselect("Select Merge Requests to Migrate", df.index)

        if st.button("Migrate Selected Merge Requests to GitHub"):
            # GitHubにPull Requestを作成
            github_headers = {
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github.v3+json",
            }
            github_pulls_url = f"{github_base_url}/repos/{github_repo}/pulls"

            success_count = 0
            failure_count = 0

            for index in to_migrate:
                row = df.loc[index]
                status_code = create_github_pull_request(
                    row, github_headers, github_pulls_url
                )
                if status_code == 201:
                    success_count += 1
                else:
                    failure_count += 1

            # 結果を表示
            st.write(
                f"Migration completed: {success_count} merge requests created successfully, {failure_count} merge requests failed."
            )
