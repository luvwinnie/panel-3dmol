"""
Panel-3Dmol: 3D Molecular Visualization Extension for Panel

A comprehensive 3D molecular visualization widget for Panel applications,
based on py3dmol library patterns but adapted for Panel's ReactiveHTML framework.
"""

__version__ = "0.1.0"
__author__ = "Panel-Chem Contributors"
__email__ = "info@panel-chem.org"
__description__ = "3D Molecular Visualization Extension for Panel"

import panel as pn

from .viewer import Mol3DViewer, view


def _jupyter_labextension_paths():
    """Called by Jupyter Lab to find the extension's assets."""
    return [{
        'src': 'labextension',
        'dest': 'panel_3dmol'
    }]


def _jupyter_nbextension_paths():
    """Called by Jupyter Notebook to find the extension's assets."""
    return [{
        'section': 'notebook',
        'src': 'nbextension',
        'dest': 'panel_3dmol',
        'require': 'panel_3dmol/extension'
    }]


def extension(*, template="material", theme="dark", **kwargs):
    """
    Load the Panel-3Dmol extension.
    
    This function should be called in your Panel app to enable 3D molecular visualization.
    
    Parameters:
    -----------
    template : str, optional
        Panel template to use (default: "material")
    theme : str, optional  
        Theme for the template (default: "dark")
    **kwargs : dict
        Additional arguments passed to pn.extension()
        
    Example:
    --------
    >>> import panel as pn
    >>> import panel_3dmol
    >>> pn.extension(template='material', theme='dark')
    >>> panel_3dmol.extension()
    """
    
    # Simply call Panel extension to ensure it's loaded
    try:
        pn.extension(template=template, **kwargs)
        print("Panel-3Dmol extension loaded successfully!")
        print("Use panel_3dmol.view() to create 3D molecular viewers.")
    except Exception as e:
        print(f"Warning: Could not load Panel extension: {e}")
        print("Panel-3Dmol components are still available.")


# Make main components available at package level
__all__ = [
    '__version__',
    'Mol3DViewer', 
    'view',
    'extension'
]
