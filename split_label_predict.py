import json
import argparse

def parse_data_to_dict(data_str):
    data_dict = {}
    for line in data_str.split('\n'):
        if ': ' in line:
            key, value = line.split(': ', 1)
            if value.replace('.', '', 1).isdigit():
                value = float(value) if '.' in value else int(value)
            data_dict[key.strip()] = value
    return data_dict


def extract_label_predict(file_path):
    """Extract the label and predict data from the .jsonl file
    and refactor it into a new dictionary, keeping the number type"""
    label_data = {}
    predict_data = {}

    with open(file_path, 'r', encoding='utf-8') as file:
        for index, line in enumerate(file):
            data = json.loads(line)
            if 'label' in data:
                label_data[index] = parse_data_to_dict(data['label'])
            if 'predict' in data:
                predict_data[index] = parse_data_to_dict(data['predict'])

    return label_data, predict_data

def main(data_folder):
    # 构建文件路径
    file_path = f'{data_folder}/generated_predictions.jsonl'
    
    # 提取标签和预测数据
    label_data, predict_data = extract_label_predict(file_path)
    
    # 保存标签数据
    with open(f'{data_folder}/label_data.json', 'w') as fp:
        json.dump(label_data, fp)
    
    # 保存预测数据
    with open(f'{data_folder}/predict_data.json', 'w') as fp:
        json.dump(predict_data, fp)

if __name__ == '__main__':
    # 设置命令行参数
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--data_folder', type=str, help='Folder path containing data files')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 执行主函数
    main(args.data_folder)
