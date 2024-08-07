import subprocess
import time
import os

from weights_manifest import WeightsManifest

BASE_URL = "https://weights.replicate.delivery/default/comfy-ui"


class WeightsDownloader:
    def __init__(self):
        self.weights_manifest = WeightsManifest()
        self.weights_map = self.weights_manifest.weights_map

    def download_weights(self, weight_str):
        if weight_str in self.weights_map:
            self.download_if_not_exists(
                weight_str,
                self.weights_map[weight_str]["url"],
                self.weights_map[weight_str]["dest"],
            )
        else:
            raise ValueError(
                f"{weight_str} unavailable. View the list of available weights: https://github.com/fofr/cog-comfyui/blob/main/supported_weights.md"
            )

    def download_if_not_exists(self, weight_str, url, dest):
        if not os.path.exists(f"{dest}/{weight_str}"):
            self.download(weight_str, url, dest)

    def download(self, weight_str, url, dest):
        tar_file = url.endswith(".tar")
        if "/" in weight_str:
            subfolder = weight_str.rsplit("/", 1)[0]
            if tar_file:
                dest = os.path.join(dest, subfolder)
                os.makedirs(dest, exist_ok=True)
            else:
                dest_dir = os.path.join(dest, subfolder)
                os.makedirs(dest_dir, exist_ok=True)
                dest = os.path.join(dest, weight_str)

        print(f"⏳ Downloading {weight_str} to {dest}")
        start = time.time()
        if tar_file:
            subprocess.check_call(
                ["pget", "--log-level", "warn", "-xf", url, dest], close_fds=False
            )
        else:
            subprocess.check_call(
                ["pget", "--log-level", "warn", "-f", url, dest], close_fds=False
            )
        elapsed_time = time.time() - start
        try:
            file_size_bytes = os.path.getsize(
                os.path.join(dest, os.path.basename(weight_str)) if tar_file else dest
            )
            file_size_megabytes = file_size_bytes / (1024 * 1024)
            print(
                f"⌛️ Downloaded {weight_str} in {elapsed_time:.2f}s, size: {file_size_megabytes:.2f}MB"
            )
        except FileNotFoundError:
            print(f"⌛️ Downloaded {weight_str} in {elapsed_time:.2f}s")
