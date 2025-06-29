# ✅ Fixed Dual Molecular Viewer - Using Proven Working Code
import panel as pn
import param
from panel.reactive import ReactiveHTML

# Enable Panel extensions
pn.extension('tabulator')
pn.config.sizing_mode = 'stretch_width'

# Global variables to access uploaded files
REACTANT_DATA = ""
PRODUCT_DATA = ""

class Mol3DViewer(ReactiveHTML):
    """
    A Panel component for 3D molecular visualization using 3Dmol.js.
    
    Based on proven working ReactiveHTML approach for maximum stability.
    """
    
    # Core parameters (simplified and proven to work)
    structure = param.String(default="", doc="Molecular structure data")
    filetype = param.String(default="xyz", doc="File type (xyz, mol, pdb, sdf, etc.)")
    background_color = param.String(default="white", doc="Background color")
    
    # Style parameters for py3dmol compatibility
    show_stick = param.Boolean(default=True, doc="Show stick representation")
    show_sphere = param.Boolean(default=True, doc="Show sphere representation")  
    show_cartoon = param.Boolean(default=False, doc="Show cartoon representation")
    show_surface = param.Boolean(default=False, doc="Show surface representation")
    show_line = param.Boolean(default=False, doc="Show line representation")
    
    # Simple, clean template (proven to work)
    _template = """
    <div id="viewer" style="width: 100%; height: 400px; border: 1px solid #ddd;"></div>
    """
    
    # Use _scripts exactly like your working code (PROVEN TO WORK!)
    _scripts = {
        "render": """
            const viewerDiv = viewer;
            state.viewer = $3Dmol.createViewer(viewerDiv, {backgroundColor: data.background_color || "white"});
            if (data.structure) {
                state.viewer.addModel(data.structure, data.filetype);
                state.viewer.setStyle({}, {stick:{radius: 0.15}, sphere:{radius: 0.3}});
                state.viewer.zoomTo();
                state.viewer.render();
            }
        """,
        "structure": """
            if (state.viewer) {
                state.viewer.clear();
                if (data.structure) {
                    state.viewer.addModel(data.structure, data.filetype);
                    
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
        """
    }
    
    # JavaScript dependencies - exactly like your working code
    __javascript__ = [
        "https://3dmol.org/build/3Dmol.js"
    ]
    
    def __init__(self, **params):
        super().__init__(**params)
    
    # py3dmol-compatible API methods
    def setStyle(self, selection={}, style={}):
        """Set molecular style (py3dmol compatible)"""
        # Reset all styles first
        self.show_stick = False
        self.show_sphere = False
        self.show_cartoon = False
        self.show_line = False
        self.show_surface = False
        
        # Set styles based on input
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
            
        # Default to stick+sphere if no style specified
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
        # Trigger re-render by updating structure parameter
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