# ComfyUI Remove Background - AI Coding Agent Instructions

## Project Overview
This is a **ComfyUI custom node extension** that integrates the `rembg` (remove background) library into ComfyUI's node graph editor. It provides a single reusable node for background removal in image processing workflows.

## Architecture & Key Concepts

### ComfyUI Custom Node Pattern
The project follows ComfyUI's required structure in `__init__.py`:
- **Node Class**: `RemoveBackgroundNode` follows the implicit ComfyUI node interface
- **`INPUT_TYPES()`**: Returns a dict with `"required"` key defining inputs - here, a single "image" parameter of type `"IMAGE"`
- **`RETURN_TYPES` & `RETURN_NAMES`**: Must match actual returns - this node returns `("IMAGE", "MASK")` as RGBA image and alpha mask
- **`FUNCTION`**: String pointing to the method that processes inputs (must match exact method name: `"remove_bg"`)
- **`CATEGORY`**: Groups nodes in UI ("SBCODE" category)
- **Export Pattern**: `NODE_CLASS_MAPPINGS` and `NODE_DISPLAY_NAME_MAPPINGS` dicts at module level for ComfyUI registration

### Data Type Conversions
The node bridges three tensor/image representations:
1. **ComfyUI tensors**: Shape `(batch, height, width, channels)` with float32 values in [0, 1]
2. **PIL Images**: Used by `rembg.remove()` for actual processing
3. **NumPy arrays**: Intermediate format for type conversion

Key conversion methods:
- `tensor_to_pil()`: Extracts first batch item `[0]`, scales to [0, 255], converts to uint8 PIL Image
- `pil_to_tensor()`: Reverses process, handles grayscale by expanding dims, returns batched tensor with `unsqueeze(0)`

### The Background Removal Flow
```
ComfyUI IMAGE tensor → tensor_to_pil() → rembg.remove() → RGBA PIL Image
  → pil_to_tensor() for RGBA + split()[-1] for alpha → Return (rgba_tensor, mask_tensor)
```

## Critical Implementation Details

**Output Format**: `rembg.remove()` returns RGBA; the node extracts alpha channel separately:
- `output.split()[-1]` isolates the alpha channel (4th channel in RGBA)
- Alpha is converted to a single-channel mask tensor for ComfyUI compatibility
- RGBA tensor includes the alpha channel (4-channel output)

**Tensor Batching**: ComfyUI processes batched images; code assumes batch_size=1 with `tensor[0]` indexing. Multi-batch handling would require looping.

**Range Conversions**: Critical for correctness
- Input from ComfyUI: [0, 1] float32
- rembg expects: [0, 255] uint8 (handled in `tensor_to_pil`)
- Output to ComfyUI: [0, 1] float32 (handled in `pil_to_tensor`)

## File Structure
```
__init__.py              # Entire node implementation (single file)
pyproject.toml          # Project metadata + ComfyUI registry configuration
requirements.txt        # Dependencies: onnxruntime, rembg
README.md              # Installation and usage docs
```

## Development Patterns & Conventions

**When Modifying This Node**:
- Always maintain symmetry between `INPUT_TYPES()` and `remove_bg()` method parameters
- Always update `INPUT_TYPES` → `RETURN_TYPES`/`RETURN_NAMES` in sync
- Tensor indexing assumes batch_size=1; document if supporting multi-batch
- Keep pixel value ranges consistent throughout conversions
- Don't modify `FUNCTION` ("remove_bg") or `CATEGORY` ("SBCODE") strings without understanding ComfyUI's node discovery

**Testing Approach**: Since this integrates with ComfyUI, manual testing through the UI is standard. Verify:
- Node appears in UI under "SBCODE" category with display name "Remove Background"
- Input image loads correctly (shape preservation from tensor)
- Output RGBA image and mask tensor have expected dimensions
- Alpha channel is properly extracted as single-channel mask

## Common Tasks

**Adding a new input parameter** (e.g., model selection, threshold):
1. Add to `INPUT_TYPES()` dict under `"required"` with proper type (e.g., `("STRING", {"default": "u2net"})`)
2. Add parameter to `remove_bg()` method signature
3. Pass parameter to `rembg.remove()` call
4. Update `RETURN_TYPES`/`RETURN_NAMES` only if return values change

**Modifying output structure**: Always update both `RETURN_TYPES` tuple AND `RETURN_NAMES` tuple simultaneously, then verify ComfyUI can connect outputs to compatible nodes downstream.

## Integration Points
- **rembg library**: Opaque ML dependency; only call `remove(pil_image)` with PIL Images, pass parameters as kwargs
- **ComfyUI framework**: Node discovery via `NODE_CLASS_MAPPINGS` export; ComfyUI handles tensor allocation/scheduling/graph execution
- **Dependencies**: `onnxruntime` (required by rembg), `torch`, `PIL`, `numpy` for tensor/image conversions
- **pyproject.toml**: Used by ComfyUI registry at https://registry.comfy.org for package discovery
