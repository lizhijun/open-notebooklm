---
title: Open NotebookLM
emoji: 🎙️
colorFrom: purple
colorTo: red
sdk: gradio
sdk_version: 5.0.1
app_file: app.py
pinned: true
header: mini
short_description: Personalised Podcasts For All - Available in 13 Languages
---

# Open NotebookLM

## Overview

This project is inspired by the NotebookLM tool, and implements it with open-source LLMs and text-to-speech models. This tool processes the content of a PDF, generates a natural dialogue suitable for an audio podcast, and outputs it as an MP3 file.

Built with:
- [Llama 3.3 70B 🦙](https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct) via [Fireworks AI 🎆](https://fireworks.ai/) and [Instructor 📐](https://github.com/instructor-ai/instructor) 
- [MeloTTS 🐚](https://huggingface.co/myshell-ai/MeloTTS-English)
- [Bark 🐶](https://huggingface.co/suno/bark)
- [Jina Reader 🔍](https://jina.ai/reader/)

## Features

- **Convert PDF to Podcast:** Upload a PDF and convert its content into a podcast dialogue.
- **Engaging Dialogue:** The generated dialogue is designed to be informative and entertaining.
- **User-friendly Interface:** Simple interface using Gradio for easy interaction.

## 前置要求

在运行项目之前，请确保安装以下依赖：

1. **Python 3.12+**

2. **ffmpeg** - 用于音频处理
   ```bash
   # MacOS
   brew install ffmpeg
   
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install ffmpeg
   
   # Windows
   # 从 https://www.ffmpeg.org/download.html 下载并安装
   ```

## 安装步骤

1. **克隆仓库:**
   ```bash
   git clone https://github.com/gabrielchua/open-notebooklm.git
   cd open-notebooklm
   ```

2. **创建虚拟环境并激活:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # MacOS/Linux
   # 或
   .venv\Scripts\activate  # Windows
   ```

3. **安装依赖包:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Set up API Key(s):**
   For this project, I am using LLama 3.3 70B hosted on Fireworks API as its JSON Mode supports passing a pydantic object. So, please set the API key as the `FIREWORKS_API_KEY` environment variable

2. **Run the application:**
   ```bash
   python app.py
   ```
   This will launch a Gradio interface in your web browser.

3. **Upload a PDF:**
   Upload the PDF document you want to convert into a podcast.

4. **Generate Audio:**
   Click the button to start the conversion process. The output will be an MP3 file containing the podcast dialogue.

## Acknowledgements

This project is forked from [`knowsuchagency/pdf-to-podcast`](https://github.com/knowsuchagency/pdf-to-podcast)

## License

This project is licensed under the Apache 2.0 License. See the [LICENSE](LICENSE) file for more information.
