import websockets
import uuid
import json
import random
import urllib.request
import urllib.parse
from PIL import Image
from io import BytesIO
import configparser
import os
import tempfile
import requests
import argparse
import shlex



# Read the configuration
config = configparser.ConfigParser()
config.read('config.properties')
server_address = config['LOCAL']['SERVER_ADDRESS']
text2img_config = config['LOCAL_TEXT2IMG']['CONFIG']
img2img_config = config['LOCAL_IMG2IMG']['CONFIG']
upscale_config = config['LOCAL_UPSCALE']['CONFIG']

def queue_prompt(prompt, client_id):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req =  urllib.request.Request("http://{}/prompt".format(server_address), data=data)
    return json.loads(urllib.request.urlopen(req).read())

def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen("http://{}/view?{}".format(server_address, url_values)) as response:
        return response.read()

def get_history(prompt_id):
    with urllib.request.urlopen("http://{}/history/{}".format(server_address, prompt_id)) as response:
        return json.loads(response.read())
    
def upload_image(filepath, subfolder=None, folder_type=None, overwrite=False):
    url = f"http://{server_address}/upload/image"
    files = {'image': open(filepath, 'rb')}
    data = {
        'overwrite': str(overwrite).lower()
    }
    if subfolder:
        data['subfolder'] = subfolder
    if folder_type:
        data['type'] = folder_type
    response = requests.post(url, files=files, data=data)
    return response.json()

class ImageGenerator:
    def __init__(self):
        self.client_id = str(uuid.uuid4())
        self.uri = f"ws://{server_address}/ws?clientId={self.client_id}"
        self.ws = None

    async def connect(self):
        self.ws = await websockets.connect(self.uri)

    async def get_images(self, prompt):
        if not self.ws:
            await self.connect()
    
        prompt_id = queue_prompt(prompt, self.client_id)['prompt_id']
        currently_Executing_Prompt = None
        output_images = []
        async for out in self.ws:
            try:
                message = json.loads(out)
                if message['type'] == 'execution_start':
                    currently_Executing_Prompt = message['data']['prompt_id']
                if message['type'] == 'executing' and prompt_id == currently_Executing_Prompt:
                    data = message['data']
                    if data['node'] is None and data['prompt_id'] == prompt_id:
                        break
            except ValueError as e:
                print("Incompatible response from ComfyUI");
                
        history = get_history(prompt_id)[prompt_id]

        for node_id in history['outputs']:
            node_output = history['outputs'][node_id]
            if 'images' in node_output:
                for image in node_output['images']:
                    image_data = get_image(image['filename'], image['subfolder'], image['type'])
                    if 'final_output' in image['filename']:
                        pil_image = Image.open(BytesIO(image_data))
                        output_images.append(pil_image)

        return output_images

    async def close(self):
        if self.ws:
            await self.ws.close()

def parsePrompt(prompt: str):
    # 这是必须被解析的命令行参数字符串
    # prompt = "a cute cat --images=4"

    # 使用 shlex.split 来正确地拆分参数字符串（保留命令行参数格式不变）
    arguments = shlex.split(prompt)

    # 创建一个 ArgumentParser 对象
    parser = argparse.ArgumentParser(description='Generate images.')

    # 定义命令行参数
    # 添加了一个 `prompt` 参数来处理 "a tiger" 部分，使用 nargs='+' 来接收全部单词
    parser.add_argument('prompt', nargs='+', help='Text to describe the image content')
    parser.add_argument('--images', type=int, default=4, help='Number of images to generate.')

    # 解析提供的参数列表
    args = parser.parse_args(arguments)

    # prompt 是一个列表，所以我们需要将单词合并成一个字符串
    text_for_search = ' '.join(args.prompt)

    # 输出解析后的参数
    print(f"Text for image search: {text_for_search}")
    print(f"Number of images requested: {args.images}")
    return text_for_search,args

async def generate_images(prompt: str,negative_prompt: str):
    with open(text2img_config, 'r') as file:
      workflow = json.load(file)
      
    generator = ImageGenerator()
    await generator.connect()

    output_node = config.get('LOCAL_TEXT2IMG', 'OUTPUT_NODES').split(',')
    prompt_nodes = config.get('LOCAL_TEXT2IMG', 'PROMPT_NODES').split(',')
    neg_prompt_nodes = config.get('LOCAL_TEXT2IMG', 'NEG_PROMPT_NODES').split(',')
    rand_seed_nodes = config.get('LOCAL_TEXT2IMG', 'RAND_SEED_NODES').split(',') 
    
    text_for_search,args = parsePrompt(prompt)

    for node in output_node:
        if not "amount" in workflow[node]["inputs"]:
            workflow[node]["inputs"]["batch_size"] = args.images
        workflow[node]["inputs"]["batch_size"] = args.images


    # Modify the prompt dictionary
    if(prompt != None and prompt_nodes[0] != ''):
      for node in prompt_nodes:
          workflow[node]["inputs"]["text"] = text_for_search
    if(negative_prompt != None and neg_prompt_nodes[0] != ''):
      for node in neg_prompt_nodes:
          workflow[node]["inputs"]["text"] = negative_prompt
    if(rand_seed_nodes[0] != ''):
      for node in rand_seed_nodes:
          if not "noise_seed" in workflow[node]["inputs"]:
            workflow[node]["inputs"]["seed"] = random.randint(0,999999999999999)
          workflow[node]["inputs"]["noise_seed"] = random.randint(0,999999999999999)

    images = await generator.get_images(workflow)
    await generator.close()

    return images

async def generate_alternatives(image: Image.Image, prompt: str, negative_prompt: str):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
      image.save(temp_file, format="PNG")
      temp_filepath = temp_file.name

    # Upload the temporary file using the upload_image method
    response_data = upload_image(temp_filepath)
    filename = response_data['name']
    with open(img2img_config, 'r') as file:
      workflow = json.load(file)
      
    generator = ImageGenerator()
    await generator.connect()

    output_node = config.get('LOCAL_IMG2IMG', 'OUTPUT_NODES').split(',')
    prompt_nodes = config.get('LOCAL_IMG2IMG', 'PROMPT_NODES').split(',')
    neg_prompt_nodes = config.get('LOCAL_IMG2IMG', 'NEG_PROMPT_NODES').split(',')
    rand_seed_nodes = config.get('LOCAL_IMG2IMG', 'RAND_SEED_NODES').split(',') 
    file_input_nodes = config.get('LOCAL_IMG2IMG', 'FILE_INPUT_NODES').split(',') 

    text_for_search,args = parsePrompt(prompt)


    for node in output_node:
        workflow[node]["inputs"]["amount"] = args.images


    if(prompt != None and prompt_nodes[0] != ''):
      for node in prompt_nodes:
          workflow[node]["inputs"]["text"] = text_for_search
    if(negative_prompt != None and neg_prompt_nodes[0] != ''):
      for node in neg_prompt_nodes:
          workflow[node]["inputs"]["text"] = negative_prompt
    if(rand_seed_nodes[0] != ''):
      for node in rand_seed_nodes:
          workflow[node]["inputs"]["seed"] = random.randint(0,999999999999999)
    if(file_input_nodes[0] != ''):
      for node in file_input_nodes:
          workflow[node]["inputs"]["image"] = filename

    images = await generator.get_images(workflow)
    await generator.close()

    return images

async def upscale_image(image: Image.Image, prompt: str,negative_prompt: str):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
      image.save(temp_file, format="PNG")
      temp_filepath = temp_file.name

    # Upload the temporary file using the upload_image method
    response_data = upload_image(temp_filepath)
    filename = response_data['name']
    with open(upscale_config, 'r') as file:
      workflow = json.load(file)

    generator = ImageGenerator()
    await generator.connect()

    prompt_nodes = config.get('LOCAL_UPSCALE', 'PROMPT_NODES').split(',')
    neg_prompt_nodes = config.get('LOCAL_UPSCALE', 'NEG_PROMPT_NODES').split(',')
    rand_seed_nodes = config.get('LOCAL_UPSCALE', 'RAND_SEED_NODES').split(',') 
    file_input_nodes = config.get('LOCAL_UPSCALE', 'FILE_INPUT_NODES').split(',') 

    # Modify the prompt dictionary
    if(prompt != None and prompt_nodes[0] != ''):
      for node in prompt_nodes:
          workflow[node]["inputs"]["text"] = prompt
    if(negative_prompt != None and neg_prompt_nodes[0] != ''):
      for node in neg_prompt_nodes:
          workflow[node]["inputs"]["text"] = negative_prompt
    if(rand_seed_nodes[0] != ''):
      for node in rand_seed_nodes:
          workflow[node]["inputs"]["seed"] = random.randint(0,999999999999999)
    if(file_input_nodes[0] != ''):
      for node in file_input_nodes:
          workflow[node]["inputs"]["image"] = filename

    images = await generator.get_images(workflow)
    await generator.close()

    return images[0]