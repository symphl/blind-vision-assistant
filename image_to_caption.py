import requests
import json
from PIL import Image
from io import BytesIO
import base64
from sendtext import send_text_to_esp32


ESP_Cam_IP = ""
ESP_TTL_IP = ""

for i in range(3):
    requests.get(f'http://{ESP_Cam_IP}/')

response = requests.get(f'http://{ESP_Cam_IP}/')

if response.status_code == 200:
    
    try:
        image = Image.open(BytesIO(response.content))
    except Exception as e:
        print(f"Failed to open the image: {e}")
        exit(1)
    
    buffered = BytesIO()
    image.save(buffered, format="JPEG")  
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": "Bearer <API_KEY>",
            "Content-Type": "application/json",
            "HTTP-Referer": "<YOUR_SITE_URL>",
            "X-Title": "<YOUR_SITE_NAME>",
        },
        data=json.dumps({
            "model": "qwen/qwen2.5-vl-72b-instruct:free",
            "messages": [
                {
                    "role": "system",
                    "content": """Describe images EXACTLY like this format:
                    - Keep description under 200 characters total
                    - Ignore the Horizontal lines they are the Camera error only
                    - Direct present-tense descriptions
                    - No speculative language
                    - Focused on key elements only
                    - Spatial orientation first
                    - Most important physical objects only
                    """
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Describe this scene from my perspective in EXACTLY 200 characters or less. Focus on key physical elements only:"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{img_str}"
                            }
                        }
                    ]
                }
            ]
        })
    )

    text_resp = response.json()["choices"][0]["message"]["content"]
    
    if len(text_resp) > 200:
        text_resp = text_resp[:197] + "..."
        
    send_text_to_esp32(ESP_TTL_IP, text_resp)

else:
    print(f"Failed to retrieve the image. Status code: {response.status_code}")

print("Playing text: To your left, clothes hang on a wooden door. A small table stands in front of you, holding various items. To the right, another wooden door with a towel and a green hanger. The floor is smooth. Move forward carefully, avoiding the table and items on the floor. The space feels confined.")