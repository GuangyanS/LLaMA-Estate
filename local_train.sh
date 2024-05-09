#!/bin/bash

CUDA_VISIBLE_DEVICES=1,2,3 accelerate launch \
    --config_file examples/accelerate/single_config.yaml \
    src/train.py \
    --stage sft \
    --do_train \
    --model_name_or_path NousResearch/Llama-2-7b-hf \
    --dataset parsed_train_06032024 \
    --dataset_dir ../../datasets/estate \
    --template default \
    --finetuning_type lora \
    --lora_target q_proj,v_proj \
    --output_dir saves/LLaMA2-7B/lora/sft \
    --overwrite_cache \
    --overwrite_output_dir \
    --cutoff_len 8192 \
    --preprocessing_num_workers 16 \
    --per_device_train_batch_size 1 \
    --gradient_accumulation_steps 2 \
    --lr_scheduler_type cosine \
    --logging_steps 10 \
    --warmup_steps 20 \
    --save_steps 1000 \
    --learning_rate 5e-5 \
    --num_train_epochs 3.0 \
    --ddp_timeout 180000000 \
    --plot_loss \
    --fp16 \
    --report_to wandb \
    --run_name 'Llama2-7b-hf-parsed_train_06032024'
