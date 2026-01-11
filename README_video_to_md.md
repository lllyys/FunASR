# 视频转Markdown脚本使用说明

## 功能简介

这个脚本可以批量将文件夹内的所有视频文件转换为Markdown文档。处理流程：
1. 从视频中提取音频（使用ffmpeg）
2. 使用FunASR模型转录音频为文字
3. 生成包含转录内容的Markdown文档

## 环境要求

### 系统依赖
- Python 3.7+
- ffmpeg（用于音频提取）
- CUDA（如使用GPU加速）

### Python依赖
```bash
pip install funasr
pip install torch  # 根据CUDA版本安装对应的PyTorch
```

### 安装ffmpeg

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
从 [ffmpeg官网](https://ffmpeg.org/download.html) 下载并添加到系统PATH

## 使用方法

### 基本用法
```bash
python video_to_md.py <视频文件夹路径>
```

### 指定输出文件夹
```bash
python video_to_md.py <视频文件夹路径> <输出文件夹路径>
```

### 指定临时文件夹
```bash
python video_to_md.py <视频文件夹路径> <输出文件夹路径> <临时文件夹路径>
```

## 使用示例

### 示例1: 处理当前目录下的videos文件夹
```bash
python video_to_md.py ./videos
```
Markdown文件将生成在 `./videos` 目录下

### 示例2: 指定输出目录
```bash
python video_to_md.py ./videos ./transcripts
```
Markdown文件将生成在 `./transcripts` 目录下

### 示例3: 指定临时文件夹
```bash
python video_to_md.py ./videos ./transcripts ./temp_audio
```
临时音频文件将保存在 `./temp_audio` 目录下（处理完成后会自动删除）

## 支持的视频格式

- .mp4
- .avi
- .mov
- .mkv
- .flv
- .wmv
- .webm
- .m4v

## 输出格式

生成的Markdown文档包含以下内容：
- 视频文件名
- 文件路径
- 生成时间
- 完整的转录文本

示例输出：
```markdown
# example.mp4

## 视频信息
- **文件名**: example.mp4
- **文件路径**: /path/to/example.mp4
- **生成时间**: 2026-01-11 10:30:00

## 转录内容

[转录的文字内容...]

---
*本文档由视频自动转录生成*
```

## 注意事项

1. **GPU加速**: 脚本默认使用 `cuda:0`，如果没有GPU，需要修改脚本中的 `device="cuda:0"` 为 `device="cpu"`

2. **磁盘空间**: 处理过程中会生成临时音频文件，确保有足够的磁盘空间

3. **处理时间**: 转录时间取决于视频长度和硬件性能，较长的视频需要更多时间

4. **中文支持**: FunASR模型主要针对中文优化，英文转录效果可能有所不同

5. **首次运行**: 首次运行时会自动下载模型文件，需要网络连接

## 修改为CPU模式

如果没有GPU，修改 [video_to_md.py](video_to_md.py) 中的第127行：
```python
# 修改前
device="cuda:0",

# 修改后
device="cpu",
```

## 故障排除

### 错误: 未找到ffmpeg
- 确保已安装ffmpeg并添加到系统PATH

### 模型加载失败
- 检查网络连接（首次运行需要下载模型）
- 确认CUDA环境配置正确（如使用GPU）

### 转录结果为空
- 检查视频是否包含音频轨道
- 尝试播放视频确认音频可用

## 性能优化建议

1. 使用GPU可显著提高转录速度
2. 如处理大量视频，可考虑批量处理
3. 定期清理临时文件夹
