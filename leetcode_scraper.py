import requests
import json
import time
import os

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0"}
SESSION = "" 
output_dir = "leetcode_samples"

if not os.path.exists(output_dir):
    os.mkdir(output_dir)

collected_count = 0
max_samples = 300

# Fetch all questions
response = requests.post(
    "https://leetcode.com/graphql/", headers=HEADERS, json={
        "operationName": "allQuestions",
        "query": """
        query allQuestions {
            problemsetQuestionList {
                questions {
                    questionId
                    titleSlug
                    difficulty
                }
            }
        }
        """
    },
    cookies={"LEETCODE_SESSION": SESSION}
)
questions_data = response.json().get("data", {}).get("problemsetQuestionList", {}).get("questions", [])

# Map question IDs to submission IDs dynamically
QUESTIONS = {}
for question in questions_data:
    question_id = int(question["questionId"])
    title_slug = question["titleSlug"]
    difficulty = question["difficulty"]

    if difficulty == "Medium":
        submission_response = requests.post(
            f"https://leetcode.com/graphql/", headers=HEADERS, json={
                "operationName": "recentSubmissions",
                "query": """
                query recentSubmissions($titleSlug: String!) {
                    recentSubmissions(titleSlug: $titleSlug) {
                        submissionId
                    }
                }
                """,
                "variables": {"titleSlug": title_slug}
            },
            cookies={"LEETCODE_SESSION": SESSION}
        )
        submission_ids = submission_response.json().get("data", {}).get("recentSubmissions", [])
        if submission_ids:
            QUESTIONS[question_id] = submission_ids[0]["submissionId"]

    time.sleep(1)

for question_id, submission_id in QUESTIONS.items():
    if collected_count >= max_samples:
        break

    try:
        response = requests.post(
            "https://leetcode.com/graphql/", headers=HEADERS, json={
                "operationName": "submissionDetails",
                "query": """
                query submissionDetails($submissionId: Int!) {
                    submissionDetails(submissionId: $submissionId) {
                        runtimeDistribution
                    }
                }
                """,
                "variables": {
                    "submissionId": submission_id
                }
            },
            cookies={"LEETCODE_SESSION": SESSION}
        )
        runtime_distribution = json.loads(
            json.loads(response.content)['data']['submissionDetails']['runtimeDistribution']
        )['distribution']

        # Iterate over runtimes to find a valid code snippet
        for runtime, _ in runtime_distribution:
            if collected_count >= max_samples:
                break

            code_response = requests.post(
                "https://leetcode.com/graphql/", headers=HEADERS, json={
                    "operationName": "codeWithRuntime",
                    "query": """
                    query codeWithRuntime($questionId: Int!, $lang: String!, $runtime: Int!, $skip: Int!) {
                        codeWithRuntime(
                            questionId: $questionId
                            lang: $lang
                            runtime: $runtime
                            skip: 0
                        ) {
                            code
                        }
                    }
                    """,
                    "variables": {
                        "lang": "python3",
                        "questionId": question_id,
                        "runtime": runtime,
                        "skip": 0
                    }
                },
                cookies={"LEETCODE_SESSION": SESSION}
            )
            code_snippet = json.loads(code_response.content).get('data', {}).get('codeWithRuntime', {}).get('code')

			# Check code size
            if code_snippet and len(code_snippet) > 700:
                file_path = os.path.join(output_dir, f"question_{question_id}.py")
                with open(file_path, 'w') as file:
                    file.write(code_snippet)

                collected_count += 1
                print(f"Collected {collected_count} samples...")
                break

            time.sleep(1)
    except Exception as e:
        print(f"Error processing question {question_id}: {e}")

print(f"Total samples collected: {collected_count}")
