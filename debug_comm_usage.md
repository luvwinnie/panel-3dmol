# Panel Communication Debugging Guide

This debugging enhancement helps identify the root cause of "Comm received message that could not be deserialized" warnings in Google Colab and other Jupyter environments.

## How to Enable Debugging

Set the environment variable `PANEL_DEBUG_COMM=true` before running your Panel application:

### In Python code:
```python
import os
os.environ['PANEL_DEBUG_COMM'] = 'true'

# Then import and use your panel_3dmol viewer
from panel_3dmol.viewer import Mol3DViewer
viewer = Mol3DViewer()
# ... use the viewer
```

### In Jupyter/Colab cell:
```python
%env PANEL_DEBUG_COMM=true

# Then run your panel code
import panel_3dmol.viewer as p3d
viewer = p3d.view()
# ... use the viewer
```

### In terminal/command line:
```bash
export PANEL_DEBUG_COMM=true
python your_script.py
```

## What the Debug Output Shows

When enabled, you'll see detailed debug information with 🔍 and ❌ emojis:

### Normal Message Processing:
```
🔍 PANEL_DEBUG_COMM: JupyterCommJSBinary.decode called
🔍 PANEL_DEBUG_COMM: Message type=<class 'dict'>
🔍 PANEL_DEBUG_COMM: _on_msg called with ref=1234-5678-abcd
🔍 PANEL_DEBUG_COMM: Patch assembled successfully
✅ PANEL_DEBUG_COMM: Patch applied successfully
```

### When Errors Occur:
```
❌ PANEL_DEBUG_COMM: DeserializationError occurred!
❌ PANEL_DEBUG_COMM: Error details: Cannot decode message with missing field 'data'
❌ PANEL_DEBUG_COMM: Original message content: {...}
❌ PANEL_DEBUG_COMM: Manager state: {...}
```

## Key Information to Look For

1. **Message Structure**: Check if incoming messages have expected fields like 'content', 'data', 'buffers'
2. **Patch Assembly**: Look for errors during the patch assembly phase
3. **Event Types**: See what types of events are being processed
4. **Manager State**: Examine the communication manager's internal state when errors occur

## Common Issues and Solutions

### Version Compatibility
If you see decoding errors, check your package versions:
```python
import comm, jupyter_bokeh, panel
print(f"comm: {comm.__version__}")
print(f"jupyter_bokeh: {jupyter_bokeh.__version__}")
print(f"panel: {panel.__version__}")
```

Recommended versions for Google Colab:
- comm==0.1.4
- jupyter_bokeh==3.0.7
- panel==1.3.8 (stable release)

### Too Many Messages
If you see rapid message streams, consider reducing update frequency:
```python
# Reduce animation speed to decrease message frequency
viewer.animation_speed = 500  # Slower = fewer messages
```

## Debugging Environment Variables

The system responds to these values for `PANEL_DEBUG_COMM`:
- `true`, `1`, `yes`, `on` (case insensitive) → Enable debugging
- Any other value → Disable debugging

## Turning Off Debugging

To disable debugging:
```python
import os
os.environ['PANEL_DEBUG_COMM'] = 'false'
# or
del os.environ['PANEL_DEBUG_COMM']
```

## Additional Debugging

For even more detailed Bokeh debugging, also set:
```python
os.environ['BOKEH_LOG_LEVEL'] = 'debug'
```

This will provide additional context about the underlying Bokeh communication system.