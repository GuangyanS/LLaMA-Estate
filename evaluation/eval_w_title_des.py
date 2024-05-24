import os
import json
import re
from bs4 import BeautifulSoup
from tqdm import tqdm  

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

TEMPLATE = """
    You are an expert admin people who will extract core information from title and/or descriptions of real estate website with json output. 
    If a property is not present, make the output value null.

    Below is the content; please try to directly and only extract all data points from the content above with directly json format:
    {
    "Price":,
    "City":,
    "PostalCode":,
    "HabitatType": ,
    "AdvertType":,
    "HabitableSurface":,
    "LandSurface":,
    "RoomsNumber":,
    "BedsNumber":,
    }
    """

# Define paths
input_folder = '/home/dxleec/gysun/datasets/estate/202403080515_html/'
output_folder = '/home/dxleec/gysun/datasets/estate/202403080515_pred_td/'
os.makedirs(output_folder, exist_ok=True)

# Initialize the tokenizer and model
model_id = "meta-llama/Meta-Llama-3-8B-Instruct"

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.bfloat16,
    device_map="auto",
    do_sample=True,
    temperature=0.5,
    trust_remote_code=True, 
)

# Function to extract estate info using a given template
def extract_estate_info(title, description):
    messages = [
        {"role": "system", "content": TEMPLATE},
        {"role": "user", "content": "Title: " + title + "\nDescription: " + description},
    ]
    input_ids = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        return_tensors="pt"
    ).to(model.device)
    terminators = [
        tokenizer.eos_token_id,
        tokenizer.convert_tokens_to_ids("<|eot_id|>")
    ]
    outputs = model.generate(
        input_ids,
        max_new_tokens=256,
        eos_token_id=terminators,
        do_sample=True,
        temperature=0.6,
        top_p=0.9,
    )
    response = outputs[0][input_ids.shape[-1]:]
    generated_text = tokenizer.decode(response, skip_special_tokens=True)
    
    json_pattern = generated_text[generated_text.find("{"):generated_text.find("}")+1]
    if json_pattern:
        try:
            parsed_data = json.loads(json_pattern)
        except json.JSONDecodeError as e:
            parsed_data = {}
            print(f"Error parsing JSON: {e}")
    else:
        print("No JSON data found in the input string.")
        parsed_data = {}
    return parsed_data  # Assuming that the generated text is JSON formatted

def save_json(file_name, title, description, extracted_info):
   # Save the extracted information as a JSON file
    output_path = os.path.join(output_folder, f"{os.path.splitext(file_name)[0]}.json")
    with open(output_path, "w", encoding="utf-8") as output_file:
        extracted_info["Title"] = title
        extracted_info["Summary"] = description
        json.dump(extracted_info, output_file, indent=4)

# Iterate through all HTML files in the input folder
for file_name in tqdm(os.listdir(input_folder), desc='Processing Files'):
    if file_name.endswith(".html"):
        file_path = os.path.join(input_folder, file_name)
        print(f"Processing file: {file_path}")
        # Read and parse the HTML file
        with open(file_path, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, 'html.parser')
            title = soup.title.string if len(soup.title) > 0 else None
            # description_meta = soup.find_all("meta", {"name": "description"})
            # if description_meta is None:
            #     description_meta = soup.find_all("meta", {"property": "description"})
            # if description_meta is None:
            #     soup.find_all("meta", {"property": "og:description"})
            # description = next((meta.get("content") for meta in description_meta if meta.get("content")), None)
            # 定义不同的 meta 搜索条件
            meta_search_conditions = [
                {"name": "description"},
                {"property": "description"},
                {"property": "og:description"},
            ]

            # 初始为 None，开始依次尝试不同的搜索条件
            description = None

            # 循环所有条件，直到找到一个含有 content 属性的标签
            for condition in meta_search_conditions:
                description_meta = soup.find_all("meta", condition)
                # 使用生成器表达式来获取第一个有效的 content
                description = next((meta.get("content") for meta in description_meta if meta.get("content")), None)
                if description:
                    break

        # If both title and description exist, extract estate information using the Llama model
        if title and description:
            extracted_info = extract_estate_info(title, description)
            save_json(file_name, title, description, extracted_info)
        elif title:
            extracted_info = extract_estate_info(title, '')
            save_json(file_name, title, description, extracted_info)