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
    
    # HTML template with proper element reference
    _template = """
    <div id="viewer-${id}" style="width: 100%; height: 400px; border: 1px solid #ddd; position: relative;">
        <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); 
                    display: none;" id="loading-${id}">Loading 3Dmol.js...</div>
    </div>
    """
    
    # JavaScript for 3Dmol.js integration
    _scripts = {
        "render": """
            // Wait for 3Dmol.js to load
            function wait3DMol(callback, timeout = 10000) {
                const start = Date.now();
                function check() {
                    if (typeof window.$3Dmol !== 'undefined') {
                        callback();
                    } else if (Date.now() - start < timeout) {
                        setTimeout(check, 100);
                    } else {
                        console.error('3Dmol.js failed to load within timeout');
                        const loading = document.getElementById('loading-' + data.id);
                        if (loading) loading.innerHTML = 'Failed to load 3Dmol.js';
                    }
                }
                check();
            }
            
            // Initialize viewer
            const viewerDiv = document.getElementById('viewer-' + data.id);
            if (viewerDiv && !state.viewer) {
                const loading = document.getElementById('loading-' + data.id);
                if (loading) loading.style.display = 'block';
                
                wait3DMol(() => {
                    try {
                        state.viewer = window.$3Dmol.createViewer(viewerDiv, {
                            backgroundColor: data.background_color || "white"
                        });
                        
                        if (loading) loading.style.display = 'none';
                        
                        // Load initial structure if provided
                        if (data.structure) {
                            state.loadStructure();
                        }
                        
                        console.log('3Dmol viewer initialized successfully');
                    } catch (error) {
                        console.error('Failed to create 3Dmol viewer:', error);
                        if (loading) loading.innerHTML = 'Error creating viewer';
                    }
                });
            }
            
            // Helper function to load structure
            state.loadStructure = function() {
                if (!state.viewer || !data.structure) return;
                
                try {
                    state.viewer.clear();
                    state.viewer.addModel(data.structure, data.filetype);
                    
                    // Apply styles
                    const style = {};
                    if (data.show_stick) style.stick = {radius: 0.15};
                    if (data.show_sphere) style.sphere = {radius: 0.3};
                    if (data.show_cartoon) style.cartoon = {};
                    if (data.show_line) style.line = {};
                    if (data.show_surface) style.surface = {};
                    
                    // Default style if none selected
                    if (Object.keys(style).length === 0) {
                        style.stick = {radius: 0.15};
                        style.sphere = {radius: 0.3};
                    }
                    
                    state.viewer.setStyle({}, style);
                    state.viewer.zoomTo();
                    state.viewer.render();
                    
                    console.log('Structure loaded successfully');
                } catch (error) {
                    console.error('Error loading structure:', error);
                }
            };
        """,
        
        "structure": """
            if (state.loadStructure) {
                state.loadStructure();
            }
        """,
        
        "filetype": """
            if (state.loadStructure) {
                state.loadStructure();
            }
        """,
        
        "background_color": """
            if (state.viewer) {
                state.viewer.setBackgroundColor(data.background_color || "white");
                state.viewer.render();
            }
        """,
        
        "show_stick": """
            if (state.loadStructure) {
                state.loadStructure();
            }
        """,
        
        "show_sphere": """
            if (state.loadStructure) {
                state.loadStructure();
            }
        """,
        
        "show_cartoon": """
            if (state.loadStructure) {
                state.loadStructure();
            }
        """,
        
        "show_line": """
            if (state.loadStructure) {
                state.loadStructure();
            }
        """,
        
        "show_surface": """
            if (state.loadStructure) {
                state.loadStructure();
            }
        """
    }
    
    # JavaScript dependencies
    __javascript__ = [
        "https://3dmol.org/build/3Dmol.js"
    ]
    
    def __init__(self, **params):
        super().__init__(**params)
    
    # py3dmol-compatible API methods
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