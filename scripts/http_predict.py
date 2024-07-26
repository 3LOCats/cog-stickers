import requests
import json

data = {
    'input':{
    'prompt': 'cat',
    'negative_prompt': '',
    'width': 1024,
    'height': 1024,
    'steps': 5,
    'number_of_images': 1,
    'output_format': 'webp',
    'output_quality': 20,
    'sticker_type': 'Stickersheet',
    'seed': None
    }
}
json_data = json.dumps(data)

url = 'http://localhost:5000/predictions'

headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, headers=headers, data=json_data)


print("Status Code:", response.status_code)
print("Response Content:", response.content)
