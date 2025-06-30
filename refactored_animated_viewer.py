#!/usr/bin/env python3
"""
Refactored AnimatedMolecularViewer using the latest Panel-3Dmol Animation API
Uses Panel-controlled animation for better integration and reliability
"""

import panel as pn
import param
import plotly.express as px
import pandas as pd
from panel_3dmol import Mol3DViewer
import warnings
import os
import asyncio

# Enable all warnings for debugging
os.environ['BOKEH_LOG_LEVEL'] = 'debug'
import logging
logging.getLogger('bokeh').setLevel(logging.DEBUG)
logging.getLogger('panel').setLevel(logging.DEBUG)
logging.getLogger('param').setLevel(logging.DEBUG)

# Enable all warnings to see what's happening
warnings.filterwarnings('default')  # Show all warnings

print("🔧 DEBUG MODE ENABLED - All warnings and logs will be shown")

# Enable Panel extensions
pn.extension('plotly')
pn.config.sizing_mode = 'stretch_width'

def extract_xyz_frames_to_list(input_file='DMF_final.xyz'):
    """Extract individual frames from a multi-frame XYZ file and return as list"""
    
    # Read multi-frame xyz file
    with open(input_file, 'r') as f:
        xyz_data = f.read()
    
    # Split each frame
    lines = xyz_data.split('\n')
    
    # Remove any empty lines at the end
    while lines and lines[-1].strip() == '':
        lines.pop()
    
    if not lines:
        return []
    
    natoms = int(lines[0])   # Number of atoms in the first line
    frame_size = natoms + 2  # Number of lines per frame (natoms + header + comment)
    num_frames = len(lines) // frame_size
    
    # Extract each frame as individual XYZ strings
    frames = []
    for i in range(num_frames):
        start = i * frame_size
        end = start + frame_size
        
        # Extract frame lines
        frame_lines = lines[start:end]
        frame_content = '\n'.join(frame_lines)
        frames.append(frame_content)
    
    return frames

# Load data (fallback to demo data if files don't exist)
try:
    xyz_frames = extract_xyz_frames_to_list('DMF_final.xyz')
    df_energy = pd.read_csv('DMF_energy.csv')
except FileNotFoundError:
    # Create demo data
    xyz_frames = []
    for i in range(20):
        scale = 1.0 + 0.3 * (i / 19.0)
        frame = f"""6
DMF frame {i+1}
N    0.000000    0.000000    0.000000
C    {1.2*scale:.6f}    0.000000    0.000000
C   {-1.2*scale:.6f}    0.000000    0.000000
H    {1.8*scale:.6f}    {0.8*scale:.6f}    0.000000
H    {1.8*scale:.6f}   {-0.8*scale:.6f}    0.000000
O   {-2.0*scale:.6f}    0.000000    0.000000"""
        xyz_frames.append(frame)
    
    # Create demo energy data
    energies = [5.0 * (i / 19.0) ** 2 for i in range(20)]
    df_energy = pd.DataFrame({
        'image': list(range(20)),
        'Delta E vs. reactant [kcal/mol]': energies
    })

num_frames = len(xyz_frames)

class AnimatedMolecularViewer(param.Parameterized):
    """
    Enhanced molecular viewer with Panel-controlled animation and energy plot integration
    Uses the latest Panel-3Dmol Animation API for better reliability
    """
    
    # Animation parameters that sync with Mol3DViewer
    current_frame = param.Integer(default=0, bounds=(0, max(0, num_frames-1)))
    animation_speed = param.Integer(default=200, bounds=(50, 1000), doc="Animation interval in ms")
    is_playing = param.Boolean(default=False)
    loop_mode = param.Selector(default="forward", objects=["forward", "backward", "pingpong"])
    
    # Display parameters
    show_stick = param.Boolean(default=True)
    show_sphere = param.Boolean(default=True)
    
    def __init__(self, **params):
        super().__init__(**params)
        
        # Create the molecular viewer using panel-3dmol with latest animation API
        self.mol_viewer = Mol3DViewer(
            min_width=600,
            height=600,
            background_color='white',
            show_atom_labels=True,
            animate=False,  # CRITICAL: Disable built-in animation completely
            current_frame=0,
            total_frames=num_frames
        )
        
        # Load all frames using panel-3dmol's addFrames method
        if xyz_frames:
            self.mol_viewer.addFrames(xyz_frames, 'xyz')
            self.mol_viewer.setStyle({}, {
                'stick': {'radius': 0.08}, 
                'sphere': {'scale': 0.12}
            })
            # Set to first frame
            self.mol_viewer.setFrame(0)
        
        # Animation control state  
        self._animation_active = False
        self._animation_callback = None
        self._animation_direction = 1  # 1 for forward, -1 for backward
        self._updating_from_panel = False
        
        # Create UI components
        self.energy_plot = self.create_energy_plot()
        self.controls = self.create_controls()
        self.info_panel = pn.pane.HTML(self.get_frame_info_html(0), 
                                      min_width=400, height=500)
        
        # Set up parameter watchers for Panel-controlled animation
        self.param.watch(self.on_frame_change, 'current_frame')
        self.param.watch(self.on_animation_control, ['is_playing', 'animation_speed', 'loop_mode'])
        self.param.watch(self.on_display_change, ['show_stick', 'show_sphere'])
        
        # Disable reactive function to avoid conflicts with animation
        # self.reactive_frame_updater = pn.bind(self.update_molecular_viewer, self.param.current_frame)
        
        # Watch mol_viewer frame changes (for 3Dmol.js animation sync)
        self.mol_viewer.param.watch(self.on_mol_viewer_frame_change, 'current_frame')
        
        # Disable Panel animation since we're using 3Dmol.js native animation
        self._panel_animation_disabled = True
        
        print(f"Initialized with {num_frames} frames using native 3Dmol.js animation")
    
    def on_mol_viewer_frame_change(self, event):
        """Handle frame changes from 3Dmol.js animation (JavaScript -> Python sync)"""
        new_frame = event.new
        
        if new_frame != self.current_frame and not self._updating_from_panel:
            # Update Panel's current_frame to match 3Dmol.js animation
            self.current_frame = new_frame
            
            # Update info panel and energy plot to follow 3Dmol.js animation
            self.info_panel.object = self.get_frame_info_html(new_frame)
            self.update_energy_plot()
    
    def update_molecular_viewer(self, frame_id):
        """Reactive function (disabled - using native 3Dmol.js animation)"""
        # This function is no longer used since we switched to native 3Dmol.js animation
        pass
    
    def apply_molecular_style(self):
        """Apply current molecular styling"""
        style = {}
        if self.show_stick:
            style['stick'] = {'radius': 0.08}
        if self.show_sphere:
            style['sphere'] = {'scale': 0.12}
        
        if style:
            self.mol_viewer.setStyle({}, style)
        else:
            # Default style if nothing selected
            self.mol_viewer.setStyle({}, {'stick': {'radius': 0.08}})
    
    def create_energy_plot(self):
        """Create interactive energy plot with current frame indicator"""
        fig = px.scatter(
            df_energy,
            x='image',
            y='Delta E vs. reactant [kcal/mol]',
            labels={
                'image': 'Image index',
                'Delta E vs. reactant [kcal/mol]': 'ΔE (kcal/mol)'
            }
        )
        
        # Add current frame indicator
        self.update_energy_plot_marker(fig)
        
        # Styling
        fig.update_traces(marker=dict(size=8))
        fig.update_layout(
            font=dict(family='Arial', size=14, color='black'),
            title=dict(text="Energy Profile Along Reaction Path", 
                      font=dict(family='Arial', size=16, color='black')),
            xaxis=dict(title_font=dict(family='Arial', size=14, color='black'),
                      tickfont=dict(family='Arial', size=12, color='black'),
                      showline=True, linecolor='black', linewidth=1,
                      mirror=True, ticks='outside', showgrid=False),
            yaxis=dict(title_font=dict(family='Arial', size=14, color='black'),
                      tickfont=dict(family='Arial', size=12, color='black'),
                      showline=True, linecolor='black', linewidth=1,
                      mirror=True, ticks='outside', showgrid=False),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=500,
            showlegend=False
        )
        
        plot_pane = pn.pane.Plotly(fig, min_width=600, height=500)
        plot_pane.param.watch(self.on_plot_click, 'click_data')
        
        return plot_pane
    
    def update_energy_plot_marker(self, fig):
        """Update the current frame marker on the energy plot"""
        if len(df_energy) > self.current_frame:
            current_energy = df_energy.iloc[self.current_frame]['Delta E vs. reactant [kcal/mol]']
            fig.add_scatter(
                x=[self.current_frame],
                y=[current_energy],
                mode='markers',
                marker=dict(size=15, color='red', symbol='diamond'),
                name='Current Frame',
                showlegend=False
            )
    
    def create_controls(self):
        """Create animation control panel"""
        
        # Frame controls
        frame_slider = pn.Param(
            self, parameters=['current_frame'], 
            widgets={'current_frame': pn.widgets.IntSlider},
            name="Frame Control"
        )
        
        # Animation controls
        play_button = pn.Param(
            self, parameters=['is_playing'],
            widgets={'is_playing': {'type': pn.widgets.Toggle, 'name': '▶️ Play/Pause'}},
            name="Animation"
        )
        
        speed_control = pn.Param(
            self, parameters=['animation_speed'],
            widgets={'animation_speed': pn.widgets.IntSlider},
            name="Speed (ms)"
        )
        
        loop_control = pn.Param(
            self, parameters=['loop_mode'],
            widgets={'loop_mode': pn.widgets.Select},
            name="Loop Mode"
        )
        
        # Display controls
        display_controls = pn.Param(
            self, parameters=['show_stick', 'show_sphere'],
            name="Display Options"
        )
        
        # Quick navigation buttons
        def go_to_start():
            self.current_frame = 0
        
        def go_to_end():
            self.current_frame = num_frames - 1
        
        def step_backward():
            if self.current_frame > 0:
                self.current_frame -= 1
        
        def step_forward():
            if self.current_frame < num_frames - 1:
                self.current_frame += 1
        
        nav_buttons = pn.Row(
            pn.widgets.Button(name='⏮️ Start', button_type='primary', width=80),
            pn.widgets.Button(name='⏪ Step', button_type='default', width=80),
            pn.widgets.Button(name='⏩ Step', button_type='default', width=80),
            pn.widgets.Button(name='⏭️ End', button_type='primary', width=80)
        )
        
        # Connect button callbacks
        nav_buttons[0].on_click(lambda event: go_to_start())
        nav_buttons[1].on_click(lambda event: step_backward())
        nav_buttons[2].on_click(lambda event: step_forward())
        nav_buttons[3].on_click(lambda event: go_to_end())
        
        return pn.Column(
            "### 🎬 Native 3Dmol.js Animation",
            frame_slider,
            nav_buttons,
            play_button,
            speed_control,
            loop_control,
            "### 🎨 Display Options", 
            display_controls,
            width=350
        )
    
    def get_frame_info_html(self, frame_id):
        """Generate HTML for frame information"""
        if frame_id < len(df_energy):
            energy_value = df_energy.iloc[frame_id]['Delta E vs. reactant [kcal/mol]']
        else:
            energy_value = 0.0
            
        progress = (frame_id / max(1, num_frames - 1) * 100) if num_frames > 1 else 0
            
        return f"""
        <div style="padding: 15px; border: 1px solid #2E86C1; border-radius: 8px; background-color: #f8f9fa;">
            <h3 style="margin-top: 0; color: #2E86C1;">Current Frame Information</h3>
            <hr style="border-color: #2E86C1; margin: 10px 0;">
            <p><strong>Frame:</strong> {frame_id} / {num_frames - 1}</p>
            <p><strong>Energy:</strong> {energy_value:.2f} kcal/mol</p>
            <p><strong>Progress:</strong> {progress:.1f}%</p>
            <p><strong>Animation Mode:</strong> Native 3Dmol.js</p>
            <p><strong>Loop Mode:</strong> {self.loop_mode}</p>
            <div style="background-color: #e7f3ff; padding: 8px; border-radius: 4px; margin-top: 10px;">
                <small><em>3Dmol.js animation syncs with Panel controls automatically</em></small>
            </div>
        </div>
        """
    
    def on_frame_change(self, event):
        """Handle frame changes - update mol_viewer and energy plot"""
        frame_id = event.new
        
        # Flag to prevent feedback loops
        self._updating_from_panel = True
        
        # Only update the current_frame parameter, let ReactiveHTML handle the rest
        if hasattr(self.mol_viewer, 'current_frame'):
            self.mol_viewer.current_frame = frame_id
        
        # Update info panel
        self.info_panel.object = self.get_frame_info_html(frame_id)
        
        # Update energy plot marker
        self.update_energy_plot()
        
        self._updating_from_panel = False
    
    def update_energy_plot(self):
        """Update the energy plot with new current frame marker"""
        # Recreate the plot with updated marker
        fig = px.scatter(
            df_energy,
            x='image',
            y='Delta E vs. reactant [kcal/mol]',
            labels={
                'image': 'Image index',
                'Delta E vs. reactant [kcal/mol]': 'ΔE (kcal/mol)'
            }
        )
        
        self.update_energy_plot_marker(fig)
        
        # Apply styling
        fig.update_traces(marker=dict(size=8))
        fig.update_layout(
            font=dict(family='Arial', size=14, color='black'),
            title=dict(text="Energy Profile Along Reaction Path", 
                      font=dict(family='Arial', size=16, color='black')),
            xaxis=dict(title_font=dict(family='Arial', size=14, color='black'),
                      tickfont=dict(family='Arial', size=12, color='black'),
                      showline=True, linecolor='black', linewidth=1,
                      mirror=True, ticks='outside', showgrid=False),
            yaxis=dict(title_font=dict(family='Arial', size=14, color='black'),
                      tickfont=dict(family='Arial', size=12, color='black'),
                      showline=True, linecolor='black', linewidth=1,
                      mirror=True, ticks='outside', showgrid=False),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=500,
            showlegend=False
        )
        
        # Update the plot pane
        self.energy_plot.object = fig
    
    def on_animation_control(self, event):
        """Handle animation control changes - Native 3Dmol.js animation"""
        if event.name == 'is_playing':
            if event.new:
                # Set animation speed and start 3Dmol.js animation
                self.mol_viewer.animation_speed = self.animation_speed
                self.mol_viewer.animate = True  # This triggers native animate() in JavaScript
            else:
                self.mol_viewer.animate = False  # This stops native animation in JavaScript
                
        elif event.name == 'animation_speed':
            # Update speed on mol_viewer - JavaScript will handle restart
            self.mol_viewer.animation_speed = event.new
            
        elif event.name == 'loop_mode':
            # For now, 3Dmol.js handles looping internally
            # Future: could modify JavaScript to support different loop modes
            pass
    
    def on_display_change(self, event):
        """Handle display option changes"""
        self.apply_molecular_style()
    
    def on_plot_click(self, event):
        """Handle energy plot clicks"""
        if event.new and 'points' in event.new:
            point = event.new['points'][0]
            frame_id = int(point['x'])
            if 0 <= frame_id < num_frames:
                self.current_frame = frame_id
    
    def sync_with_3dmol_animation(self):
        """This method is no longer needed - 3Dmol.js animation syncs automatically via JavaScript callbacks"""
        pass
    
    # Note: Frame advancement is now handled by native 3Dmol.js animation
    # The JavaScript callback in viewer.py automatically updates self.current_frame
    
    def create_dashboard(self):
        """Create the complete dashboard"""
        
        # Title
        title = pn.pane.HTML("""
        <h1 style="color: #2E86C1; text-align: center; font-family: Arial;">
            🧬 Animated Molecular Reaction Path Viewer
        </h1>
        <hr style="border-color: #2E86C1;">
        """, min_width=1400, height=80)
        
        # Instructions
        instructions = pn.pane.HTML("""
        <div style="padding: 10px; background-color: #e7f3ff; border-left: 4px solid #2E86C1; border-radius: 4px; margin-bottom: 20px;">
            <strong>Native 3Dmol.js Animation:</strong> This version uses the 3Dmol.js built-in animate() method 
            for smooth molecular animation. Panel controls automatically sync with the animation speed and current frame.
            Change animation speed in milliseconds using the speed slider.
        </div>
        """, min_width=1400, height=60)
        
        # Main layout
        main_content = pn.Row(
            # Left: Molecular viewer
            pn.Column(
                pn.pane.HTML("<h3 style='color: #2E86C1; text-align: center;'>🧬 3D Structure</h3>"),
                self.mol_viewer,
                min_width=600
            ),
            
            # Center: Energy plot
            pn.Column(
                pn.pane.HTML("<h3 style='color: #2E86C1; text-align: center;'>📊 Energy Profile</h3>"),
                self.energy_plot,
                min_width=600
            ),
            
            # Right: Controls and info
            pn.Column(
                self.controls,
                pn.Spacer(height=20),
                self.info_panel,
                min_width=400
            ),
            
            sizing_mode='stretch_width'
        )
        
        return pn.Column(
            title,
            instructions,
            main_content,
            min_width=1600,
            height=900,
            sizing_mode='stretch_width'
        )

# Create the application
viewer_app = AnimatedMolecularViewer()
app = viewer_app.create_dashboard()

# Make it servable
app.servable()

# Display the app
app