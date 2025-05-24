import requests

tuning_text = open("tuning_text3.txt", "r", encoding="utf-8").read()

def get_access_token(token):
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

    payload={
    'scope': 'GIGACHAT_API_PERS'
    }
    headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'application/json',
    'RqUID': '92636ae3-e3fe-49c2-8f9f-af372adb3151',
    'Authorization': f'Basic {token}'
    }

    response = requests.request("POST", url, headers=headers, data=payload, verify=False)

    return response.json()["access_token"]


def parse_command(prompt, access_token):
    chat_url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"  # Актуальный URL API
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {
        "model": "GigaChat",
        "messages": [{"role": "user", "content": f"{tuning_text}\n{prompt}"}],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(
            chat_url,
            headers=headers,
            json=payload,
            verify=False,
            timeout=10
        )
        
        if response.status_code != 200:
            return {
                "error": f"HTTP Error {response.status_code}",
                "response_text": response.text
            }
            
        return response.json()
        
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


