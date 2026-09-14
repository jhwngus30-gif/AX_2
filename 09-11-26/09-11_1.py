from openai import OpenAI
# # 실행방법 : python 파일명

# client = OpenAI(api_key="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") 
# -> 무효화된 api임!!
# # git에만 안올라가면 api를 써도 된다. git에 올라가는게 문제
# response = client.chat.completions.create(model='gpt-4o-mini', #model 지정
#                                           messages=[{'role':'system','content':'You are a helpful assistant'}])
# print(response.choices[0].message.content)

def ask_llm(api_key, model, question):
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {'role': 'system', 'content': '친절한 도우미'},
            {'role': 'user', 'content': question}
        ]
    )
    return response.choices[0].message.content, response.usage

my_api_key = 'YOUR_API_KEY'
# api_key : ai 에도 올리지 말기, api 적고 푸쉬해버리면 git에 올라감

answer, usage = ask_llm(my_api_key, 'gpt-4o-mini', '안녕하세요. 오늘 날씨가 어떤가요?')

print('Answer:', answer) 
