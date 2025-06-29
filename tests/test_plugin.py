#!/usr/bin/env python3
"""
Simple test script for 3Dmol Panel Plugin
Tests basic functionality and API compatibility
"""

import sys
import panel as pn

def test_imports():
    """Test if we can import the plugin"""
    try:
        from panel_3dmol import Mol3DViewer, view
        print("✅ Successfully imported Mol3DViewer and view")
        return True, Mol3DViewer, view
    except ImportError as e:
        print(f"❌ Failed to import plugin: {e}")
        return False, None, None

def test_basic_viewer_creation(view_func):
    """Test basic viewer creation"""
    try:
        viewer = view_func(width=600, height=400)
        print("✅ Successfully created viewer instance")
        return True, viewer
    except Exception as e:
        print(f"❌ Failed to create viewer: {e}")
        return False, None

def test_api_methods(viewer):
    """Test py3dmol-compatible API methods"""
    try:
        # Test data
        water_xyz = """3
Water molecule
O    0.0000    0.0000    0.0000
H    0.7572    0.5861    0.0000
H   -0.7572    0.5861    0.0000"""
        
        # Test addModel
        result = viewer.addModel(water_xyz, 'xyz')
        if result == viewer:
            print("✅ addModel() method works (returns self)")
        else:
            print("❌ addModel() doesn't return self")
        
        # Test setStyle
        result = viewer.setStyle({}, {'stick': {'radius': 0.2}, 'sphere': {'radius': 0.3}})
        if result == viewer:
            print("✅ setStyle() method works (returns self)")
        else:
            print("❌ setStyle() doesn't return self")
        
        # Test setBackgroundColor
        result = viewer.setBackgroundColor('lightblue')
        if result == viewer:
            print("✅ setBackgroundColor() method works (returns self)")
        else:
            print("❌ setBackgroundColor() doesn't return self")
        
        # Test zoomTo
        result = viewer.zoomTo()
        if result == viewer:
            print("✅ zoomTo() method works (returns self)")
        else:
            print("❌ zoomTo() doesn't return self")
        
        # Test render
        result = viewer.render()
        if result == viewer:
            print("✅ render() method works (returns self)")
        else:
            print("❌ render() doesn't return self")
        
        return True
        
    except Exception as e:
        print(f"❌ API method test failed: {e}")
        return False

def test_parameters(viewer):
    """Test parameter setting and getting"""
    try:
        # Test structure parameter
        viewer.structure = "test structure"
        if viewer.structure == "test structure":
            print("✅ Structure parameter works")
        else:
            print("❌ Structure parameter failed")
        
        # Test filetype parameter
        viewer.filetype = "pdb"
        if viewer.filetype == "pdb":
            print("✅ Filetype parameter works")
        else:
            print("❌ Filetype parameter failed")
        
        # Test show_stick parameter
        viewer.show_stick = False
        if viewer.show_stick == False:
            print("✅ Show_stick parameter works")
        else:
            print("❌ Show_stick parameter failed")
        
        # Test stick_radius parameter
        viewer.stick_radius = 0.25
        if abs(viewer.stick_radius - 0.25) < 0.001:
            print("✅ Stick_radius parameter works")
        else:
            print("❌ Stick_radius parameter failed")
        
        return True
        
    except Exception as e:
        print(f"❌ Parameter test failed: {e}")
        return False

def test_panel_display(viewer):
    """Test Panel display functionality"""
    try:
        # Test creating a simple Panel layout
        app = pn.Column(
            "## Test 3Dmol Viewer",
            viewer,
            width=700
        )
        print("✅ Successfully created Panel layout with viewer")
        return True, app
        
    except Exception as e:
        print(f"❌ Panel display test failed: {e}")
        return False, None

def run_all_tests():
    """Run all tests"""
    print("🧪 Starting 3Dmol Panel Plugin Tests")
    print("=" * 50)
    
    # Test 1: Imports
    success, Mol3DViewer, view_func = test_imports()
    if not success:
        print("❌ Cannot continue without successful imports")
        return False
    
    # Test 2: Basic viewer creation
    success, viewer = test_basic_viewer_creation(view_func)
    if not success:
        print("❌ Cannot continue without viewer creation")
        return False
    
    # Test 3: API methods
    print("\n🔧 Testing API Methods:")
    test_api_methods(viewer)
    
    # Test 4: Parameters
    print("\n📊 Testing Parameters:")
    test_parameters(viewer)
    
    # Test 5: Panel display
    print("\n🖥️  Testing Panel Display:")
    success, app = test_panel_display(viewer)
    
    print("\n" + "=" * 50)
    print("🎉 Tests completed!")
    
    if success:
        return app
    else:
        return None

def main():
    """Main test function"""
    # Enable Panel extensions
    pn.extension()
    
    # Run tests
    app = run_all_tests()
    
    if app:
        print("\n🚀 Starting test server...")
        print("📱 Open http://localhost:5008 to view the test")
        app.show(port=5008, title="3Dmol Plugin Test")
    else:
        print("❌ Tests failed, not starting server")

if __name__ == "__main__":
    main() 