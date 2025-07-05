import panel as pn
import param
from panel.reactive import ReactiveHTML
import re
import io
import warnings

# Optional imports for molecular file parsing
try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors
    HAS_RDKIT = True
except ImportError:
    HAS_RDKIT = False

try:
    from openbabel import openbabel
    HAS_OPENBABEL = True
except ImportError:
    HAS_OPENBABEL = False

try:
    import cclib
    HAS_CCLIB = True
except ImportError:
    HAS_CCLIB = False

try:
    from ase import io as ase_io
    HAS_ASE = True
except ImportError:
    HAS_ASE = False

class Mol3DViewer(ReactiveHTML):
    """
    A Panel component for 3D molecular visualization using 3Dmol.js.
    """
    
    # Core parameters
    structure = param.String(default="", doc="Molecular structure data")
    filetype = param.String(default="xyz", doc="File type (xyz, mol, pdb, sdf, com, gjf)")
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
    animate_options = param.Dict(default={}, doc="Custom 3Dmol.js animation options")
    
    # Internal parameters for parsed data
    parsed_atoms = param.List(default=[], doc="Parsed atom coordinates for labeling")
    
    
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
                console.log('🧬 RENDER: Original filetype:', data.filetype);
                
                // Convert structure to 3Dmol.js compatible format if needed
                let processedStructure = data.structure;
                let processedFiletype = data.filetype;
                
                // Check if this is multi-frame data
                if (data.total_frames > 1) {
                    console.log('🧬 RENDER: Using addModelsAsFrames for multi-frame structure');
                    try {
                        // Use addModelsAsFrames for multi-frame structures
                        state.viewer.addModelsAsFrames(processedStructure, processedFiletype);
                        console.log('🧬 RENDER: addModelsAsFrames completed successfully');
                    } catch (err) {
                        console.error('🧬 RENDER: Error in addModelsAsFrames:', err);
                        console.log('🧬 RENDER: Falling back to single model...');
                        state.viewer.addModel(processedStructure, processedFiletype);
                    }
                } else {
                    console.log('🧬 RENDER: Using addModel for single frame');
                    // Single frame - use regular addModel
                    state.viewer.addModel(processedStructure, processedFiletype);
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
                    
                    // Add atom labels if enabled using Python-parsed coordinates
                    if (data.show_atom_labels && data.parsed_atoms) {
                        data.parsed_atoms.forEach((atom, idx) => {
                            const [element, x, y, z] = atom;
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
                
                // Add atom labels if enabled using Python-parsed coordinates
                if (data.show_atom_labels && data.parsed_atoms) {
                    data.parsed_atoms.forEach((atom, idx) => {
                        const [element, x, y, z] = atom;
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
                    // Use 3Dmol.js built-in animate method with custom options support
                    try {
                        // Merge custom animate_options with defaults
                        const defaultOptions = {
                            loop: 'forward',
                            interval: data.animation_speed || 200,
                            reps: 0  // Infinite loop
                        };
                        
                        const animateOptions = Object.assign({}, defaultOptions, data.animate_options || {});
                        console.log('🎬 Starting animation with options:', animateOptions);
                        
                        state.viewer.animate(animateOptions);
                        state.animating = true;
                        
                        // Reduced frequency frame sync to minimize comm overhead but maintain sync
                        let lastSyncTime = 0;
                        const SYNC_THROTTLE = 200; // Sync every 200ms max to reduce messages
                        
                        state.sync_interval = setInterval(() => {
                            if (state.viewer && state.animating) {
                                const now = Date.now();
                                if ((now - lastSyncTime) >= SYNC_THROTTLE) {
                                    try {
                                        if (typeof state.viewer.getFrame === 'function') {
                                            const currentFrame = state.viewer.getFrame();
                                            if (data.current_frame !== currentFrame) {
                                                data.current_frame = currentFrame;
                                                lastSyncTime = now;
                                            }
                                        }
                                    } catch (err) {
                                        // Silently handle frame sync errors
                                    }
                                }
                            }
                        }, SYNC_THROTTLE);
                        
                    } catch (err) {
                        console.error('Error starting 3Dmol.js animation:', err);
                    }
                } else {
                    // Stop frame sync polling
                    if (state.sync_interval) {
                        clearInterval(state.sync_interval);
                        state.sync_interval = null;
                    }
                    
                    // Stop 3Dmol.js animation immediately
                    try {
                        if (state.viewer.stopAnimate) {
                            state.viewer.stopAnimate();
                        }
                        if (state.viewer.pauseAnimate) {
                            state.viewer.pauseAnimate();
                        }
                        state.animating = false;
                        console.log('⏹️ Animation stopped');
                    } catch (err) {
                        console.error('Error stopping 3Dmol.js animation:', err);
                    }
                }
            }
        """,
        
        "animation_speed": """
            // Always respond to animation speed changes, whether animating or not
            console.log('🎚️ Animation speed changed to:', data.animation_speed, 'ms');
            
            if (state.viewer && data.total_frames > 1) {
                // If currently animating, restart with new speed
                if (state.animating) {
                    console.log('🔄 Restarting animation with new speed...');
                    
                    // Stop current animation and sync
                    if (state.sync_interval) {
                        clearInterval(state.sync_interval);
                        state.sync_interval = null;
                    }
                    
                    try {
                        if (state.viewer.stopAnimate) {
                            state.viewer.stopAnimate();
                        }
                        
                        // Use custom options if available, otherwise defaults
                        const defaultOptions = {
                            loop: 'forward',
                            interval: data.animation_speed,
                            reps: 0
                        };
                        
                        const animateOptions = Object.assign({}, defaultOptions, data.animate_options || {});
                        
                        // Restart animation with new speed
                        state.viewer.animate(animateOptions);
                        
                        // Restart throttled frame sync
                        let lastSyncTime = 0;
                        const SYNC_THROTTLE = 200;
                        
                        state.sync_interval = setInterval(() => {
                            if (state.viewer && state.animating) {
                                const now = Date.now();
                                if ((now - lastSyncTime) >= SYNC_THROTTLE) {
                                    try {
                                        if (typeof state.viewer.getFrame === 'function') {
                                            const currentFrame = state.viewer.getFrame();
                                            if (data.current_frame !== currentFrame) {
                                                data.current_frame = currentFrame;
                                                lastSyncTime = now;
                                            }
                                        }
                                    } catch (err) {
                                        // Silently handle sync errors
                                    }
                                }
                            }
                        }, SYNC_THROTTLE);
                        
                        console.log('✅ Animation restarted with speed:', data.animation_speed, 'ms');
                        
                    } catch (err) {
                        console.error('Error updating animation speed:', err);
                    }
                } else {
                    console.log('📝 Animation speed updated (not currently animating)');
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
        
    def _convert_to_3dmol_format(self, structure_data, filetype):
        """Convert molecular files to 3Dmol.js compatible formats using external packages"""
        filetype = filetype.lower()
        
        # Direct 3Dmol.js supported formats
        if filetype in ['xyz', 'pdb', 'sdf']:
            return structure_data, filetype
        
        # Convert MOL to SDF (3Dmol.js treats them similarly)
        if filetype == 'mol':
            return structure_data, 'sdf'
        
        # Convert COM/GJF using available packages
        if filetype in ['com', 'gjf']:
            return self._convert_gaussian_to_xyz(structure_data)
        
        # Fallback - try to parse as XYZ
        warnings.warn(f"Unsupported format {filetype}, attempting to parse as XYZ")
        return structure_data, 'xyz'
    
    def _convert_gaussian_to_xyz(self, gaussian_data):
        """Convert Gaussian COM/GJF format to XYZ using available packages"""
        
        # Try OpenBabel first (most comprehensive)
        if HAS_OPENBABEL:
            try:
                return self._openbabel_to_xyz(gaussian_data, 'com')
            except Exception as e:
                warnings.warn(f"OpenBabel conversion failed: {e}")
        
        # Try CClib for Gaussian files
        if HAS_CCLIB:
            try:
                return self._cclib_to_xyz(gaussian_data)
            except Exception as e:
                warnings.warn(f"CClib conversion failed: {e}")
        
        # Fallback to manual parsing
        try:
            return self._manual_gaussian_to_xyz(gaussian_data)
        except Exception as e:
            raise ValueError(f"Failed to convert Gaussian file: {e}")
    
    def _openbabel_to_xyz(self, data, input_format):
        """Convert using OpenBabel"""
        conv = openbabel.OBConversion()
        conv.SetInAndOutFormats(input_format, "xyz")
        
        mol = openbabel.OBMol()
        conv.ReadString(mol, data)
        
        xyz_data = conv.WriteString(mol)
        return xyz_data, 'xyz'
    
    def _cclib_to_xyz(self, gaussian_data):
        """Convert Gaussian data using CClib"""
        # CClib typically works with files, so we'll use a string buffer
        string_buffer = io.StringIO(gaussian_data)
        
        # Parse the Gaussian data
        parser = cclib.io.ccopen(string_buffer)
        if parser is None:
            raise ValueError("CClib could not parse the Gaussian data")
        
        data = parser.parse()
        
        # Extract coordinates and atom types
        if not hasattr(data, 'atomcoords') or not hasattr(data, 'atomnos'):
            raise ValueError("No coordinate data found in Gaussian file")
        
        # Use the last set of coordinates
        coords = data.atomcoords[-1]
        atomnos = data.atomnos
        
        # Convert atomic numbers to symbols
        from cclib.parser.utils import PeriodicTable
        pt = PeriodicTable()
        
        # Create XYZ format
        xyz_lines = [str(len(atomnos)), "Converted from Gaussian format"]
        for i, (atomno, coord) in enumerate(zip(atomnos, coords)):
            symbol = pt.element[atomno]
            x, y, z = coord
            xyz_lines.append(f"{symbol} {x:.6f} {y:.6f} {z:.6f}")
        
        return '\n'.join(xyz_lines), 'xyz'
    
    def _manual_gaussian_to_xyz(self, gaussian_data):
        """Manual parsing of Gaussian COM/GJF format"""
        lines = gaussian_data.strip().split('\n')
        
        # Find the molecule specification section
        coord_start = -1
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped and len(stripped.split()) == 2:
                try:
                    # Check if line contains charge and multiplicity
                    charge, mult = map(int, stripped.split())
                    coord_start = i + 1
                    break
                except ValueError:
                    continue
        
        if coord_start == -1:
            raise ValueError("Could not find molecule specification in Gaussian file")
        
        # Extract coordinates
        atoms = []
        for i in range(coord_start, len(lines)):
            line = lines[i].strip()
            if not line or line.startswith('%') or line.startswith('#'):
                break
            
            parts = line.split()
            if len(parts) >= 4:
                try:
                    element = parts[0]
                    x, y, z = map(float, parts[1:4])
                    atoms.append((element, x, y, z))
                except (ValueError, IndexError):
                    break
        
        if not atoms:
            raise ValueError("No valid coordinates found in Gaussian file")
        
        # Create XYZ format
        xyz_lines = [str(len(atoms)), "Converted from Gaussian format"]
        for element, x, y, z in atoms:
            xyz_lines.append(f"{element} {x:.6f} {y:.6f} {z:.6f}")
        
        return '\n'.join(xyz_lines), 'xyz'
    
    def _parse_atoms_for_labels(self, structure_data, filetype):
        """Parse atom coordinates for labeling from various formats"""
        filetype = filetype.lower()
        
        if filetype == 'xyz':
            return self._parse_xyz_atoms(structure_data)
        elif filetype == 'pdb':
            return self._parse_pdb_atoms(structure_data)
        elif filetype in ['sdf', 'mol']:
            return self._parse_sdf_atoms(structure_data)
        elif filetype in ['com', 'gjf']:
            # Convert to XYZ first, then parse
            xyz_data, _ = self._convert_gaussian_to_xyz(structure_data)
            return self._parse_xyz_atoms(xyz_data)
        else:
            return []
    
    def _parse_xyz_atoms(self, xyz_data):
        """Parse XYZ format atoms"""
        lines = xyz_data.strip().split('\n')
        if len(lines) < 3:
            return []
        
        try:
            natoms = int(lines[0])
            atoms = []
            for i in range(2, min(2 + natoms, len(lines))):
                parts = lines[i].split()
                if len(parts) >= 4:
                    element = parts[0]
                    x, y, z = map(float, parts[1:4])
                    atoms.append((element, x, y, z))
            return atoms
        except (ValueError, IndexError):
            return []
    
    def _parse_pdb_atoms(self, pdb_data):
        """Parse PDB format atoms"""
        lines = pdb_data.strip().split('\n')
        atoms = []
        
        for line in lines:
            if line.startswith('ATOM') or line.startswith('HETATM'):
                try:
                    if len(line) >= 54:
                        element = line[76:78].strip() or line[12:16].strip()[:1]
                        x = float(line[30:38].strip())
                        y = float(line[38:46].strip())
                        z = float(line[46:54].strip())
                        atoms.append((element, x, y, z))
                except (ValueError, IndexError):
                    continue
        
        return atoms
    
    def _parse_sdf_atoms(self, sdf_data):
        """Parse SDF/MOL format atoms"""
        lines = sdf_data.strip().split('\n')
        
        if len(lines) < 4:
            return []
        
        try:
            counts_line = lines[3]
            atom_count = int(counts_line[:3])
            
            atoms = []
            for i in range(4, min(4 + atom_count, len(lines))):
                line = lines[i]
                if len(line) >= 34:
                    x = float(line[:10].strip())
                    y = float(line[10:20].strip())
                    z = float(line[20:30].strip())
                    element = line[31:34].strip()
                    atoms.append((element, x, y, z))
            
            return atoms
        except (ValueError, IndexError):
            return []
        
    
    # py3dmol-compatible API methods
    def addModel(self, data, format):
        """Add a molecular model to the viewer (py3dmol compatible)"""
        try:
            # Convert to 3Dmol.js compatible format if needed
            converted_data, converted_format = self._convert_to_3dmol_format(data, format)
            self.structure = converted_data
            self.filetype = converted_format
            
            # Parse atoms for labeling using original format
            self.parsed_atoms = self._parse_atoms_for_labels(data, format)
        except Exception as e:
            warnings.warn(f"Format conversion failed: {e}. Using original data.")
            self.structure = data
            self.filetype = format
            
            # Try parsing with original format
            try:
                self.parsed_atoms = self._parse_atoms_for_labels(data, format)
            except Exception as parse_e:
                warnings.warn(f"Atom parsing failed: {parse_e}")
                self.parsed_atoms = []
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
    
    def startAnimation(self, speed=None, loop_mode="forward", **animate_options):
        """Start 3Dmol.js native animation with custom options (py3dmol compatible)"""
        if speed is not None:
            self.animation_speed = speed
        
        # Build animation options
        options = {'loop': loop_mode}
        options.update(animate_options)
        
        if options:
            self.animate_options = options
        
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
    
    def setAnimationOptions(self, **options):
        """Set custom 3Dmol.js animation options"""
        self.animate_options = options
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