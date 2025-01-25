"""
utils.py

Functions:
- generate_script: Get the dialogue from the LLM.
- call_llm: Call the LLM with the given prompt and dialogue format.
- parse_url: Parse the given URL and return the text content.
- generate_podcast_audio: Generate audio for podcast using TTS or advanced audio models.
- _use_suno_model: Generate advanced audio using Bark.
- _use_melotts_api: Generate audio using TTS model.
- _get_melo_tts_params: Get TTS parameters based on speaker and language.
"""

# Standard library imports
import time
from typing import Any, Union

# Third-party imports
import requests
from loguru import logger
from bark import SAMPLE_RATE, generate_audio, preload_models
from gradio_client import Client
from scipy.io.wavfile import write as write_wav
import backoff
from urllib3.util.retry import Retry
import urllib3
import json

# Local imports
from constants import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_MODEL,
    DEEPSEEK_MAX_TOKENS,
    DEEPSEEK_TEMPERATURE,
    MELO_API_NAME,
    MELO_TTS_SPACES_ID,
    MELO_RETRY_ATTEMPTS,
    MELO_RETRY_DELAY,
    JINA_READER_URL,
    JINA_RETRY_ATTEMPTS,
    JINA_RETRY_DELAY,
    DEEPSEEK_BASE_URL,
)
from schema import ShortDialogue, MediumDialogue

# Initialize Hugging Face client
hf_client = Client(MELO_TTS_SPACES_ID)

# Download and load all models for Bark
preload_models()

# 禁用不安全的 HTTPS 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def create_openai_client():
    """创建带有重试机制的 OpenAI 客户端"""
    # 创建自定义的 httpx 客户端
    client = httpx.Client(
        verify=certifi.where(),  # 使用 certifi 的证书
        timeout=30.0,
        follow_redirects=True
    )
    
    return OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com/v1",
        timeout=30.0,
        max_retries=3,
        http_client=client,  # 使用自定义的 httpx 客户端
    )

def generate_script(
    system_prompt: str,
    input_text: str,
    output_model: Union[ShortDialogue, MediumDialogue],
) -> Union[ShortDialogue, MediumDialogue]:
    """获取对话脚本，带有错误重试"""
    try:
        first_draft_dialogue = call_llm(system_prompt, input_text, output_model)
        
        # 添加改进提示
        improvement_prompt = f"{system_prompt}\n\n这是第一版对话:\n\n{first_draft_dialogue.model_dump_json()}\n\n请改进对话，使其更自然流畅。"
        final_dialogue = call_llm(improvement_prompt, "请优化对话内容", output_model)
        
        return final_dialogue
    except Exception as e:
        logger.error(f"生成对话脚本失败: {str(e)}")
        raise gr.Error("生成对话时出错，请稍后重试")

def call_api(system_prompt: str, text: str) -> dict:
    """直接调用 DeepSeek API"""
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        "temperature": DEEPSEEK_TEMPERATURE,
        "max_tokens": DEEPSEEK_MAX_TOKENS,
        "response_format": {"type": "json_object"}
    }
    
    try:
        response = requests.post(
            f"{DEEPSEEK_BASE_URL}/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"API 调用失败: {str(e)}")
        raise

@backoff.on_exception(
    backoff.expo,
    Exception,
    max_tries=3,
    max_time=30
)
def call_llm(system_prompt: str, text: str, dialogue_format: Any) -> Any:
    """调用 LLM 并处理响应"""
    try:
        response = call_api(system_prompt, text)
        result = response['choices'][0]['message']['content']
        logger.debug(f"API 返回结果: {result}")
        
        try:
            # 尝试解析 JSON
            data = json.loads(result)
            # 处理中文说话者名称
            if 'dialogue' in data:
                for item in data['dialogue']:
                    if item['speaker'] == '小美':
                        item['speaker'] = 'Host (Jane)'
                    elif item['speaker'] == '专家':
                        item['speaker'] = 'Guest'
            # 验证数据结构
            return dialogue_format(**data)
        except Exception as e:
            logger.error(f"JSON 解析错误: {str(e)}")
            raise
            
    except Exception as e:
        logger.error(f"调用 DeepSeek API 时出错: {str(e)}")
        raise

def parse_url(url: str) -> str:
    """Parse the given URL and return the text content."""
    for attempt in range(JINA_RETRY_ATTEMPTS):
        try:
            full_url = f"{JINA_READER_URL}{url}"
            response = requests.get(full_url, timeout=60)
            response.raise_for_status()  # Raise an exception for bad status codes
            break
        except requests.RequestException as e:
            if attempt == JINA_RETRY_ATTEMPTS - 1:  # Last attempt
                raise ValueError(
                    f"Failed to fetch URL after {JINA_RETRY_ATTEMPTS} attempts: {e}"
                ) from e
            time.sleep(JINA_RETRY_DELAY)  # Wait for X second before retrying
    return response.text

def generate_podcast_audio(
    text: str, speaker: str, language: str, use_advanced_audio: bool, random_voice_number: int
) -> str:
    """Generate audio for podcast using TTS or advanced audio models."""
    if use_advanced_audio:
        return _use_suno_model(text, speaker, language, random_voice_number)
    else:
        return _use_melotts_api(text, speaker, language)

def _use_suno_model(text: str, speaker: str, language: str, random_voice_number: int) -> str:
    """Generate advanced audio using Bark."""
    host_voice_num = str(random_voice_number)
    guest_voice_num = str(random_voice_number + 1)
    audio_array = generate_audio(
        text,
        history_prompt=f"v2/{language}_speaker_{host_voice_num if speaker == 'Host (Jane)' else guest_voice_num}",
    )
    file_path = f"audio_{language}_{speaker}.mp3"
    write_wav(file_path, SAMPLE_RATE, audio_array)
    return file_path

def _use_melotts_api(text: str, speaker: str, language: str) -> str:
    """Generate audio using TTS model."""
    accent, speed = _get_melo_tts_params(speaker, language)

    for attempt in range(MELO_RETRY_ATTEMPTS):
        try:
            return hf_client.predict(
                text=text,
                language=language,
                speaker=accent,
                speed=speed,
                api_name=MELO_API_NAME,
            )
        except Exception as e:
            if attempt == MELO_RETRY_ATTEMPTS - 1:  # Last attempt
                raise  # Re-raise the last exception if all attempts fail
            time.sleep(MELO_RETRY_DELAY)  # Wait for X second before retrying

def _get_melo_tts_params(speaker: str, language: str) -> tuple[str, float]:
    """Get TTS parameters based on speaker and language."""
    if speaker == "Guest":
        accent = "EN-US" if language == "EN" else language
        speed = 0.9
    else:  # host
        accent = "EN-Default" if language == "EN" else language
        speed = (
            1.1 if language != "EN" else 1
        )  # if the language is not English, try speeding up so it'll sound different from the host
        # for non-English, there is only one voice
    return accent, speed
