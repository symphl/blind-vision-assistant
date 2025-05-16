import requests
import json


def send_text_to_esp32(ip_address, text):
    url = f"http://{ip_address}/speak"
    
    payload = {
        "text": text
    }
    
    json_payload = json.dumps(payload)
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, data=json_payload, headers=headers)
        
        if response.status_code == 200:
            print(f"Success: {response.text}")
        else:
            print(f"Error: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
