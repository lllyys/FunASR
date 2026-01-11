#!/usr/bin/env python3
"""
视频转Markdown脚本
将指定文件夹内的所有视频文件提取音频并转录为Markdown文档
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from funasr import AutoModel

# 支持的视频格式
VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm', '.m4v'}

def extract_audio(video_path, output_audio_path):
    """
    从视频文件中提取音频

    Args:
        video_path: 视频文件路径
        output_audio_path: 输出音频文件路径

    Returns:
        bool: 提取是否成功
    """
    try:
        cmd = [
            'ffmpeg',
            '-i', str(video_path),
            '-vn',  # 不处理视频
            '-acodec', 'pcm_s16le',  # 音频编码格式
            '-ar', '16000',  # 采样率
            '-ac', '1',  # 单声道
            '-y',  # 覆盖已存在的文件
            str(output_audio_path)
        ]

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"错误: 提取音频失败 - {video_path}")
        print(f"详情: {e.stderr.decode('utf-8', errors='ignore')}")
        return False
    except FileNotFoundError:
        print("错误: 未找到ffmpeg，请确保已安装ffmpeg")
        return False


def transcribe_audio(audio_path, model):
    """
    使用FunASR转录音频

    Args:
        audio_path: 音频文件路径
        model: FunASR模型实例

    Returns:
        str: 转录文本
    """
    try:
        start = time.perf_counter()
        res = model.generate(input=[str(audio_path)], cache={}, batch_size_s=0)
        elapsed_s = time.perf_counter() - start

        text = res[0]["text"]
        print(f"  转录完成，耗时: {elapsed_s:.2f}秒")
        return text
    except Exception as e:
        print(f"错误: 转录失败 - {e}")
        return ""


def create_markdown(video_path, transcript_text, output_md_path):
    """
    创建Markdown文档

    Args:
        video_path: 原视频文件路径
        transcript_text: 转录文本
        output_md_path: 输出Markdown文件路径
    """
    video_name = video_path.name

    md_content = f"""# {video_name}

## 视频信息
- **文件名**: {video_name}
- **文件路径**: {video_path.absolute()}
- **生成时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}

## 转录内容

{transcript_text}

---
*本文档由视频自动转录生成*
"""

    try:
        with open(output_md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        print(f"  已生成: {output_md_path}")
    except Exception as e:
        print(f"错误: 无法写入Markdown文件 - {e}")


def process_videos(input_folder, output_folder=None, temp_folder=None):
    """
    批量处理视频文件

    Args:
        input_folder: 输入视频文件夹路径
        output_folder: 输出Markdown文件夹路径（默认为输入文件夹）
        temp_folder: 临时音频文件夹路径（默认为/tmp）
    """
    input_path = Path(input_folder)

    if not input_path.exists():
        print(f"错误: 输入文件夹不存在 - {input_folder}")
        return

    # 设置输出文件夹
    if output_folder is None:
        output_path = input_path
    else:
        output_path = Path(output_folder)
        output_path.mkdir(parents=True, exist_ok=True)

    # 设置临时文件夹
    if temp_folder is None:
        temp_path = Path("/tmp/video_transcripts")
    else:
        temp_path = Path(temp_folder)
    temp_path.mkdir(parents=True, exist_ok=True)

    # 查找所有视频文件
    video_files = []
    for ext in VIDEO_EXTENSIONS:
        video_files.extend(input_path.glob(f"*{ext}"))
        video_files.extend(input_path.glob(f"*{ext.upper()}"))

    if not video_files:
        print(f"在 {input_folder} 中未找到视频文件")
        print(f"支持的格式: {', '.join(VIDEO_EXTENSIONS)}")
        return

    print(f"找到 {len(video_files)} 个视频文件")
    print("正在初始化FunASR模型...")

    # 初始化模型
    try:
        model = AutoModel(
            model="FunAudioLLM/Fun-ASR-Nano-2512",
            vad_model="iic/speech_fsmn_vad_zh-cn-16k-common-pytorch",
            vad_kwargs={"max_single_segment_time": 30000},
            device="cuda:0",
        )
        print("模型加载成功\n")
    except Exception as e:
        print(f"错误: 模型加载失败 - {e}")
        return

    # 处理每个视频文件
    success_count = 0
    for idx, video_file in enumerate(video_files, 1):
        print(f"[{idx}/{len(video_files)}] 处理: {video_file.name}")

        # 生成临时音频文件路径
        audio_file = temp_path / f"{video_file.stem}.wav"

        # 提取音频
        print("  提取音频中...")
        if not extract_audio(video_file, audio_file):
            continue

        # 转录音频
        print("  转录音频中...")
        transcript = transcribe_audio(audio_file, model)

        if not transcript:
            print("  跳过: 转录结果为空")
            # 清理临时文件
            if audio_file.exists():
                audio_file.unlink()
            continue

        # 生成Markdown文件
        md_file = output_path / f"{video_file.stem}.md"
        create_markdown(video_file, transcript, md_file)

        # 清理临时音频文件
        if audio_file.exists():
            audio_file.unlink()

        success_count += 1
        print()

    print(f"完成! 成功处理 {success_count}/{len(video_files)} 个视频文件")
    print(f"Markdown文件保存在: {output_path.absolute()}")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python video_to_md.py <视频文件夹路径> [输出文件夹路径] [临时文件夹路径]")
        print("\n示例:")
        print("  python video_to_md.py ./videos")
        print("  python video_to_md.py ./videos ./output")
        print("  python video_to_md.py ./videos ./output ./temp")
        sys.exit(1)

    input_folder = sys.argv[1]
    output_folder = sys.argv[2] if len(sys.argv) > 2 else None
    temp_folder = sys.argv[3] if len(sys.argv) > 3 else None

    process_videos(input_folder, output_folder, temp_folder)


if __name__ == "__main__":
    main()
