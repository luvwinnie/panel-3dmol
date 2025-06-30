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
    
    
    # HTML template (simple and supports multiple instances)
    _template = """
    <div id="viewer" style="width: 100%; height: 400px; border: 1px solid #ddd;"></div>
    """
    
    # JavaScript for 3Dmol.js integration (simple working pattern)
    _scripts = {
        "render": """
            const viewerDiv = viewer;
            state.viewer = $3Dmol.createViewer(viewerDiv, {backgroundColor: data.background_color || "white"});
            if (data.structure) {
                console.log('Loading structure with', data.total_frames, 'frames');
                // Check if this is multi-frame data
                if (data.total_frames > 1) {
                    console.log('Using addModelsAsFrames for multi-frame structure');
                    // Use addModelsAsFrames for multi-frame structures
                    state.viewer.addModelsAsFrames(data.structure, data.filetype);
                } else {
                    console.log('Using addModel for single frame');
                    // Single frame - use regular addModel
                    state.viewer.addModel(data.structure, data.filetype);
                }
                state.viewer.setStyle({}, {stick:{radius: 0.15}, sphere:{radius: 0.3}});
                state.viewer.zoomTo();
                state.viewer.render();
                
                // Debug: Check loaded models
                const models = state.viewer.getModels();
                console.log('Models loaded after render:', models.length);
                if (models.length > 0 && data.total_frames > 1) {
                    console.log('Model has frames:', models[0].getFrames ? models[0].getFrames() : 'No getFrames method');
                }
            }
        """,
        
        "structure": """
            if (state.viewer) {
                state.viewer.clear();
                if (data.structure) {
                    console.log('Updating structure with', data.total_frames, 'frames');
                    // Check if this is multi-frame data
                    if (data.total_frames > 1) {
                        console.log('Using addModelsAsFrames for multi-frame structure update');
                        // Use addModelsAsFrames for multi-frame structures
                        state.viewer.addModelsAsFrames(data.structure, data.filetype);
                    } else {
                        console.log('Using addModel for single frame update');
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
                    const models = state.viewer.getModels();
                    console.log('Models loaded after structure update:', models.length);
                    if (models.length > 0 && data.total_frames > 1) {
                        console.log('Model frames after update:', models[0].getFrames ? models[0].getFrames() : 'No getFrames method');
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
            if (state.viewer && data.total_frames > 1) {
                console.log('Setting frame to:', data.current_frame, 'of', data.total_frames);
                // Check if we have models loaded
                const models = state.viewer.getModels();
                console.log('Number of models loaded:', models.length);
                if (models.length > 0) {
                    console.log('Model frames available:', models[0].getFrames ? models[0].getFrames() : 'getFrames not available');
                }
                
                // Use 3Dmol.js setFrame method for multi-frame structures
                state.viewer.setFrame(data.current_frame).then(() => {
                    state.viewer.render();
                    console.log('Frame set and rendered:', data.current_frame);
                }).catch(err => {
                    console.error('Error setting frame:', err);
                    console.log('Trying fallback render...');
                    state.viewer.render();
                });
            }
        """,
        
        "animate": """
            if (state.viewer && data.total_frames > 1) {
                if (data.animate) {
                    console.log('Animation enabled - using Panel-controlled animation');
                    // Panel controls the animation, we just need to be ready
                    // The actual frame updates come through current_frame parameter
                } else {
                    console.log('Animation disabled');
                }
            }
        """,
        
        "animation_speed": """
            if (state.viewer) {
                console.log('Animation speed changed to:', data.animation_speed, 'ms');
                // Panel controls the animation speed, no action needed here
            }
        """,
        
        "total_frames": """
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
    
    def startAnimation(self, speed=None):
        """Start animation playback (py3dmol compatible)"""
        if speed is not None:
            self.animation_speed = speed
        self.animate = True
        return self
    
    def stopAnimation(self):
        """Stop animation playback (py3dmol compatible)"""
        self.animate = False
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