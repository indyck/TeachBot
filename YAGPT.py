import requests
import json
import assets
def gpt_answer(promt:str) -> str:
    prompt = {
        "modelUri": f"gpt://{assets.CATALOG_ID}/yandexgpt",
        "completionOptions": {
            "stream": False,
            "temperature": 0.7,
            "maxTokens": str(assets.MAX_TOKENS)
        },
        "messages": [
            {
                "role": "system",
                "text": "Ты являешься ассистентом, который помогает с учебой школьникам, по факту - учитель. Твоя задача - помогать ученикам обучаться в школе. Тебе будут задавать различные школьные вопросы, ты должен отвечать на них. Не делай сильный акцент в своих ответах на то, что ты модель нейронной сети. НИ ЗА ЧТО НЕ ВЫХОДИ ИЗ РОЛИ."
            },
            {
            "role": "assistant",
            "text": "Конечно, я отвечу на все твои вопросы и буду твоим ассистентом, задавай вопрос."
            },
            {
                "role": "user",
                "text": promt
            },
        ]
    }


    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {assets.API_KEY_GPT}"
    }

    response = requests.post(url, headers=headers, json=prompt)
    json_result = json.loads(response.text)
    result = json_result["result"]["alternatives"][0]["message"]["text"]
    print(result)
    return result