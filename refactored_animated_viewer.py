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

# Suppress BokehWarnings using official Bokeh methods
os.environ['BOKEH_LOG_LEVEL'] = 'error'
import logging
logging.getLogger('bokeh').setLevel(logging.ERROR)

# Additional warning suppression
warnings.filterwarnings('ignore', category=UserWarning, module='bokeh')
warnings.filterwarnings('ignore', message='.*bokeh.*')
warnings.filterwarnings('ignore', message='.*width-responsive sizing_mode.*')
warnings.filterwarnings('ignore', category=UserWarning, module='param')

# Bokeh validation silence
try:
    from bokeh.core.validation import silence
    from bokeh.core.validation.warnings import MISSING_RENDERERS
    silence(MISSING_RENDERERS, True)
except ImportError:
    pass

try:
    import bokeh.core.validation as validation
    validation.silence_all_warnings()
except (ImportError, AttributeError):
    pass

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
    print("Demo mode: Creating sample data (DMF_final.xyz and DMF_energy.csv not found)")
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
            animate=False,  # Use Panel-controlled animation, not built-in
            animation_speed=self.animation_speed,
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
        self._animation_callback = None
        self._animation_direction = 1  # 1 for forward, -1 for backward
        self._last_update_time = 0
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
        
        # Watch mol_viewer frame changes (for external updates)
        self.mol_viewer.param.watch(self.on_mol_viewer_frame_change, 'current_frame')
        
        print(f"Initialized with {num_frames} frames using Panel-controlled animation")
    
    def on_mol_viewer_frame_change(self, event):
        """Handle frame changes from the mol_viewer (for bidirectional sync)"""
        if event.new != self.current_frame and not self._updating_from_panel:
            self.current_frame = event.new
    
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
            "### 🎮 Panel-Controlled Animation",
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
            <p><strong>Animation Mode:</strong> Panel-controlled</p>
            <p><strong>Loop Mode:</strong> {self.loop_mode}</p>
            <div style="background-color: #e7f3ff; padding: 8px; border-radius: 4px; margin-top: 10px;">
                <small><em>Use controls to navigate frames or click the energy plot</em></small>
            </div>
        </div>
        """
    
    def on_frame_change(self, event):
        """Handle frame changes - update mol_viewer and energy plot"""
        frame_id = event.new
        
        # Flag to prevent feedback loops
        self._updating_from_panel = True
        
        # Update molecular viewer frame using panel-3dmol's setFrame
        self.mol_viewer.setFrame(frame_id)
        
        # Also update the mol_viewer's current_frame parameter to keep it in sync
        if hasattr(self.mol_viewer, 'current_frame'):
            self.mol_viewer.current_frame = frame_id
        
        # Update info panel
        self.info_panel.object = self.get_frame_info_html(frame_id)
        
        # Update energy plot marker
        self.update_energy_plot()
        
        self._updating_from_panel = False
        
        print(f"Frame updated to: {frame_id}")
    
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
        """Handle animation control changes - Panel-controlled animation"""
        if event.name == 'is_playing':
            if event.new:
                self.start_panel_animation()
            else:
                self.stop_panel_animation()
        elif event.name == 'animation_speed':
            # Restart animation with new speed if playing
            if self.is_playing:
                self.stop_panel_animation()
                self.start_panel_animation()
        elif event.name == 'loop_mode':
            # Reset direction for loop mode changes
            self._animation_direction = 1
            print(f"Loop mode changed to: {event.new}")
    
    def on_display_change(self, event):
        """Handle display option changes"""
        self.apply_molecular_style()
        print(f"Display updated: {event.name} = {event.new}")
    
    def on_plot_click(self, event):
        """Handle energy plot clicks"""
        if event.new and 'points' in event.new:
            point = event.new['points'][0]
            frame_id = int(point['x'])
            if 0 <= frame_id < num_frames:
                self.current_frame = frame_id
                print(f"Clicked on energy plot, jumping to frame: {frame_id}")
    
    def start_panel_animation(self):
        """Start Panel-controlled animation using periodic callbacks"""
        if self._animation_callback is None:
            self._animation_callback = pn.state.add_periodic_callback(
                self.advance_frame, 
                self.animation_speed
            )
            print(f"Started Panel animation at {self.animation_speed}ms intervals, mode: {self.loop_mode}")
            print(f"Current frame: {self.current_frame}, Total frames: {num_frames}")
    
    def stop_panel_animation(self):
        """Stop Panel-controlled animation"""
        if self._animation_callback is not None:
            self._animation_callback.stop()
            self._animation_callback = None
            print("Stopped Panel animation")
    
    def advance_frame(self):
        """Advance to next frame based on loop mode (called by Panel periodic callback)"""
        old_frame = self.current_frame
        
        if self.loop_mode == "forward":
            next_frame = (self.current_frame + 1) % num_frames
        elif self.loop_mode == "backward":
            next_frame = (self.current_frame - 1) % num_frames
        elif self.loop_mode == "pingpong":
            # Ping-pong animation
            next_frame = self.current_frame + self._animation_direction
            
            # Check boundaries and reverse direction
            if next_frame >= num_frames - 1:
                next_frame = num_frames - 1
                self._animation_direction = -1
            elif next_frame <= 0:
                next_frame = 0
                self._animation_direction = 1
        
        self.current_frame = next_frame
        print(f"Animation: {old_frame} -> {next_frame} (mode: {self.loop_mode})")
    
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
            <strong>Latest Animation API:</strong> This version uses Panel-controlled animation for maximum reliability and control. 
            Features include forward/backward/pingpong loop modes, energy plot synchronization, and responsive frame updates.
            Click any point on the energy plot to jump to that frame.
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
print("Creating refactored AnimatedMolecularViewer with latest Panel-3Dmol Animation API...")

viewer_app = AnimatedMolecularViewer()
app = viewer_app.create_dashboard()

# Make it servable
app.servable()

# Display the app
app