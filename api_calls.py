import os
import json
from openai import OpenAI
import base64


# Initialize OpenAI clients with multiple API keys
api_key_av = os.environ.get('OPENAI_API_KEY1')
api_key_txt = os.environ.get('OPENAI_API_KEY2')
client_av = OpenAI(api_key=api_key_av)
client_txt = OpenAI(api_key=api_key_txt)

prompt_base_judgement = "Transform the given description into a sassy, cynical description."
prompt_format = "Respond in max 150 words. Output the result in the following JSON format: {'res': <judgmental description>}"


def generate_image_desc(image_path: str) -> str:
    print("-- 1. Generating neutral description")
    try:
        with open(image_path, 'rb') as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            response = client_av.chat.completions.create(
                model="gpt-4-vision-preview", 
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Describe what you see in a concise neutral tone (max 100 words)."},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                },
                            },
                        ],
                    }
                ],
                max_tokens=100,
            )

            neutral_desc = response.choices[0].message.content

            print(f"-- Image analysis result: {neutral_desc}")
            return neutral_desc

    except Exception as e:
        print(f"-- ERROR: Failed to analyze image: {e}")


def create_judgemental_desc(text_str: str) -> str:
    print("-- 2. Generating judgmental description")
    chat_completion = client_txt.chat.completions.create(
        model="gpt-3.5-turbo",
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": prompt_base_judgement + prompt_format},
            {"role": "user", "content": text_str},
        ],
        max_tokens=150,
    )

    response = chat_completion.choices[0].message.content
    response_json = json.loads(response)

    result = response_json['res']
    print(f">> Judgement is done: {result}")    
    return result


def generate_audio(text_str: str, output_path):
    print("-- 3. Generating TTS audio description")

    # Generate audio file from content with specified voice
    response = client_av.audio.speech.create(
        model="tts-1",
        input=text_str,
        voice="shimmer",
    )
    # Save audio file
    response.stream_to_file(output_path)

    print(f"-- Conversation audio segments saved with alternating voices.")