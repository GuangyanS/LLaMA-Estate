#!/bin/bash

DATA_FOLDER="saves/Llama-3-8B-Instruct"

# Set CUDA device
CUDA_VISIBLE_DEVICES=0 python src/train.py \
    --stage sft \
    --do_predict \
    --model_name_or_path meta-llama/Meta-Llama-3-8B-Instruct\
    --adapter_name_or_path ../../init_weights/estate_checkpoint/lora/sft \
    --dataset parsed_test_15032024 \
    --dataset_dir ../../datasets/estate \
    --template default \
    --finetuning_type lora \
    --output_dir $DATA_FOLDER \
    --overwrite_cache \
    --overwrite_output_dir \
    --cutoff_len 1024 \
    --preprocessing_num_workers 16 \
    --per_device_eval_batch_size 1 \
    --predict_with_generate

# Run the Python scripts with the specified data folder
python split_label_predict.py --data_folder $DATA_FOLDER
python visualization.py --data_folder $DATA_FOLDER
