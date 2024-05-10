#!/bin/bash
#SBATCH --nodes=1 
#SBATCH --time=0:10:00
#SBATCH --gres=gpu:2
#SBATCH --constraint=a100
#SBATCH --ntasks=4
#SBATCH --tasks-per-node=4
#SBATCH --cpus-per-task=4
#SBATCH --job-name=estate
#SBATCH --mail-type=ALL
#SBATCH --output=bin/%x-%j-slurm.out
#SBATCH --error=bin/%x-%j-slurm.err

# entire script fails if a single command fails
set -e

# create the conda environment
PROJECT_DIR=/ibex/user/wangc0g/gysun/projs/LLaMA-Estate
# source conda env
source /ibex/user/${USER}/mambaforge/bin/activate
echo "activation conda"

ENV_PREFIX="$PROJECT_DIR"/env
mamba env create --prefix $ENV_PREFIX --file "$PROJECT_DIR"/environment.yml
conda activate llama
echo "activation env"

cd "$PROJECT_DIR"

export WANDB_API_KEY='ee181b943a37dc1d4de0ed8aac14a15db109d7cb'
sh local_train.sh
