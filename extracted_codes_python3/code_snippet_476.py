from openai import OpenAI
import chromadb

client = chromadb.PersistentClient("d:/JHQ/chromaRAG/data/persist")

collection = client.get_collection("test")
rescc = collection.query(query_texts="工程概况应包括什么",n_results=3)

print(rescc.get("documents"))



# Modify OpenAI's API key and API base to use vLLM's API server.
openai_api_key = "EMPTY"
openai_api_base = "http://localhost:8000/v1/"
client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)

completion = client.chat.completions.create(model="/data/JHQ/modelspace/Qwen-1.5-14B",
                                      messages=[
                                        {"role": "system", "content": "You are a helpful assistant."},
                                        {"role": "user", "content": "参考文本回答问题我的问题是：工程概况应包括什么 | "+"".join(rescc.get("documents")[0])},
                                    ],
                                    stream=False,max_tokens=2048)
# 流式
for message in completion:
    print(message)
