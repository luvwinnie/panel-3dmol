"""
Simple test script for 3Dmol Panel Plugin
Tests basic functionality and API compatibility
"""

import pytest
import panel as pn
from panel_3dmol import Mol3DViewer, view


def test_imports():
    """Test if we can import the plugin"""
    # Just test that imports work
    assert Mol3DViewer is not None
    assert view is not None
    print("✅ Successfully imported Mol3DViewer and view")


def test_basic_viewer_creation():
    """Test basic viewer creation"""
    viewer = view(width=600, height=400)
    assert viewer is not None
    assert isinstance(viewer, Mol3DViewer)
    print("✅ Successfully created viewer instance")


def test_api_methods():
    """Test py3dmol-compatible API methods"""
    viewer = Mol3DViewer()
    
    # Test data
    water_xyz = """3
Water molecule
O    0.0000    0.0000    0.0000
H    0.7572    0.5861    0.0000
H   -0.7572    0.5861    0.0000"""
    
    # Test setStyle
    result = viewer.setStyle({}, {'stick': {'radius': 0.2}, 'sphere': {'radius': 0.3}})
    assert result == viewer, "setStyle should return self"
    
    # Test setBackgroundColor
    result = viewer.setBackgroundColor('lightblue')
    assert result == viewer, "setBackgroundColor should return self"
    assert viewer.background_color == 'lightblue'
    
    # Test render
    result = viewer.render()
    assert result == viewer, "render should return self"
    
    # Test clear
    result = viewer.clear()
    assert result == viewer, "clear should return self"
    assert viewer.structure == ""
    
    print("✅ All API methods work correctly")


def test_parameters():
    """Test parameter setting and getting"""
    viewer = Mol3DViewer()
    
    # Test structure parameter
    viewer.structure = "test structure"
    assert viewer.structure == "test structure"
    
    # Test filetype parameter
    viewer.filetype = "pdb"
    assert viewer.filetype == "pdb"
    
    # Test show_stick parameter
    viewer.show_stick = False
    assert viewer.show_stick == False
    
    # Test background_color parameter
    viewer.background_color = "red"
    assert viewer.background_color == "red"
    
    print("✅ All parameters work correctly")


def test_panel_display():
    """Test Panel display functionality"""
    pn.extension()
    viewer = Mol3DViewer()
    
    # Test creating a simple Panel layout
    app = pn.Column(
        "## Test 3Dmol Viewer",
        viewer,
        width=700
    )
    
    assert len(app.objects) == 2
    assert app.objects[1] is viewer
    print("✅ Successfully created Panel layout with viewer")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])