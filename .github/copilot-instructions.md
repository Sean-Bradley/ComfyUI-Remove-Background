# ComfyUI Remove Background - AI Coding Agent Instructions

## Project Overview
This is a **ComfyUI custom node extension** that integrates the `rembg` (remove background) library into ComfyUI's node graph editor. It provides a single reusable node for background removal in image processing workflows.

## Architecture & Key Concepts

### ComfyUI Custom Node Pattern
The project follows ComfyUI's required structure:
- **Node Class**: `RemoveBackgroundNode` inherits the node interface (implicit from pattern)
- **`INPUT_TYPES()`**: Returns a dict defining required inputs - here, a single "image" parameter of type `"IMAGE"`
- **`RETURN_TYPES` & `RETURN_NAMES`**: Must match actual returns - this node returns `("IMAGE", "MASK")` as RGBA image and alpha mask
- **`FUNCTION`**: String pointing to the method that processes inputs (must match exact method name: `"remove_bg"`)
- **`CATEGORY`**: Groups nodes in UI ("SBCODE" category)
- **Export Pattern**: `NODE_CLASS_MAPPINGS` and `NODE_DISPLAY_NAME_MAPPINGS` dicts at module level for registration

### Data Type Conversions
The node bridges three tensor/image representations:
1. **ComfyUI tensors**: Shape `(batch, height, width, channels)` with float32 values in [0, 1]
2. **PIL Images**: Used by `rembg.remove()` for actual processing
3. **NumPy arrays**: Intermediate format for type conversion

Key conversion methods:
- `tensor_to_pil()`: Extracts first batch item, scales to [0, 255], converts to uint8 PIL Image
- `pil_to_tensor()`: Reverses process, handles grayscale by expanding dims, returns batched tensor

### The Background Removal Flow
```
ComfyUI IMAGE tensor → PIL Image → rembg.remove() → RGBA PIL Image → Extract RGBA & Alpha → Return tensors
```

## Critical Implementation Details

**Output Format**: `rembg.remove()` returns RGBA; the node extracts alpha channel separately:
- `output.split()[-1]` isolates the alpha channel (4th channel in RGBA)
- Alpha is converted to a single-channel mask tensor for ComfyUI
- RGBA tensor includes the alpha channel (4-channel output)

**Tensor Batching**: ComfyUI processes batched images; code assumes batch_size=1 with `tensor[0]` indexing. Multi-batch handling would require looping.

## File Structure & Dependencies
```
__init__.py          # Single source file containing entire node implementation
rembg               # External dependency for background removal (must be installed)
PIL, torch, numpy   # Standard dependencies for tensor/image conversions
folder_paths        # ComfyUI module (imported but unused in current implementation)
```

## Development Patterns & Conventions

**When Modifying This Node**:
- Always maintain `INPUT_TYPES` → `RETURN_TYPES`/`RETURN_NAMES` consistency
- Tensor indexing assumes batch_size=1; document if supporting multi-batch
- Keep pixel value ranges consistent: ComfyUI uses [0, 1] floats; rembg uses [0, 255] uint8
- Don't modify `FUNCTION` or `CATEGORY` strings without understanding ComfyUI's node discovery

**Testing Approach**: Since this integrates with ComfyUI, manual testing through the UI is the standard approach. Verify:
- Node appears in UI under "SBCODE" category with display name "Remove Background (RMBG)"
- Input image loads correctly (shape preservation)
- Output RGBA image and mask tensor have expected dimensions

## Common Tasks

**Adding a new input parameter** (e.g., threshold):
1. Add to `INPUT_TYPES()` return dict with proper type
2. Add parameter to `remove_bg()` method signature
3. Update `RETURN_TYPES`/`RETURN_NAMES` if return values change

**Changing output types**: Must update both `RETURN_TYPES` tuple AND `RETURN_NAMES` tuple simultaneously, then verify ComfyUI can connect outputs to compatible nodes.

## Integration Points
- **rembg library**: Opaque dependency for the actual ML model; only call `remove()` with PIL Images
- **ComfyUI framework**: Node discovery via `NODE_CLASS_MAPPINGS` export; assumes ComfyUI handles tensor allocation/scheduling
- **Upstream data**: Receives IMAGE from ComfyUI node graph (unknown source in workflow)
