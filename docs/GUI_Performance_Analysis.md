# GUI Performance Analysis & Optimization Plan

## Current Performance Issues Identified

### 1. **Image Resize Operations (CRITICAL)**
**Location**: `display_image_in_panel()` in `improved_seedream_layout.py` (line 4342)

**Problems**:
- Opens image from disk on EVERY display call
- Resizes with LANCZOS (slowest but highest quality) every time
- No caching - same image resized repeatedly
- Creates new PhotoImage objects constantly

**Impact**: 
- 3600x3600px image → 2048x2048px resize = ~100-300ms PER resize
- During zoom: 5+ redraws = 500-1500ms total lag
- During drag: Constant redraws cause stuttering

### 2. **Zoom Event Handling**
**Location**: `on_mouse_wheel_zoom()` + `_apply_debounced_zoom()` (lines 2951-3021)

**Problems**:
- Calls `on_zoom_changed()` which calls `display_image_in_panel()`
- Even with 150ms debounce, still triggers full image reload+resize
- No incremental scaling - always full recalculation

**Impact**:
- Each zoom level change = full image reload + resize
- User sees delay between scroll and visual update

### 3. **Canvas Update Calls**
**Location**: Multiple places using `update_idletasks()`

**Problems**:
- Forces synchronous UI updates
- Blocks event loop
- Multiple calls in display pipeline

**Impact**:
- Adds 10-50ms per call
- Causes visible stuttering

### 4. **No Image Caching Strategy**
**Current State**: Zero caching

**Missing**:
- No PIL Image cache (disk I/O every time)
- No scaled image cache (resize every time)  
- No PhotoImage cache (recreation every time)

**Impact**:
- Repeated expensive operations
- High CPU usage
- High disk I/O

### 5. **Drag/Pan Implementation**
**Location**: Sync drag handlers (lines 255-354)

**Problems**:
- Each drag event can trigger scroll region recalculation
- No throttling on drag updates
- Recalculates sync position every pixel move

**Impact**:
- Drag feels sluggish
- High CPU during pan operations

---

## Optimization Strategies (Priority Order)

### **PRIORITY 1: Image Caching System**
**Expected Improvement**: 70-80% reduction in display time

```python
class ImageCache:
    """Cache for PIL images and scaled versions"""
    def __init__(self, max_cache_size=10):
        self.pil_cache = {}  # path -> PIL Image
        self.scaled_cache = {}  # (path, width, height) -> PIL Image
        self.photo_cache = {}  # (path, width, height) -> PhotoImage
        self.max_size = max_cache_size
        
    def get_pil_image(self, path):
        if path not in self.pil_cache:
            self.pil_cache[path] = Image.open(path)
            self._cleanup_cache()
        return self.pil_cache[path]
    
    def get_scaled_image(self, path, width, height):
        key = (path, width, height)
        if key not in self.scaled_cache:
            pil_img = self.get_pil_image(path)
            scaled = pil_img.resize((width, height), Image.Resampling.BILINEAR)
            self.scaled_cache[key] = scaled
            self._cleanup_cache()
        return self.scaled_cache[key]
```

**Benefits**:
- Disk I/O only on first load
- Resize only on first display at each size
- Near-instant redisplay at same zoom level

### **PRIORITY 2: Fast Resampling for Interactive Operations**
**Expected Improvement**: 60-70% faster resize operations

**Change**:
```python
# Use BILINEAR for interactive operations (zoom/drag)
img_resized = img.resize((new_width, new_height), Image.Resampling.BILINEAR)

# Use LANCZOS only for final display after interaction ends
img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
```

**Benefits**:
- BILINEAR is 3-5x faster than LANCZOS
- Still acceptable quality during interaction
- Upgrade to LANCZOS after 500ms of no interaction

### **PRIORITY 3: Eliminate Redundant Redraws**
**Expected Improvement**: 50-60% fewer redraws

**Strategy**:
```python
def display_image_in_panel(self, image_path, panel_type, force=False):
    # Check if redraw actually needed
    current_state = (image_path, self.zoom_var.get(), 
                     canvas.winfo_width(), canvas.winfo_height())
    
    if hasattr(self, '_last_display_state'):
        if self._last_display_state.get(panel_type) == current_state and not force:
            return  # Skip redundant redraw
    
    # ... do display ...
    
    self._last_display_state[panel_type] = current_state
```

**Benefits**:
- Skips unnecessary redraws
- Especially helpful during drag operations

### **PRIORITY 4: Async Image Loading**
**Expected Improvement**: Perceived performance boost

```python
async def display_image_async(self, image_path, panel_type):
    # Show placeholder immediately
    self.show_loading_indicator(panel_type)
    
    # Load/resize in background thread
    img_data = await asyncio.to_thread(self._load_and_resize, image_path)
    
    # Update UI in main thread
    self.parent_frame.after(0, lambda: self._display_photo(img_data, panel_type))
```

**Benefits**:
- UI stays responsive during load
- No blocking on large images
- Better perceived performance

### **PRIORITY 5: Remove update_idletasks() Calls**
**Expected Improvement**: 10-20% faster display

**Replace**:
```python
canvas.update_idletasks()  # REMOVE THIS
canvas_width = canvas.winfo_width()
```

**With**:
```python
# Use cached canvas size or scheduled update
canvas_width = getattr(self, f'_{panel_type}_canvas_width', 300)
```

**Benefits**:
- No forced synchronous updates
- Smoother event loop
- Less stuttering

### **PRIORITY 6: Optimize Drag Updates**
**Expected Improvement**: Smoother panning

```python
def handle_sync_drag(self, event, source_panel):
    # Throttle updates - only process every Nth pixel
    if not hasattr(self, '_drag_counter'):
        self._drag_counter = 0
    
    self._drag_counter += 1
    if self._drag_counter % 3 != 0:  # Process every 3rd event
        return
    
    # ... rest of drag logic ...
```

**Benefits**:
- Fewer drag events processed
- Smoother movement
- Lower CPU usage

---

## Implementation Impact Summary

| Optimization | Effort | Impact | Priority |
|-------------|--------|---------|----------|
| Image Caching | High | 70-80% faster | **P1** |
| Fast Resampling | Low | 60-70% faster | **P2** |
| Skip Redundant Redraws | Medium | 50-60% fewer calls | **P3** |
| Async Loading | Medium | Perceived boost | P4 |
| Remove update_idletasks | Low | 10-20% faster | P5 |
| Throttle Drag | Low | Smoother panning | P6 |

**Combined Expected Improvement**: 3-5x faster overall performance

---

## Quick Wins (Can Implement Now)

1. **Change LANCZOS → BILINEAR** (1 line change, 60% faster)
2. **Remove update_idletasks()** (Delete lines, 10-20% faster)  
3. **Throttle drag events** (5 lines, smoother panning)

These three alone should dramatically improve responsiveness!

