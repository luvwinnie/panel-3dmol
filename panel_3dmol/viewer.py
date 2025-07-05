import panel as pn
import param
from panel.reactive import ReactiveHTML

class Mol3DViewer(ReactiveHTML):
    """
    A Panel component for 3D molecular visualization using 3Dmol.js.
    """
    
    # Core parameters
    structure = param.String(default="", doc="Molecular structure data")
    filetype = param.String(default="xyz", doc="File type (xyz, mol, pdb, sdf, etc.)")
    background_color = param.String(default="white", doc="Background color")
    
    # Style parameters for py3dmol compatibility
    show_stick = param.Boolean(default=True, doc="Show stick representation")
    show_sphere = param.Boolean(default=True, doc="Show sphere representation")  
    show_cartoon = param.Boolean(default=False, doc="Show cartoon representation")
    show_surface = param.Boolean(default=False, doc="Show surface representation")
    show_line = param.Boolean(default=False, doc="Show line representation")
    
    # Label parameters
    labels = param.List(default=[], doc="List of labels to display")
    show_atom_labels = param.Boolean(default=False, doc="Automatically show atom indices")
    
    # Animation parameters
    current_frame = param.Integer(default=0, bounds=(0, None), doc="Current animation frame")
    total_frames = param.Integer(default=1, bounds=(1, None), doc="Total number of frames")
    animate = param.Boolean(default=False, doc="Enable/disable animation")
    animation_speed = param.Number(default=100, bounds=(1, 10000), doc="Animation speed in milliseconds")
    
    
    # HTML template (simplified - no multiple template variables)
    _template = """
    <div id="viewer" style="width: 100%; height: 400px; border: 1px solid #ddd;"></div>
    <div id="frame-debug" style="font-size: 12px; color: blue; padding: 2px;">
        Frame: <span id="current-frame">0</span> / <span id="total-frames">1</span>
    </div>
    """
    
    # JavaScript for 3Dmol.js integration (correct Panel ReactiveHTML syntax)
    _scripts = {
        "render": """
            const viewerDiv = viewer;
            
            // Check if 3Dmol.js is loaded
            if (typeof $3Dmol === 'undefined') {
                console.error('🧬 RENDER: 3Dmol.js is not loaded yet, retrying in 100ms...');
                setTimeout(() => {
                    if (typeof $3Dmol !== 'undefined') {
                        console.log('🧬 RENDER: 3Dmol.js loaded on retry');
                        // Retry the render
                        state.viewer = $3Dmol.createViewer(viewerDiv, {backgroundColor: data.background_color || "white"});
                        // ... rest of render logic would go here
                    } else {
                        console.error('🧬 RENDER: 3Dmol.js still not loaded after retry');
                    }
                }, 100);
                return;
            }
            
            state.viewer = $3Dmol.createViewer(viewerDiv, {backgroundColor: data.background_color || "white"});
            console.log('🧬 RENDER: 3Dmol viewer created:', !!state.viewer);
            
            if (data.structure) {
                console.log('🧬 RENDER: Loading structure with', data.total_frames, 'frames');
                console.log('🧬 RENDER: Structure length:', data.structure.length, 'characters');
                
                // Check if this is multi-frame data
                if (data.total_frames > 1) {
                    console.log('🧬 RENDER: Using addModelsAsFrames for multi-frame structure');
                    try {
                        // Use addModelsAsFrames for multi-frame structures
                        state.viewer.addModelsAsFrames(data.structure, data.filetype);
                        console.log('🧬 RENDER: addModelsAsFrames completed successfully');
                    } catch (err) {
                        console.error('🧬 RENDER: Error in addModelsAsFrames:', err);
                        console.log('🧬 RENDER: Falling back to single model...');
                        state.viewer.addModel(data.structure, data.filetype);
                    }
                } else {
                    console.log('🧬 RENDER: Using addModel for single frame');
                    // Single frame - use regular addModel
                    state.viewer.addModel(data.structure, data.filetype);
                }
                state.viewer.setStyle({}, {stick:{radius: 0.15}, sphere:{radius: 0.3}});
                state.viewer.zoomTo();
                state.viewer.render();
                
                // Debug: Check loaded models
                try {
                    if (typeof state.viewer.getModels === 'function') {
                        const models = state.viewer.getModels();
                        console.log('🧬 RENDER: Models loaded after render:', models.length);
                        if (models.length > 0 && data.total_frames > 1) {
                            console.log('🧬 RENDER: Model has frames:', models[0].getFrames ? models[0].getFrames() : 'No getFrames method');
                            // Try to get frame count if available
                            try {
                                if (typeof models[0].getFrames === 'function') {
                                    const frameCount = models[0].getFrames();
                                    console.log('🧬 RENDER: Actual frame count from model:', frameCount);
                                }
                            } catch (e) {
                                console.log('🧬 RENDER: Cannot get frame count:', e.message);
                            }
                        }
                    } else {
                        console.log('🧬 RENDER: getModels method not available on viewer');
                    }
                } catch (e) {
                    console.error('🧬 RENDER: Error checking models:', e.message);
                }
            }
        """,
        
        "structure": """
            if (state.viewer) {
                state.viewer.clear();
                if (data.structure) {
                    console.log('🧬 Updating structure with', data.total_frames, 'frames');
                    console.log('🧬 Structure length:', data.structure.length, 'characters');
                    
                    // Check if this is multi-frame data
                    if (data.total_frames > 1) {
                        console.log('🧬 Using addModelsAsFrames for multi-frame structure update');
                        try {
                            // Use addModelsAsFrames for multi-frame structures
                            state.viewer.addModelsAsFrames(data.structure, data.filetype);
                            console.log('🧬 addModelsAsFrames completed successfully');
                        } catch (err) {
                            console.error('🧬 Error in addModelsAsFrames:', err);
                            console.log('🧬 Falling back to single model...');
                            state.viewer.addModel(data.structure, data.filetype);
                        }
                    } else {
                        console.log('🧬 Using addModel for single frame update');
                        // Single frame - use regular addModel
                        state.viewer.addModel(data.structure, data.filetype);
                    }
                    
                    // Build style based on current parameters
                    const style = {};
                    if (data.show_stick) style.stick = {radius: 0.15};
                    if (data.show_sphere) style.sphere = {radius: 0.3};
                    if (data.show_cartoon) style.cartoon = {};
                    if (data.show_line) style.line = {};
                    if (data.show_surface) style.surface = {};
                    
                    // Default to stick+sphere if nothing selected
                    if (Object.keys(style).length === 0) {
                        style.stick = {radius: 0.15};
                        style.sphere = {radius: 0.3};
                    }
                    
                    state.viewer.setStyle({}, style);
                    state.viewer.zoomTo();
                    
                    // Debug: Check loaded models after structure update
                    try {
                        if (typeof state.viewer.getModels === 'function') {
                            const models = state.viewer.getModels();
                            console.log('🧬 Models loaded after structure update:', models.length);
                            if (models.length > 0 && data.total_frames > 1) {
                                console.log('🧬 Model frames after update:', models[0].getFrames ? models[0].getFrames() : 'No getFrames method');
                                // Try to get frame count if available
                                try {
                                    if (typeof models[0].getFrames === 'function') {
                                        const frameCount = models[0].getFrames();
                                        console.log('🧬 Actual frame count from model:', frameCount);
                                    }
                                } catch (e) {
                                    console.log('🧬 Cannot get frame count:', e.message);
                                }
                            }
                        } else {
                            console.log('🧬 getModels method not available on viewer');
                        }
                    } catch (e) {
                        console.error('🧬 Error checking models:', e.message);
                    }
                    
                    // Handle labels after structure is loaded
                    state.viewer.removeAllLabels();
                    
                    // Add atom labels if enabled
                    if (data.show_atom_labels) {
                        const lines = data.structure.trim().split('\\n');
                        if (data.filetype === 'xyz' && lines.length > 2) {
                            const natoms = parseInt(lines[0]);
                            const atomLines = lines.slice(2, 2 + natoms);
                            
                            atomLines.forEach((line, idx) => {
                                const parts = line.trim().split(/\\s+/);
                                if (parts.length >= 4) {
                                    const x = parseFloat(parts[1]);
                                    const y = parseFloat(parts[2]);
                                    const z = parseFloat(parts[3]);
                                    
                                    state.viewer.addLabel(String(idx + 1), {
                                        position: {x: x, y: y, z: z},
                                        backgroundColor: 'white',
                                        backgroundOpacity: 0,
                                        fontColor: 'blue',
                                        font: 'arial',
                                        fontSize: 16,
                                        fontOpacity: 1.0,
                                        inFront: true
                                    });
                                }
                            });
                        } else if (data.filetype === 'pdb') {
                            const atomLines = lines.filter(line => line.startsWith('ATOM') || line.startsWith('HETATM'));
                            
                            atomLines.forEach((line, idx) => {
                                const x = parseFloat(line.substring(30, 38).trim());
                                const y = parseFloat(line.substring(38, 46).trim());
                                const z = parseFloat(line.substring(46, 54).trim());
                                
                                state.viewer.addLabel(String(idx + 1), {
                                    position: {x: x, y: y, z: z},
                                    backgroundColor: 'white',
                                    backgroundOpacity: 0,
                                    fontColor: 'blue',
                                    font: 'arial',
                                    fontSize: 16,
                                    fontOpacity: 1.0,
                                    inFront: true
                                });
                            });
                        }
                    }
                    
                    // Add custom labels
                    if (data.labels && Array.isArray(data.labels)) {
                        data.labels.forEach(label => {
                            state.viewer.addLabel(label.text, label.options || {});
                        });
                    }
                    
                    state.viewer.render();
                }
            }
        """,
        
        "filetype": """
            if (state.viewer && data.structure) {
                state.viewer.clear();
                state.viewer.addModel(data.structure, data.filetype);
                
                // Apply current style
                const style = {};
                if (data.show_stick) style.stick = {radius: 0.15};
                if (data.show_sphere) style.sphere = {radius: 0.3};
                if (data.show_cartoon) style.cartoon = {};
                if (data.show_line) style.line = {};
                if (data.show_surface) style.surface = {};
                
                if (Object.keys(style).length === 0) {
                    style.stick = {radius: 0.15};
                    style.sphere = {radius: 0.3};
                }
                
                state.viewer.setStyle({}, style);
                state.viewer.zoomTo();
                state.viewer.render();
            }
        """,
        
        "background_color": """
            if (state.viewer) {
                state.viewer.setBackgroundColor(data.background_color || "white");
                state.viewer.render();
            }
        """,
        
        "show_stick": """
            if (state.viewer && data.structure) {
                const style = {};
                if (data.show_stick) style.stick = {radius: 0.15};
                if (data.show_sphere) style.sphere = {radius: 0.3};
                if (data.show_cartoon) style.cartoon = {};
                if (data.show_line) style.line = {};
                if (data.show_surface) style.surface = {};
                
                if (Object.keys(style).length === 0) {
                    style.stick = {radius: 0.15};
                    style.sphere = {radius: 0.3};
                }
                
                state.viewer.setStyle({}, style);
                state.viewer.render();
            }
        """,
        
        "show_sphere": """
            if (state.viewer && data.structure) {
                const style = {};
                if (data.show_stick) style.stick = {radius: 0.15};
                if (data.show_sphere) style.sphere = {radius: 0.3};
                if (data.show_cartoon) style.cartoon = {};
                if (data.show_line) style.line = {};
                if (data.show_surface) style.surface = {};
                
                if (Object.keys(style).length === 0) {
                    style.stick = {radius: 0.15};
                    style.sphere = {radius: 0.3};
                }
                
                state.viewer.setStyle({}, style);
                state.viewer.render();
            }
        """,
        
        "show_cartoon": """
            if (state.viewer && data.structure) {
                const style = {};
                if (data.show_stick) style.stick = {radius: 0.15};
                if (data.show_sphere) style.sphere = {radius: 0.3};
                if (data.show_cartoon) style.cartoon = {};
                if (data.show_line) style.line = {};
                if (data.show_surface) style.surface = {};
                
                if (Object.keys(style).length === 0) {
                    style.stick = {radius: 0.15};
                    style.sphere = {radius: 0.3};
                }
                
                state.viewer.setStyle({}, style);
                state.viewer.render();
            }
        """,
        
        "show_line": """
            if (state.viewer && data.structure) {
                const style = {};
                if (data.show_stick) style.stick = {radius: 0.15};
                if (data.show_sphere) style.sphere = {radius: 0.3};
                if (data.show_cartoon) style.cartoon = {};
                if (data.show_line) style.line = {};
                if (data.show_surface) style.surface = {};
                
                if (Object.keys(style).length === 0) {
                    style.stick = {radius: 0.15};
                    style.sphere = {radius: 0.3};
                }
                
                state.viewer.setStyle({}, style);
                state.viewer.render();
            }
        """,
        
        "show_surface": """
            if (state.viewer && data.structure) {
                const style = {};
                if (data.show_stick) style.stick = {radius: 0.15};
                if (data.show_sphere) style.sphere = {radius: 0.3};
                if (data.show_cartoon) style.cartoon = {};
                if (data.show_line) style.line = {};
                if (data.show_surface) style.surface = {};
                
                if (Object.keys(style).length === 0) {
                    style.stick = {radius: 0.15};
                    style.sphere = {radius: 0.3};
                }
                
                state.viewer.setStyle({}, style);
                state.viewer.render();
            }
        """,
        
        "labels": """
            if (state.viewer) {
                // Clear existing labels
                state.viewer.removeAllLabels();
                
                // Add custom labels
                if (data.labels && Array.isArray(data.labels)) {
                    data.labels.forEach(label => {
                        state.viewer.addLabel(label.text, label.options || {});
                    });
                }
                
                state.viewer.render();
            }
        """,
        
        "show_atom_labels": """
            if (state.viewer && data.structure) {
                // Clear existing labels
                state.viewer.removeAllLabels();
                
                // Add atom labels if enabled
                if (data.show_atom_labels) {
                    const lines = data.structure.trim().split('\\n');
                    
                    if (data.filetype === 'xyz' && lines.length > 2) {
                        const natoms = parseInt(lines[0]);
                        const atomLines = lines.slice(2, 2 + natoms);
                        
                        atomLines.forEach((line, idx) => {
                            const parts = line.trim().split(/\\s+/);
                            if (parts.length >= 4) {
                                const x = parseFloat(parts[1]);
                                const y = parseFloat(parts[2]);
                                const z = parseFloat(parts[3]);
                                
                                state.viewer.addLabel(String(idx + 1), {
                                    position: {x: x, y: y, z: z},
                                    backgroundColor: 'white',
                                    backgroundOpacity: 0,
                                    fontColor: 'blue',
                                    font: 'arial',
                                    fontSize: 16,
                                    fontOpacity: 1.0,
                                    inFront: true
                                });
                            }
                        });
                    } else if (data.filetype === 'pdb') {
                        const atomLines = lines.filter(line => line.startsWith('ATOM') || line.startsWith('HETATM'));
                        
                        atomLines.forEach((line, idx) => {
                            const x = parseFloat(line.substring(30, 38).trim());
                            const y = parseFloat(line.substring(38, 46).trim());
                            const z = parseFloat(line.substring(46, 54).trim());
                            
                            state.viewer.addLabel(String(idx + 1), {
                                position: {x: x, y: y, z: z},
                                backgroundColor: 'white',
                                backgroundOpacity: 0,
                                fontColor: 'blue',
                                font: 'arial',
                                fontSize: 16,
                                fontOpacity: 1.0,
                                inFront: true
                            });
                        });
                    }
                }
                
                // Re-add custom labels
                if (data.labels && Array.isArray(data.labels)) {
                    data.labels.forEach(label => {
                        state.viewer.addLabel(label.text, label.options || {});
                    });
                }
                
                state.viewer.render();
            }
        """,
        
        "current_frame": """
            // Update the frame display elements
            const currentFrameSpan = document.getElementById('current-frame');
            const totalFramesSpan = document.getElementById('total-frames');
            if (currentFrameSpan) {
                currentFrameSpan.textContent = data.current_frame;
            }
            if (totalFramesSpan) {
                totalFramesSpan.textContent = data.total_frames;
            }
            
            if (state.viewer) {
                try {
                    if (typeof state.viewer.setFrame === 'function') {
                        state.viewer.setFrame(data.current_frame);
                        
                        if (typeof state.viewer.render === 'function') {
                            state.viewer.render();
                        }
                    }
                } catch (err) {
                    // Try fallback render
                    try {
                        if (state.viewer.render) {
                            state.viewer.render();
                        }
                    } catch (renderErr) {
                        console.error('Frame update failed:', renderErr);
                    }
                }
            }
        """,
        
        "animate": """
            if (state.viewer && data.total_frames > 1) {
                if (data.animate) {
                    // Use 3Dmol.js built-in animate method
                    try {
                        const animateOptions = {
                            loop: 'forward',
                            interval: data.animation_speed || 200,
                            reps: 0  // Infinite loop
                        };
                        
                        state.viewer.animate(animateOptions);
                        state.animating = true;
                        
                        // Start frame sync polling to update Python parameters
                        state.sync_interval = setInterval(() => {
                            if (state.viewer && state.animating) {
                                try {
                                    if (typeof state.viewer.getFrame === 'function') {
                                        const currentFrame = state.viewer.getFrame();
                                        if (data.current_frame !== currentFrame) {
                                            data.current_frame = currentFrame;
                                        }
                                    }
                                } catch (err) {
                                    // Frame sync errors are expected during transitions
                                }
                            }
                        }, Math.min(data.animation_speed / 2, 100));
                        
                    } catch (err) {
                        console.error('Error starting 3Dmol.js animation:', err);
                    }
                } else {
                    // Stop frame sync polling
                    if (state.sync_interval) {
                        clearInterval(state.sync_interval);
                        state.sync_interval = null;
                    }
                    
                    // Stop 3Dmol.js animation
                    try {
                        if (state.viewer.stopAnimate) {
                            state.viewer.stopAnimate();
                        }
                        if (state.viewer.pauseAnimate) {
                            state.viewer.pauseAnimate();
                        }
                        state.animating = false;
                    } catch (err) {
                        console.error('Error stopping 3Dmol.js animation:', err);
                    }
                }
            }
        """,
        
        "animation_speed": """
            if (state.viewer && state.animating) {
                // Restart frame sync with new speed
                if (state.sync_interval) {
                    clearInterval(state.sync_interval);
                    state.sync_interval = null;
                }
                
                // Restart animation with new speed
                try {
                    if (state.viewer.stopAnimate) {
                        state.viewer.stopAnimate();
                    }
                    
                    const animateOptions = {
                        loop: 'forward',
                        interval: data.animation_speed,
                        reps: 0
                    };
                    
                    state.viewer.animate(animateOptions);
                    
                    // Restart frame sync with new speed
                    state.sync_interval = setInterval(() => {
                        if (state.viewer && state.animating) {
                            try {
                                if (typeof state.viewer.getFrame === 'function') {
                                    const currentFrame = state.viewer.getFrame();
                                    if (data.current_frame !== currentFrame) {
                                        data.current_frame = currentFrame;
                                    }
                                }
                            } catch (err) {
                                // Frame sync errors are expected during transitions
                            }
                        }
                    }, Math.min(data.animation_speed / 2, 100));
                    
                } catch (err) {
                    console.error('Error updating animation speed:', err);
                }
            }
        """,
        
        "total_frames": """
            // Update the total frames display
            const totalFramesSpan = document.getElementById('total-frames');
            if (totalFramesSpan) {
                totalFramesSpan.textContent = data.total_frames;
            }
            
            if (state.viewer) {
                // Update frame bounds when total frames changes
                if (data.current_frame >= data.total_frames) {
                    // Reset to first frame if current frame is out of bounds
                    state.viewer.setFrame(0);
                    state.viewer.render();
                }
            }
        """
    }
    
    # JavaScript dependencies
    __javascript__ = [
        "https://3dmol.org/build/3Dmol.js"
    ]
    
    def __init__(self, **params):
        super().__init__(**params)
        self._labels_list = []  # Internal storage for labels
        self._updating_frame = False  # Flag to prevent feedback loops
        self._frame_structures = []  # Storage for frame structures
        
    
    # py3dmol-compatible API methods
    def addModel(self, data, format):
        """Add a molecular model to the viewer (py3dmol compatible)"""
        self.structure = data
        self.filetype = format
        return self
    
    def setStyle(self, selection={}, style={}):
        """Set molecular style (py3dmol compatible)"""
        self.show_stick = False
        self.show_sphere = False
        self.show_cartoon = False
        self.show_line = False
        self.show_surface = False
        
        if 'stick' in style:
            self.show_stick = True
        if 'sphere' in style:
            self.show_sphere = True
        if 'cartoon' in style:
            self.show_cartoon = True
        if 'line' in style:
            self.show_line = True
        if 'surface' in style:
            self.show_surface = True
            
        if not any([self.show_stick, self.show_sphere, self.show_cartoon, 
                   self.show_line, self.show_surface]):
            self.show_stick = True
            self.show_sphere = True
            
        return self
    
    def setBackgroundColor(self, color):
        """Set background color (py3dmol compatible)"""
        self.background_color = color
        return self
    
    def render(self):
        """Force render update (py3dmol compatible)"""
        self.param.trigger('structure')
        return self
    
    def clear(self):
        """Clear all models (py3dmol compatible)"""
        self.structure = ""
        return self
    
    def center(self):
        """Center/zoom to molecule (py3dmol compatible)"""
        self.param.trigger('structure')
        return self
    
    def addLabel(self, text, options=None):
        """Add a label to the viewer (py3dmol compatible)"""
        if options is None:
            options = {}
        
        label = {
            'text': text,
            'options': options
        }
        
        self._labels_list.append(label)
        self.labels = self._labels_list.copy()  # Trigger reactivity
        return self
    
    def removeAllLabels(self):
        """Remove all labels from the viewer (py3dmol compatible)"""
        self._labels_list = []
        self.labels = []
        return self
    
    def showAtomLabels(self, show=True):
        """Show/hide automatic atom index labels"""
        self.show_atom_labels = show
        return self
    
    def autoLabel(self):
        """Automatically add atom index labels based on structure"""
        if not self.structure:
            return self
            
        lines = self.structure.strip().split('\n')
        
        if self.filetype == 'xyz' and len(lines) > 2:
            natoms = int(lines[0])
            atom_lines = lines[2:2 + natoms]
            
            for idx, line in enumerate(atom_lines):
                parts = line.split()
                if len(parts) >= 4:
                    x, y, z = map(float, parts[1:4])
                    self.addLabel(str(idx + 1), {
                        'position': {'x': x, 'y': y, 'z': z},
                        'backgroundColor': 'white',
                        'backgroundOpacity': 0,
                        'fontColor': 'blue',
                        'font': 'arial',
                        'fontSize': 16,
                        'fontOpacity': 1.0,
                        'inFront': True
                    })
        
        elif self.filetype == 'pdb':
            atom_lines = [line for line in lines if line.startswith(('ATOM', 'HETATM'))]
            
            for idx, line in enumerate(atom_lines):
                if len(line) >= 54:
                    x = float(line[30:38].strip())
                    y = float(line[38:46].strip()) 
                    z = float(line[46:54].strip())
                    self.addLabel(str(idx + 1), {
                        'position': {'x': x, 'y': y, 'z': z},
                        'backgroundColor': 'white',
                        'backgroundOpacity': 0,
                        'fontColor': 'blue',
                        'font': 'arial',
                        'fontSize': 16,
                        'fontOpacity': 1.0,
                        'inFront': True
                    })
        
        return self
    
    def setFrame(self, frame):
        """Set the current animation frame (py3dmol compatible)"""
        if 0 <= frame < self.total_frames:
            self._updating_frame = True
            self.current_frame = frame
            self._updating_frame = False
        return self
    
    def getFrame(self):
        """Get the current animation frame (py3dmol compatible)"""
        return self.current_frame
    
    def startAnimation(self, speed=None, loop_mode="forward"):
        """Start 3Dmol.js native animation (py3dmol compatible)"""
        if speed is not None:
            self.animation_speed = speed
        self.animate = True
        return self
    
    def stopAnimation(self):
        """Stop animation playback (py3dmol compatible)"""
        self.animate = False
        return self
    
    def stopAnimationImmediate(self):
        """Stop animation immediately and force cleanup (Python instant stop)"""
        self.animate = False
        self.param.trigger('animate')  # Force immediate JavaScript execution
        return self
    
    def setAnimationSpeed(self, speed):
        """Set animation speed in milliseconds (py3dmol compatible)"""
        self.animation_speed = speed
        return self
    
    def addFrames(self, structures, filetype=None):
        """Add multiple structures as animation frames"""
        if filetype is None:
            filetype = self.filetype
            
        if isinstance(structures, list):
            # Multiple structures - create multi-frame content
            if filetype == 'xyz':
                # For 3Dmol.js addModelsAsFrames, we need to create a proper multi-frame XYZ format
                # Each frame should be separated without extra newlines between frames
                combined_frames = []
                for structure in structures:
                    combined_frames.append(structure.strip())
                self.structure = "\n".join(combined_frames)
            else:
                # For other formats, just use the first structure for now
                # TODO: Implement proper multi-frame support for PDB/SDF
                self.structure = structures[0] if structures else ""
            
            self.total_frames = len(structures)
            self.current_frame = 0
            # Store the structures for proper 3Dmol.js handling
            self._frame_structures = structures
        else:
            # Single structure
            self.structure = structures
            self.total_frames = 1
            self.current_frame = 0
            self._frame_structures = [structures]
            
        return self

# Factory function for easier usage (py3dmol compatible)
def view(width=600, height=400, **kwargs):
    """Create a 3Dmol.js viewer for Panel applications (py3dmol compatible)"""
    viewer = Mol3DViewer(**kwargs)
    if 'sizing_mode' not in kwargs:
        viewer.width = width
        viewer.height = height
    return viewer

# Make components available for import
__all__ = ['Mol3DViewer', 'view']