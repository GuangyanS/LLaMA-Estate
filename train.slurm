#!/bin/bash
#SBATCH --nodes=1 
#SBATCH --time=0:10:00
#SBATCH --gres=gpu:3
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
PROJECT_DIR=/ibex/user/${USER}/gysun/projs/LLaMA-Estate
# source conda env
source /ibex/user/${USER}/mambaforge/bin/activate
echo "activation conda"

ENV_PREFIX="$PROJECT_DIR"/env

# Check if the environment already exists
if conda env list | grep -q "$ENV_PREFIX"; then
    echo "Environment already exists at ${ENV_PREFIX}. Activating environment."
else
    echo "Creating a new environment at ${ENV_PREFIX}."
    mamba env create --prefix "$ENV_PREFIX" --file "${PROJECT_DIR}/environment.yml"
    if [[ $? -ne 0 ]]; then
        echo "Failed to create environment. Exiting."
        exit 1
    fi
    echo "Environment created."
fi

conda activate "$ENV_PREFIX"
echo "activation env"

cd "$PROJECT_DIR"

export WANDB_API_KEY='ee181b943a37dc1d4de0ed8aac14a15db109d7cb'
export HF_TOKEN='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
sh local_train.sh
