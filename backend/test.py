import requests
import json

url = "http://127.0.0.1:8000/simulate"

data = {
    "champ1": {
        "name": "Aatrox",
        "level": 11,
        "items": ["Long Sword", "Phage"],
        "buffs": ["red"]
    },
    "champ2": {
        "name": "Garen",
        "level": 11,
        "items": ["Chain Vest", "Doran's Blade"],
        "buffs": []
    }
}

response = requests.post(url, json=data)
print("응답 상태:", response.status_code)
print("응답 내용:", response.text)

try:
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print("JSON 파싱 실패:", e)
