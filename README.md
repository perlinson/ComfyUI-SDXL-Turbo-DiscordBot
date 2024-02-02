# SDXL-Turbo-DiscordBot


**SDXL-Turbo-DiscordBot** is a Discord bot designed specifically for image generation using the renowned SDXL-Turbo 1.0 fp16 model. It's inspired by the features of the Midjourney Discord bot, offering capabilities like text-to-image generation, variations in outputs, and the ability to upscale these outputs for enhanced clarity.

<div align="center">

Support Author of SDXL-DiscrodBot work,Not me

[![Support Author of SDXL-DiscrodBot work](https://i.imgur.com/NOoWZ8G.png)](https://ko-fi.com/dab_bot)

</div>


## Key Features:

1. **Text-to-Image Generation**: Convert your ideas into visuals. Just type in a positive+negative prompt, and the bot will generate an image that matches your text.

2. **Variations on Outputs**: Not satisfied with the first image? The bot can produce multiple variations, giving you the freedom to choose the one that fits best.

3. **Upscale Outputs**: Enhance the clarity of generated images by upscaling them. Perfect for when you need higher resolution visuals.

4. **Integration Flexibility**: 
   - **Public Stability AI API**: For those who prefer a hassle-free setup, the bot can integrate seamlessly with the public Stability AI API. All you need is your API key.
   - **Local ComfyUI System**: For users who prioritize data privacy or want to work offline, the bot can run locally using the ComfyUI system.

5. **Custom Workflows with ComfyUI**: The bot comes with default configurations that cater to most users. However, if you have specific needs, it supports custom ComfyUI workflows, allowing you to tailor the bot's operations to your exact requirements.

## Quick Start

### 1. **Download & Extract**
- [Download the latest executable](https://github.com/perlinson/ComfyUI-SDXL-Turbo-DiscordBot/releases) suitable for your OS.
- Extract the zip file to your desired location.

### 2. **Configuration**
- Open `config.properties` using a text editor.
- Set your Discord bot token: Find `[BOT][TOKEN]` and replace the placeholder with your token.

### 3. **Choose Your Source**

#### Option A: **The Stability AI API**
- Set your API key: Replace the placeholder in `[API][API_KEY]` with your StabilityAI API key.
- Update the source: Change `[BOT][SDXL_SOURCE]` to 'API'.

#### Option B: **Local System via ComfyUI**
- Set if you want to use Proxy URL: Replace the placeholder in `[LOCAL][USE_PROXY]` to `TRUE`,Set your Proxy URL: Replace the placeholder in `[LOCAL][PROXY_URL]` with your Proxy URL (default is `127.0.0.1:7890`),otherwise set it to `FALSE`.
- .
- Update the source: Change `[BOT][SDXL_SOURCE]` to 'LOCAL'.
- Download and add models to ComfyUI:
  - [sd_xl_turbo_1.0_fp16 model](https://huggingface.co/stabilityai/sdxl-turbo/blob/main/sd_xl_turbo_1.0_fp16.safetensors) → `checkpoints` folder
  - [4x-Ultrasharp Upscaler model](https://huggingface.co/lokCX/4x-Ultrasharp/blob/main/4x-UltraSharp.pth) → `upscale_models` folder
- Ensure that ComfyUI is running while the bot is running

### 4. **Generate the App**
- navigate to the root directory
- run `pyinstaller pyinstaller .\bot.py  -i favicon.ico --onefile` to generate the executable.

### 5. **Run the App**
- Double-click on `SDXL-Bot.exe` to launch.
- **Note for Windows users:** If Windows Defender warns about an "unknown publisher", you can safely ignore it. You might also need to whitelist this app in your antivirus software.

## Advanced setup
For more advanced configuration and custom workflows visit the [wiki](https://github.com/dab-bot/ComfyUI-SDXL-DiscordBot/wiki/Advanced-config)
