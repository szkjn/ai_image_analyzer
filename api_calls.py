import os
import shutil
import json
import time
from openai import OpenAI
import base64
from playsound import playsound

from prompt_data import MAX_TOKENS, ERROR_SOUND, ai_personas
from utilities import SoundPlayer

# Initialize OpenAI clients with multiple API keys
api_key = os.environ.get('OPENAI_API_KEY1')
client = OpenAI(api_key=api_key)

common_prompt = f"DON'T COMMENT ON QUALITY OF PICTURE OR BACKGROUND. COMMENT ON THE SUBJECT ITSELF. \
    RESPOND IN AROUND {MAX_TOKENS} TOKENS. \
    OUTPUT THE RESULT IN THE FOLLOWING JSON FORMAT: {{'res': <judgmental description>}}"
prompt_base_judgement = ai_personas[0]["prompt"]

#------------------------
#-------- STEP 1 --------
#------------------------
def generate_image_desc(image_path: str, max_tokens: int) -> str:
    start_time = time.time()
    sound_step1_path = 'audio/base/bbc_noise6d.mp3'
    sound_player = SoundPlayer(sound_step1_path)
    sound_player.start()
    neutral_desc = None

    print("-- 1. Generating neutral description")

    try:
        with open(image_path, 'rb') as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            response = client.chat.completions.create(
                model="gpt-4o-mini", 
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": f"Describe what you see in a concise neutral tone (max {MAX_TOKENS} tokens)."},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                },
                            },
                        ],
                    }
                ],
                max_tokens=max_tokens,
            )

            neutral_desc = response.choices[0].message.content
            print(f"-- Image analysis result: {neutral_desc}")


            archive_dir = "archive"
            base_name = os.path.basename(image_path)
            archive_path = os.path.join(archive_dir, base_name)

            counter = 1
            file_name, file_extension = os.path.splitext(base_name)
            while os.path.exists(archive_path):
                archive_path = os.path.join(archive_dir, f"{file_name}_{counter}{file_extension}")
                counter += 1

            shutil.move(image_path, archive_path)


    except Exception as e:
        # playsound(ERROR_SOUND)
        print(f"-- ERROR: Failed to analyze image: {e}")

    sound_player.stop()
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"== Execution time: {execution_time} seconds") 

    return neutral_desc


#------------------------
#-------- STEP 2 --------
#------------------------
def create_judgemental_desc(text_str: str, id: int, max_tokens: int) -> str:
    start_time = time.time()
    sound_step1_path = 'audio/base/bbc_noise4d.mp3'
    sound_player = SoundPlayer(sound_step1_path)
    sound_player.start()
    judgemental_desc = None

    print("-- 2. Generating judgmental description")
    
    try:
        print("-- Attempting to create judgement")
        chat_completion = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": ai_personas[id]["prompt"] + common_prompt},
                {"role": "user", "content": text_str},
            ],
            max_tokens=max_tokens,
            temperature=1.2
        )

        print("-- Judgement created successfully")
        response = chat_completion.choices[0].message.content
        print(f"-- Response received: {response}")
        response_json = json.loads(response)

        judgemental_desc = response_json['res']
        print(f">> Judgement is done: {judgemental_desc}")    
    
    except Exception as e:
        # playsound(ERROR_SOUND)
        print(f"-- ERROR: Failed to create judgement: {e}")
        print(f"-- Exception details: {str(e)}")

    sound_player.stop()

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"== Execution time: {execution_time} seconds") 

    return judgemental_desc


#------------------------
#-------- STEP 3 --------
#------------------------
def generate_audio(text_str: str, id: int, output_path: str):
    start_time = time.time()
    sound_step1_path = 'audio/base/bbc_noise3d.mp3'
    sound_player = SoundPlayer(sound_step1_path)
    sound_player.start()
    print("-- 3. Generating TTS audio description")

    try:
        # Generate audio file from content with specified voice
        response = client.audio.speech.create(
            model="tts-1",
            input=text_str,
            voice=ai_personas[id]["voice"],
        )
        # Save audio file
        response.stream_to_file(output_path)

        print(f"-- Conversation audio segments saved with alternating voices.")

    except Exception as e:
        # playsound(ERROR_SOUND)
        print(f"-- ERROR: Failed to analyze image: {e}")

    sound_player.stop()
    
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"== Execution time: {execution_time} seconds") 
        