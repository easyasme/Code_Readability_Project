import requests
import json
import time
import os
import sys

# User agent
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0"}
SESSION = ""
RANGE = 100 # Number of solutions to get from each question

# Mapping of question IDs to submission IDs
QUESTIONS = {
	146: 1471406520, # LRU Cache
	355: 1471395746, # Design Twitter
}

output_dir = "leetcode_samples"
if not os.path.exists(output_dir):
	os.mkdir(output_dir)

# Get distributions
for question_id, submission_id in QUESTIONS.items():
	distribution = requests.post("https://leetcode.com/graphql/", headers=HEADERS, json={
		"operationName": "submissionDetails",
		"query": "\n query submissionDetails($submissionId: Int!) {\n submissionDetails(submissionId: $submissionId) {\n runtime\n runtimeDisplay\n runtimePercentile\n runtimeDistribution\n memory\n memoryDisplay\n memoryPercentile\n memoryDistribution\n code\n timestamp\n statusCode\n user {\n username\n profile {\n realName\n userAvatar\n }\n }\n lang {\n name\n verboseName\n }\n question {\n questionId\n titleSlug\n hasFrontendPreview\n }\n notes\n flagType\n topicTags {\n tagId\n slug\n name\n }\n runtimeError\n compileError\n lastTestcase\n codeOutput\n expectedOutput\n totalCorrect\n totalTestcases\n fullCodeOutput\n testDescriptions\n testBodies\n testInfo\n stdOutput\n }\n}\n ",
		"variables": {
			"submissionId": submission_id
		}
	}, cookies={    
		"LEETCODE_SESSION": SESSION
	})
	distribution = [runtime for runtime, _ in json.loads(json.loads(distribution.content)['data']['submissionDetails']['runtimeDistribution'])['distribution']]

	for i in range(min(RANGE, len(distribution))):
		runtime = distribution[i]
		response = requests.post("https://leetcode.com/graphql/", headers=HEADERS, json={
			"operationName": "codeWithRuntime",
			"query": "\n query codeWithRuntime($questionId: Int!, $lang: String!, $runtime: Int!, $skip: Int!) {\n codeWithRuntime(\n questionId: $questionId\n lang: $lang\n runtime: $runtime\n skip: $skip\n ) {\n code\n hasPrevious\n hasNext\n }\n}\n ",
			"variables": {
				"lang": "python3",
				"questionId": question_id,
				"runtime": runtime,
				"skip": 0
			}
		}, cookies={
			"LEETCODE_SESSION": SESSION
		})
		
		try:
			snippet = json.loads(response.content)['data']['codeWithRuntime']['code']
			print(snippet)
			print("\n########################################################################\n")
			file_dir = os.path.join(output_dir, f"question_{question_id}")
			if not os.path.exists(file_dir):
				os.mkdir(file_dir)
			file_path = os.path.join(file_dir, f"sample_{i}.py")
			with open(file_path, 'w') as file:
				file.write(snippet)

		except:
			pass
		time.sleep(1)