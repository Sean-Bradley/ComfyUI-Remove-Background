from rembg import new_session, remove
from PIL import Image
import torch
import numpy as np

SESSION = None

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

    def _get_session(self):
        global SESSION
        if SESSION is None:
            SESSION = new_session()
        return SESSION

    def tensor_to_pil(self, tensor):
        # tensor shape [B, H, W, C]
        if len(tensor.shape) == 4:
            tensor = tensor[0]
        arr = tensor.cpu().numpy()
        arr = (arr * 255).clip(0,255).astype(np.uint8)
        return Image.fromarray(arr)

    def pil_to_tensor_image(self, pil_img):
        arr = np.array(pil_img).astype(np.float32) / 255.0
        if arr.ndim == 2:
            # If grayscale, convert to 3-channel so C=3
            arr = np.stack([arr,arr,arr], axis=-1)
        return torch.from_numpy(arr).unsqueeze(0)

    def pil_to_tensor_mask(self, pil_mask):
        # pil_mask is a single-channel (‘L’) image
        arr = np.array(pil_mask).astype(np.float32) / 255.0
        # shape [H, W]
        tensor = torch.from_numpy(arr).unsqueeze(0)  # shape [1, H, W]
        return tensor

    def remove_bg(self, image):
        session = self._get_session()
        pil_image = self.tensor_to_pil(image)
        output = remove(pil_image, session=session)  # RGBA PIL

        rgba_tensor = self.pil_to_tensor_image(output)

        alpha = output.split()[-1]  # PIL single channel
        mask_tensor = self.pil_to_tensor_mask(alpha)
        mask_tensor = 1.0 - mask_tensor  # Invert mask: background=1, foreground=0

        return (rgba_tensor, mask_tensor)


NODE_CLASS_MAPPINGS = {
    "SBCODERemoveBackground": RemoveBackgroundNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SBCODERemoveBackground": "Remove Background"
}
