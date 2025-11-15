"""
语音识别API - 使用Google Speech-to-Text API
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
import io
from typing import Optional

router = APIRouter(prefix="/api/speech", tags=["speech"])

# 尝试导入 Google Cloud Speech
GOOGLE_SPEECH_AVAILABLE = False
try:
    from google.cloud import speech
    GOOGLE_SPEECH_AVAILABLE = True
except ImportError:
    print("警告: Google Cloud Speech库未安装，语音识别功能将不可用")


@router.post("/transcribe")
async def transcribe_audio(audio_file: UploadFile = File(...)):
    """
    将音频文件转换为文字
    支持格式: WAV, FLAC, MP3, OGG, OPUS, AMR, M4A
    """
    if not GOOGLE_SPEECH_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="Google Speech-to-Text service is not available. Please install google-cloud-speech library."
        )
    
    try:
        # 检查是否有API密钥
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        credentials_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
        
        # 读取音频文件
        audio_content = await audio_file.read()
        
        # 初始化 Google Speech 客户端
        if credentials_json:
            import json
            credentials_info = json.loads(credentials_json)
            client = speech.SpeechClient.from_service_account_info(credentials_info)
        elif credentials_path and os.path.exists(credentials_path):
            client = speech.SpeechClient()
        elif credentials_path:
            raise HTTPException(
                status_code=503,
                detail="Google Cloud credentials file not found. Please check GOOGLE_APPLICATION_CREDENTIALS path."
            )
        else:
            # 尝试使用默认凭证（如果已设置环境变量）
            try:
                client = speech.SpeechClient()
            except Exception as e:
                raise HTTPException(
                    status_code=503,
                    detail="Google Cloud credentials not configured. Please set GOOGLE_APPLICATION_CREDENTIALS or GOOGLE_CREDENTIALS_JSON."
                )
        
        # 根据文件类型确定编码格式
        file_extension = audio_file.filename.split('.')[-1].lower() if audio_file.filename else 'webm'
        content_type = audio_file.content_type or ''
        
        # 映射文件类型到编码格式
        encoding_map = {
            'webm': speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            'opus': speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            'wav': speech.RecognitionConfig.AudioEncoding.LINEAR16,
            'flac': speech.RecognitionConfig.AudioEncoding.FLAC,
            'mp3': speech.RecognitionConfig.AudioEncoding.MP3,
            'ogg': speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
            'amr': speech.RecognitionConfig.AudioEncoding.AMR,
            'm4a': speech.RecognitionConfig.AudioEncoding.MP3,
        }
        
        # 默认使用 WebM Opus（浏览器常用格式）
        audio_encoding = encoding_map.get(file_extension, speech.RecognitionConfig.AudioEncoding.WEBM_OPUS)
        
        # 配置识别参数
        config = speech.RecognitionConfig(
            encoding=audio_encoding,
            sample_rate_hertz=48000,  # WebM Opus 通常使用 48000 Hz
            language_code="en-US",  # 主要语言：英文
            alternative_language_codes=["zh-CN"],  # 备选语言：中文
            enable_automatic_punctuation=True,
            model="latest_long",  # 使用最新的长音频模型
        )
        
        audio = speech.RecognitionAudio(content=audio_content)
        
        # 执行识别
        response = client.recognize(config=config, audio=audio)
        
        # 提取识别结果
        transcript = ""
        for result in response.results:
            if result.alternatives:
                transcript += result.alternatives[0].transcript + " "
        
        transcript = transcript.strip()
        
        if not transcript:
            return JSONResponse(
                status_code=200,
                content={
                    "success": False,
                    "error": "No speech detected in audio"
                }
            )
        
        return {
            "success": True,
            "transcript": transcript,
            "confidence": response.results[0].alternatives[0].confidence if response.results and response.results[0].alternatives else None
        }
    
    except Exception as e:
        print(f"语音识别失败: {type(e).__name__}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Speech recognition failed: {str(e)}"
        )

