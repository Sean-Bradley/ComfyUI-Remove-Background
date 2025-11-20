from rembg import remove
from PIL import Image
import torch
import numpy as np


class RemoveBackgroundNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("rgba_image", "alpha_mask")
    FUNCTION = "remove_bg"
    CATEGORY = "SBCODE"

    def tensor_to_pil(self, tensor):
        if len(tensor.shape) == 4:
            tensor = tensor[0]
        arr = (tensor.cpu().numpy() * 255).clip(0, 255).astype(np.uint8)
        return Image.fromarray(arr)

    def pil_to_tensor(self, pil_img):
        arr = np.array(pil_img).astype(np.float32) / 255.0
        if arr.ndim == 2:
            arr = np.expand_dims(arr, axis=-1)
        return torch.from_numpy(arr).unsqueeze(0)

    def remove_bg(self, image):
        pil_image = self.tensor_to_pil(image)
        output = remove(pil_image)  # returns RGBA

        rgba_tensor = self.pil_to_tensor(output)
        alpha = output.split()[-1]
        mask_tensor = self.pil_to_tensor(alpha)

        return (rgba_tensor, mask_tensor)


NODE_CLASS_MAPPINGS = {
    "RemoveBackground": RemoveBackgroundNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RemoveBackground": "Remove Background"
}
