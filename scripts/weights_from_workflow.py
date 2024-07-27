import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from helpers.ComfyUI_LayerDiffuse import ComfyUI_LayerDiffuse

def handle_weights(workflow):
    weights_to_download = []
    weights_filetypes = [
        ".ckpt",
        ".safetensors",
        ".pt",
        ".pth",
        ".bin",
        ".onnx",
        ".torchscript",
    ]

    for node in workflow.values():
        for handler in [
            ComfyUI_LayerDiffuse,
        ]:
            handler.add_weights(weights_to_download, node)

        if "inputs" in node:
            for input in node["inputs"].values():
                if isinstance(input, str) and any(
                    input.endswith(ft) for ft in weights_filetypes
                ):
                    weights_to_download.append(input)

    weights_to_download = list(set(weights_to_download))
    return weights_to_download

def main(filename):
    weights = []
    with open(filename, 'r') as f:
        workflow = json.load(f)
        weights = handle_weights(workflow)
    print('\n'.join(weights))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python weights_from_workflow.py  <workflow.json>")
        sys.exit(1)
    filename = sys.argv[1]
    main(filename)
