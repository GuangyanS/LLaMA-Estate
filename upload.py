from huggingface_hub import HfApi
api = HfApi()

api.upload_folder(
    folder_path="saves/LLaMA3-8B",
    repo_id="RIT4AGI/estate_checkpoint",
    repo_type="model",
)
