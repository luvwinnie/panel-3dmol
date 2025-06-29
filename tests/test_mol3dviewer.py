"""
Unit tests for Mol3DViewer functionality
"""
import pytest
import panel as pn
from panel_3dmol import Mol3DViewer, view


class TestMol3DViewer:
    """Test suite for Mol3DViewer class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        pn.extension()
        self.viewer = Mol3DViewer()
        
        # Sample molecular data for testing
        self.benzene_xyz = """6
Benzene molecule
C    0.0000    1.3970    0.0000
C    1.2098    0.6985    0.0000  
C    1.2098   -0.6985    0.0000
C    0.0000   -1.3970    0.0000
C   -1.2098   -0.6985    0.0000
C   -1.2098    0.6985    0.0000"""
        
        self.caffeine_pdb = """ATOM      1  N   CAF     1      -0.744   1.329   0.000  1.00  0.00           N  
ATOM      2  C   CAF     1       0.558   1.875   0.000  1.00  0.00           C  
ATOM      3  C   CAF     1       1.657   1.080   0.000  1.00  0.00           C  
ATOM      4  N   CAF     1       1.657  -0.287   0.000  1.00  0.00           N  
ATOM      5  C   CAF     1       0.455  -0.832   0.000  1.00  0.00           C  
ATOM      6  C   CAF     1      -0.744  -0.037   0.000  1.00  0.00           C  """

    def test_viewer_creation(self):
        """Test basic viewer creation"""
        viewer = Mol3DViewer()
        assert viewer is not None
        assert hasattr(viewer, 'structure')
        assert hasattr(viewer, 'filetype')
        assert hasattr(viewer, 'background_color')

    def test_default_parameters(self):
        """Test default parameter values"""
        viewer = Mol3DViewer()
        assert viewer.structure == ""
        assert viewer.filetype == "xyz"
        assert viewer.background_color == "white"
        assert viewer.show_stick == True
        assert viewer.show_sphere == True
        assert viewer.show_cartoon == False
        assert viewer.show_line == False
        assert viewer.show_surface == False

    def test_parameter_setting(self):
        """Test setting parameters"""
        viewer = Mol3DViewer()
        
        # Test structure setting
        viewer.structure = self.benzene_xyz
        assert viewer.structure == self.benzene_xyz
        
        # Test filetype setting
        viewer.filetype = "pdb"
        assert viewer.filetype == "pdb"
        
        # Test background color setting
        viewer.background_color = "black"
        assert viewer.background_color == "black"
        
        # Test style parameters
        viewer.show_stick = False
        viewer.show_cartoon = True
        assert viewer.show_stick == False
        assert viewer.show_cartoon == True

    def test_set_style_method(self):
        """Test py3dmol-compatible setStyle method"""
        viewer = Mol3DViewer()
        
        # Test stick style
        result = viewer.setStyle({}, {'stick': {'radius': 0.2}})
        assert result is viewer  # Should return self for chaining
        assert viewer.show_stick == True
        assert viewer.show_sphere == False
        assert viewer.show_cartoon == False
        
        # Test multiple styles
        viewer.setStyle({}, {'stick': {'radius': 0.2}, 'sphere': {'radius': 0.4}})
        assert viewer.show_stick == True
        assert viewer.show_sphere == True
        assert viewer.show_cartoon == False
        
        # Test cartoon style
        viewer.setStyle({}, {'cartoon': {}})
        assert viewer.show_cartoon == True
        assert viewer.show_stick == False
        assert viewer.show_sphere == False
        
        # Test line style
        viewer.setStyle({}, {'line': {}})
        assert viewer.show_line == True
        assert viewer.show_stick == False
        
        # Test surface style
        viewer.setStyle({}, {'surface': {}})
        assert viewer.show_surface == True
        assert viewer.show_stick == False

    def test_background_color_method(self):
        """Test setBackgroundColor method"""
        viewer = Mol3DViewer()
        
        result = viewer.setBackgroundColor('lightgray')
        assert result is viewer  # Should return self for chaining
        assert viewer.background_color == 'lightgray'
        
        viewer.setBackgroundColor('#ffffff')
        assert viewer.background_color == '#ffffff'

    def test_clear_method(self):
        """Test clear method"""
        viewer = Mol3DViewer()
        viewer.structure = self.benzene_xyz
        
        result = viewer.clear()
        assert result is viewer  # Should return self for chaining
        assert viewer.structure == ""

    def test_method_chaining(self):
        """Test that methods can be chained together"""
        viewer = Mol3DViewer()
        
        # Should be able to chain multiple method calls
        result = (viewer
                 .setStyle({}, {'stick': {'radius': 0.2}})
                 .setBackgroundColor('lightgray')
                 .clear())
        
        assert result is viewer
        assert viewer.background_color == 'lightgray'
        assert viewer.structure == ""

    def test_render_method(self):
        """Test render method"""
        viewer = Mol3DViewer()
        result = viewer.render()
        assert result is viewer  # Should return self for chaining

    def test_center_method(self):
        """Test center method"""
        viewer = Mol3DViewer()
        result = viewer.center()
        assert result is viewer  # Should return self for chaining

    def test_structure_formats(self):
        """Test loading different molecular formats"""
        viewer = Mol3DViewer()
        
        # Test XYZ format
        viewer.structure = self.benzene_xyz
        viewer.filetype = "xyz"
        assert viewer.structure == self.benzene_xyz
        assert viewer.filetype == "xyz"
        
        # Test PDB format
        viewer.structure = self.caffeine_pdb
        viewer.filetype = "pdb"
        assert viewer.structure == self.caffeine_pdb
        assert viewer.filetype == "pdb"

    def test_with_panel_layout(self):
        """Test that viewer works in Panel layouts"""
        viewer = Mol3DViewer()
        
        # Test in Column layout
        col = pn.Column("Test", viewer)
        assert viewer in col.objects
        
        # Test in Row layout
        row = pn.Row(viewer, "Test")
        assert viewer in row.objects

    def test_javascript_dependencies(self):
        """Test that JavaScript dependencies are properly defined"""
        viewer = Mol3DViewer()
        assert hasattr(viewer, '__javascript__')
        assert isinstance(viewer.__javascript__, list)
        assert len(viewer.__javascript__) > 0
        assert any('3dmol' in js.lower() for js in viewer.__javascript__)

    def test_template_structure(self):
        """Test that HTML template is properly defined"""
        viewer = Mol3DViewer()
        assert hasattr(viewer, '_template')
        assert isinstance(viewer._template, str)
        assert 'viewer-' in viewer._template  # Should have viewer element
        assert 'loading-' in viewer._template  # Should have loading element

    def test_scripts_structure(self):
        """Test that JavaScript scripts are properly defined"""
        viewer = Mol3DViewer()
        assert hasattr(viewer, '_scripts')
        assert isinstance(viewer._scripts, dict)
        
        # Check for essential script handlers
        essential_scripts = ['render', 'structure', 'background_color']
        for script in essential_scripts:
            assert script in viewer._scripts
            assert isinstance(viewer._scripts[script], str)


class TestViewFactory:
    """Test suite for the view factory function"""
    
    def test_view_factory_creation(self):
        """Test view factory function"""
        viewer = view()
        assert isinstance(viewer, Mol3DViewer)
        
    def test_view_factory_with_dimensions(self):
        """Test view factory with custom dimensions"""
        viewer = view(width=800, height=600)
        assert isinstance(viewer, Mol3DViewer)
        assert viewer.width == 800
        assert viewer.height == 600
        
    def test_view_factory_with_kwargs(self):
        """Test view factory with additional kwargs"""
        viewer = view(background_color='black', show_cartoon=True)
        assert isinstance(viewer, Mol3DViewer)
        assert viewer.background_color == 'black'
        assert viewer.show_cartoon == True


class TestPanelIntegration:
    """Test Panel-specific integration features"""
    
    def setup_method(self):
        """Set up Panel extension"""
        pn.extension()
    
    def test_reactive_parameters(self):
        """Test that parameters are reactive"""
        viewer = Mol3DViewer()
        
        # Parameters should have param watchers
        assert hasattr(viewer.param, 'structure')
        assert hasattr(viewer.param, 'filetype')
        assert hasattr(viewer.param, 'background_color')
    
    def test_panel_app_creation(self):
        """Test creating a Panel app with viewer"""
        viewer = Mol3DViewer()
        
        app = pn.Column(
            "# Test App",
            viewer
        )
        
        assert len(app.objects) == 2
        assert str(app.objects[0].object) == "# Test App"  # Panel wraps strings in Markdown
        assert app.objects[1] is viewer
    
    def test_multiple_viewers(self):
        """Test creating multiple viewers"""
        viewer1 = Mol3DViewer()
        viewer2 = Mol3DViewer()
        
        # Should be different instances
        assert viewer1 is not viewer2
        
        # Should be able to set different parameters
        viewer1.background_color = 'white'
        viewer2.background_color = 'black'
        
        assert viewer1.background_color != viewer2.background_color


if __name__ == "__main__":
    pytest.main([__file__, "-v"])