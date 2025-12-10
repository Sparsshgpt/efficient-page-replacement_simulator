"""
Module 2: Visualization Module
==============================
Purpose: Show how pages move inside frames with a Tkinter GUI.

Features:
- Step-by-step frame visualization
- Table view showing all steps
- Color-coded page faults (red) and hits (green)
- Highlight replaced pages
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from typing import List, Callable, Optional, Dict
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from modules.simulation_engine import SimulationEngine, SimulationResult
from modules.metrics import MetricsCalculator


class PageReplacementGUI:
    """
    Main GUI application for the Page Replacement Simulator.
    
    Responsibilities:
    - Create and manage the main window
    - Handle user input (reference string, frames, algorithm)
    - Display step-by-step visualization
    - Show comparison results and charts
    """
    
    # Color scheme
    COLORS = {
        'bg_dark': '#1a1a2e',
        'bg_medium': '#16213e',
        'bg_light': '#0f3460',
        'accent': '#e94560',
        'success': '#00d9a5',
        'warning': '#ffd93d',
        'text_primary': '#ffffff',
        'text_secondary': '#a0a0a0',
        'hit': '#00d9a5',
        'fault': '#e94560',
        'frame_empty': '#2d2d44',
        'frame_filled': '#4a4a6a'
    }
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("🖥️ Efficient Page Replacement Algorithm Simulator")
        self.root.geometry("1200x800")
        self.root.configure(bg=self.COLORS['bg_dark'])
        self.root.minsize(1000, 700)
        
        # Initialize engines
        self.engine = SimulationEngine()
        self.metrics = MetricsCalculator()
        
        # Simulation state
        self.current_step = 0
        self.results: List[SimulationResult] = []
        self.all_results: Dict[str, List[SimulationResult]] = {}  # For export
        self.reference_string: List[int] = []
        self.num_frames = 3
        self.is_running = False
        
        # Build UI
        self._create_styles()
        self._create_main_layout()
        self._create_input_panel()
        self._create_control_panel()
        self._create_visualization_area()
        self._create_metrics_panel()
        
        # Set default values
        self.ref_entry.insert(0, "7,0,1,2,0,3,0,4,2,3,0,3,2,1,2,0,1,7,0,1")
        self.frame_spinbox.set(3)
    
    def _create_styles(self):
        """Configure ttk styles for modern look."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure('TFrame', background=self.COLORS['bg_dark'])
        style.configure('TLabel', 
                       background=self.COLORS['bg_dark'], 
                       foreground=self.COLORS['text_primary'],
                       font=('Segoe UI', 11))
        style.configure('Title.TLabel', 
                       font=('Segoe UI', 16, 'bold'),
                       foreground=self.COLORS['accent'])
        style.configure('Header.TLabel', 
                       font=('Segoe UI', 12, 'bold'))
        style.configure('TButton',
                       font=('Segoe UI', 10, 'bold'),
                       padding=10)
        style.configure('Accent.TButton',
                       background=self.COLORS['accent'],
                       foreground='white')
    
    def _create_main_layout(self):
        """Create the main layout structure."""
        # Header
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        title_label = ttk.Label(header_frame, 
                               text="🖥️ Efficient Page Replacement Algorithm Simulator",
                               style='Title.TLabel')
        title_label.pack(side=tk.LEFT)
        
        subtitle = ttk.Label(header_frame, 
                            text="Visualize FIFO, LRU, and Optimal algorithms",
                            foreground=self.COLORS['text_secondary'])
        subtitle.pack(side=tk.LEFT, padx=20)
        
        # Main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Left panel (input + controls + visualization)
        self.left_panel = ttk.Frame(self.main_container)
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Right panel (metrics)
        self.right_panel = ttk.Frame(self.main_container)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(20, 0))
    
    def _create_input_panel(self):
        """Create the input panel for reference string and frames."""
        input_frame = tk.Frame(self.left_panel, bg=self.COLORS['bg_medium'], 
                              relief=tk.FLAT, bd=0)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Inner padding
        inner_frame = tk.Frame(input_frame, bg=self.COLORS['bg_medium'])
        inner_frame.pack(fill=tk.X, padx=15, pady=15)
        
        # Reference string
        ref_label = tk.Label(inner_frame, text="📄 Reference String:", 
                            bg=self.COLORS['bg_medium'], fg=self.COLORS['text_primary'],
                            font=('Segoe UI', 11, 'bold'))
        ref_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.ref_entry = tk.Entry(inner_frame, font=('Consolas', 12), 
                                 width=50, bg=self.COLORS['bg_light'],
                                 fg=self.COLORS['text_primary'],
                                 insertbackground=self.COLORS['text_primary'],
                                 relief=tk.FLAT, bd=5)
        self.ref_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
        
        # Hint
        hint_label = tk.Label(inner_frame, text="(Comma-separated, e.g., 7,0,1,2,0,3)", 
                             bg=self.COLORS['bg_medium'], fg=self.COLORS['text_secondary'],
                             font=('Segoe UI', 9))
        hint_label.grid(row=0, column=2, sticky=tk.W)
        
        # Random Generate button
        self.random_btn = tk.Button(inner_frame, text="🎲 Random", 
                                   command=self.generate_random,
                                   bg='#a55eea', fg='white',
                                   font=('Segoe UI', 9, 'bold'),
                                   relief=tk.FLAT, padx=10, pady=2,
                                   cursor='hand2')
        self.random_btn.grid(row=0, column=3, padx=5)
        
        # Number of frames
        frame_label = tk.Label(inner_frame, text="🖼️ Number of Frames:", 
                              bg=self.COLORS['bg_medium'], fg=self.COLORS['text_primary'],
                              font=('Segoe UI', 11, 'bold'))
        frame_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.frame_spinbox = ttk.Spinbox(inner_frame, from_=1, to=10, width=5,
                                         font=('Segoe UI', 12))
        self.frame_spinbox.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)
        
        # Algorithm selection
        algo_label = tk.Label(inner_frame, text="⚙️ Algorithm:", 
                             bg=self.COLORS['bg_medium'], fg=self.COLORS['text_primary'],
                             font=('Segoe UI', 11, 'bold'))
        algo_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        self.algo_var = tk.StringVar(value="ALL")
        algo_frame = tk.Frame(inner_frame, bg=self.COLORS['bg_medium'])
        algo_frame.grid(row=2, column=1, columnspan=2, sticky=tk.W, padx=10)
        
        for algo in ["FIFO", "LRU", "LFU", "Optimal", "Clock", "ALL"]:
            rb = tk.Radiobutton(algo_frame, text=algo, variable=self.algo_var, 
                               value=algo, bg=self.COLORS['bg_medium'],
                               fg=self.COLORS['text_primary'], 
                               selectcolor=self.COLORS['bg_light'],
                               activebackground=self.COLORS['bg_medium'],
                               activeforeground=self.COLORS['accent'],
                               font=('Segoe UI', 10))
            rb.pack(side=tk.LEFT, padx=8)
    
    def _create_control_panel(self):
        """Create control buttons."""
        control_frame = tk.Frame(self.left_panel, bg=self.COLORS['bg_dark'])
        control_frame.pack(fill=tk.X, pady=10)
        
        # Run button
        self.run_btn = tk.Button(control_frame, text="▶ Run Simulation", 
                                command=self.run_simulation,
                                bg=self.COLORS['success'], fg='white',
                                font=('Segoe UI', 11, 'bold'),
                                relief=tk.FLAT, padx=20, pady=8,
                                cursor='hand2')
        self.run_btn.pack(side=tk.LEFT, padx=5)
        
        # Step button
        self.step_btn = tk.Button(control_frame, text="⏭ Step", 
                                 command=self.step_simulation,
                                 bg=self.COLORS['bg_light'], fg='white',
                                 font=('Segoe UI', 11, 'bold'),
                                 relief=tk.FLAT, padx=20, pady=8,
                                 cursor='hand2')
        self.step_btn.pack(side=tk.LEFT, padx=5)
        
        # Reset button
        self.reset_btn = tk.Button(control_frame, text="🔄 Reset", 
                                  command=self.reset_simulation,
                                  bg=self.COLORS['warning'], fg='black',
                                  font=('Segoe UI', 11, 'bold'),
                                  relief=tk.FLAT, padx=20, pady=8,
                                  cursor='hand2')
        self.reset_btn.pack(side=tk.LEFT, padx=5)
        
        # Compare button
        self.compare_btn = tk.Button(control_frame, text="📊 Compare All", 
                                    command=self.compare_algorithms,
                                    bg=self.COLORS['accent'], fg='white',
                                    font=('Segoe UI', 11, 'bold'),
                                    relief=tk.FLAT, padx=20, pady=8,
                                    cursor='hand2')
        self.compare_btn.pack(side=tk.LEFT, padx=5)
        
        # Export button
        self.export_btn = tk.Button(control_frame, text="💾 Export TXT", 
                                   command=self.export_results,
                                   bg='#6c5ce7', fg='white',
                                   font=('Segoe UI', 11, 'bold'),
                                   relief=tk.FLAT, padx=20, pady=8,
                                   cursor='hand2')
        self.export_btn.pack(side=tk.LEFT, padx=5)
    
    def _create_visualization_area(self):
        """Create the visualization area with frame display and step table."""
        viz_frame = tk.Frame(self.left_panel, bg=self.COLORS['bg_medium'])
        viz_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Title
        viz_title = tk.Label(viz_frame, text="📺 Step-by-Step Visualization", 
                            bg=self.COLORS['bg_medium'], fg=self.COLORS['text_primary'],
                            font=('Segoe UI', 12, 'bold'))
        viz_title.pack(anchor=tk.W, padx=15, pady=10)
        
        # Current frame display
        self.frame_display = tk.Frame(viz_frame, bg=self.COLORS['bg_medium'])
        self.frame_display.pack(fill=tk.X, padx=15, pady=5)
        
        # Step indicator
        self.step_label = tk.Label(viz_frame, text="Step: 0 / 0", 
                                  bg=self.COLORS['bg_medium'], fg=self.COLORS['text_secondary'],
                                  font=('Segoe UI', 10))
        self.step_label.pack(anchor=tk.W, padx=15)
        
        # Current page info
        self.current_page_label = tk.Label(viz_frame, text="", 
                                          bg=self.COLORS['bg_medium'], 
                                          fg=self.COLORS['text_primary'],
                                          font=('Segoe UI', 11))
        self.current_page_label.pack(anchor=tk.W, padx=15, pady=5)
        
        # Results table
        table_title = tk.Label(viz_frame, text="📋 Simulation Results Table", 
                              bg=self.COLORS['bg_medium'], fg=self.COLORS['text_primary'],
                              font=('Segoe UI', 12, 'bold'))
        table_title.pack(anchor=tk.W, padx=15, pady=(15, 5))
        
        # Create Treeview for results
        table_frame = tk.Frame(viz_frame, bg=self.COLORS['bg_medium'])
        table_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.results_tree = ttk.Treeview(table_frame, 
                                         columns=('step', 'page', 'frames', 'status'),
                                         show='headings',
                                         yscrollcommand=scrollbar.set)
        
        self.results_tree.heading('step', text='Step')
        self.results_tree.heading('page', text='Page')
        self.results_tree.heading('frames', text='Frames')
        self.results_tree.heading('status', text='Status')
        
        self.results_tree.column('step', width=60, anchor=tk.CENTER)
        self.results_tree.column('page', width=80, anchor=tk.CENTER)
        self.results_tree.column('frames', width=200, anchor=tk.CENTER)
        self.results_tree.column('status', width=120, anchor=tk.CENTER)
        
        self.results_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.results_tree.yview)
        
        # Configure tags for coloring
        self.results_tree.tag_configure('hit', background='#1a472a', foreground='#00d9a5')
        self.results_tree.tag_configure('fault', background='#4a1a1a', foreground='#ff6b6b')
    
    def _create_metrics_panel(self):
        """Create the metrics and comparison panel."""
        metrics_frame = tk.Frame(self.right_panel, bg=self.COLORS['bg_medium'], 
                                width=350)
        metrics_frame.pack(fill=tk.BOTH, expand=True)
        metrics_frame.pack_propagate(False)
        
        # Title
        metrics_title = tk.Label(metrics_frame, text="📊 Performance Metrics", 
                                bg=self.COLORS['bg_medium'], fg=self.COLORS['text_primary'],
                                font=('Segoe UI', 14, 'bold'))
        metrics_title.pack(pady=15)
        
        # Stats container
        stats_frame = tk.Frame(metrics_frame, bg=self.COLORS['bg_medium'])
        stats_frame.pack(fill=tk.X, padx=15)
        
        # Page Faults
        self._create_stat_card(stats_frame, "Page Faults", "0", 
                              self.COLORS['fault'], 'faults')
        
        # Page Hits
        self._create_stat_card(stats_frame, "Page Hits", "0", 
                              self.COLORS['success'], 'hits')
        
        # Hit Ratio
        self._create_stat_card(stats_frame, "Hit Ratio", "0%", 
                              self.COLORS['warning'], 'ratio')
        
        # Algorithm label
        self.algo_label = tk.Label(metrics_frame, text="Algorithm: -", 
                                  bg=self.COLORS['bg_medium'], 
                                  fg=self.COLORS['text_secondary'],
                                  font=('Segoe UI', 10))
        self.algo_label.pack(pady=10)
        
        # Comparison results area
        comparison_title = tk.Label(metrics_frame, text="📈 Comparison Results", 
                                   bg=self.COLORS['bg_medium'], 
                                   fg=self.COLORS['text_primary'],
                                   font=('Segoe UI', 12, 'bold'))
        comparison_title.pack(pady=(20, 10))
        
        self.comparison_text = scrolledtext.ScrolledText(metrics_frame, 
                                                         height=10, width=35,
                                                         bg=self.COLORS['bg_light'],
                                                         fg=self.COLORS['text_primary'],
                                                         font=('Consolas', 9),
                                                         relief=tk.FLAT)
        self.comparison_text.pack(padx=15, pady=5, fill=tk.X)
    
    def _create_stat_card(self, parent, label: str, value: str, color: str, attr_name: str):
        """Create a statistics card widget."""
        card = tk.Frame(parent, bg=self.COLORS['bg_light'], relief=tk.FLAT)
        card.pack(fill=tk.X, pady=5)
        
        inner = tk.Frame(card, bg=self.COLORS['bg_light'])
        inner.pack(fill=tk.X, padx=15, pady=10)
        
        lbl = tk.Label(inner, text=label, bg=self.COLORS['bg_light'], 
                      fg=self.COLORS['text_secondary'], font=('Segoe UI', 9))
        lbl.pack(anchor=tk.W)
        
        val_label = tk.Label(inner, text=value, bg=self.COLORS['bg_light'], 
                            fg=color, font=('Segoe UI', 24, 'bold'))
        val_label.pack(anchor=tk.W)
        
        # Store reference for updating
        setattr(self, f'stat_{attr_name}', val_label)
    
    def _update_frame_display(self, frames: List[int], num_frames: int, 
                              is_fault: bool, replaced: Optional[int] = None):
        """Update the visual frame display."""
        # Clear current display
        for widget in self.frame_display.winfo_children():
            widget.destroy()
        
        # Create frame boxes
        for i in range(num_frames):
            box = tk.Frame(self.frame_display, width=60, height=60, 
                          relief=tk.FLAT, bd=2)
            box.pack_propagate(False)
            box.pack(side=tk.LEFT, padx=5)
            
            if i < len(frames):
                # Frame has content
                color = self.COLORS['fault'] if is_fault else self.COLORS['success']
                if replaced is not None and i < len(frames) and frames[i] == replaced:
                    color = self.COLORS['warning']
                
                box.configure(bg=color)
                label = tk.Label(box, text=str(frames[i]), 
                               bg=color, fg='white',
                               font=('Segoe UI', 18, 'bold'))
                label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            else:
                # Empty frame
                box.configure(bg=self.COLORS['frame_empty'])
                label = tk.Label(box, text="-", 
                               bg=self.COLORS['frame_empty'], 
                               fg=self.COLORS['text_secondary'],
                               font=('Segoe UI', 18))
                label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
    def _validate_input(self) -> bool:
        """Validate user input."""
        # Validate reference string
        ref_str = self.ref_entry.get()
        valid, pages, error = self.engine.validate_reference_string(ref_str)
        if not valid:
            messagebox.showerror("Input Error", error)
            return False
        
        self.reference_string = pages
        
        # Validate frame count
        try:
            self.num_frames = int(self.frame_spinbox.get())
            valid, error = self.engine.validate_frame_count(self.num_frames)
            if not valid:
                messagebox.showerror("Input Error", error)
                return False
        except ValueError:
            messagebox.showerror("Input Error", "Frame count must be a number")
            return False
        
        return True
    
    def run_simulation(self):
        """Run the complete simulation."""
        if not self._validate_input():
            return
        
        self.reset_simulation()
        algo = self.algo_var.get()
        
        if algo == "FIFO":
            self.results = self.engine.run_fifo(self.reference_string, self.num_frames)
            self.algo_label.config(text="Algorithm: FIFO")
        elif algo == "LRU":
            self.results = self.engine.run_lru(self.reference_string, self.num_frames)
            self.algo_label.config(text="Algorithm: LRU")
        elif algo == "Optimal":
            self.results = self.engine.run_optimal(self.reference_string, self.num_frames)
            self.algo_label.config(text="Algorithm: Optimal")
        elif algo == "Clock":
            self.results = self.engine.run_clock(self.reference_string, self.num_frames)
            self.algo_label.config(text="Algorithm: Clock")
        elif algo == "LFU":
            self.results = self.engine.run_lfu(self.reference_string, self.num_frames)
            self.algo_label.config(text="Algorithm: LFU")
        else:
            # Run all and show comparison
            self.compare_algorithms()
            return
        
        # Display all results
        self._display_all_results()
        self._update_metrics()
    
    def _display_all_results(self):
        """Display all simulation results in the table."""
        # Clear table
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Add results
        for i, result in enumerate(self.results):
            status = "❌ FAULT" if result.is_fault else "✅ HIT"
            frames_str = str(result.frames)
            tag = 'fault' if result.is_fault else 'hit'
            
            self.results_tree.insert('', 'end', 
                                    values=(i+1, result.page, frames_str, status),
                                    tags=(tag,))
        
        # Update frame display with final state
        if self.results:
            last = self.results[-1]
            self._update_frame_display(last.frames, self.num_frames, 
                                       last.is_fault, last.replaced_page)
            self.step_label.config(text=f"Step: {len(self.results)} / {len(self.results)}")
            self.current_step = len(self.results)
    
    def step_simulation(self):
        """Execute one step of the simulation."""
        if not self.results:
            if not self._validate_input():
                return
            
            algo = self.algo_var.get()
            if algo == "ALL":
                algo = "FIFO"  # Default to FIFO for stepping
                self.algo_var.set("FIFO")
            
            if algo == "FIFO":
                self.results = self.engine.run_fifo(self.reference_string, self.num_frames)
                self.algo_label.config(text="Algorithm: FIFO")
            elif algo == "LRU":
                self.results = self.engine.run_lru(self.reference_string, self.num_frames)
                self.algo_label.config(text="Algorithm: LRU")
            elif algo == "Clock":
                self.results = self.engine.run_clock(self.reference_string, self.num_frames)
                self.algo_label.config(text="Algorithm: Clock")
            elif algo == "LFU":
                self.results = self.engine.run_lfu(self.reference_string, self.num_frames)
                self.algo_label.config(text="Algorithm: LFU")
            else:
                self.results = self.engine.run_optimal(self.reference_string, self.num_frames)
                self.algo_label.config(text="Algorithm: Optimal")
        
        if self.current_step < len(self.results):
            result = self.results[self.current_step]
            
            # Update step counter
            self.current_step += 1
            self.step_label.config(text=f"Step: {self.current_step} / {len(self.results)}")
            
            # Update current page info
            status = "❌ PAGE FAULT" if result.is_fault else "✅ PAGE HIT"
            self.current_page_label.config(
                text=f"Accessing Page: {result.page} → {status}",
                fg=self.COLORS['fault'] if result.is_fault else self.COLORS['success']
            )
            
            # Update frame display
            self._update_frame_display(result.frames, self.num_frames, 
                                       result.is_fault, result.replaced_page)
            
            # Add to table
            status_text = "❌ FAULT" if result.is_fault else "✅ HIT"
            tag = 'fault' if result.is_fault else 'hit'
            self.results_tree.insert('', 'end',
                                    values=(self.current_step, result.page, 
                                           str(result.frames), status_text),
                                    tags=(tag,))
            
            # Scroll to latest
            children = self.results_tree.get_children()
            if children:
                self.results_tree.see(children[-1])
            
            # Update metrics
            self._update_metrics_partial()
    
    def _update_metrics(self):
        """Update the metrics display."""
        stats = self.engine.get_statistics()
        self.stat_faults.config(text=str(stats['page_faults']))
        self.stat_hits.config(text=str(stats['page_hits']))
        self.stat_ratio.config(text=f"{stats['hit_ratio']}%")
    
    def _update_metrics_partial(self):
        """Update metrics based on current step."""
        faults = sum(1 for r in self.results[:self.current_step] if r.is_fault)
        hits = self.current_step - faults
        ratio = (hits / self.current_step * 100) if self.current_step > 0 else 0
        
        self.stat_faults.config(text=str(faults))
        self.stat_hits.config(text=str(hits))
        self.stat_ratio.config(text=f"{ratio:.1f}%")
    
    def reset_simulation(self):
        """Reset the simulation state."""
        self.current_step = 0
        self.results = []
        
        # Clear table
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Reset displays
        self.step_label.config(text="Step: 0 / 0")
        self.current_page_label.config(text="")
        self.stat_faults.config(text="0")
        self.stat_hits.config(text="0")
        self.stat_ratio.config(text="0%")
        self.algo_label.config(text="Algorithm: -")
        
        # Clear frame display
        for widget in self.frame_display.winfo_children():
            widget.destroy()
        
        # Initialize empty frames
        self._update_frame_display([], int(self.frame_spinbox.get() or 3), False)
    
    def compare_algorithms(self):
        """Run all algorithms and show comparison."""
        if not self._validate_input():
            return
        
        self.metrics.clear_results()
        
        # Run FIFO
        fifo_results = self.engine.run_fifo(self.reference_string, self.num_frames)
        stats = self.engine.get_statistics()
        self.metrics.add_result('FIFO', stats['page_faults'], stats['page_hits'])
        self.all_results['FIFO'] = fifo_results
        
        # Run LRU
        lru_results = self.engine.run_lru(self.reference_string, self.num_frames)
        stats = self.engine.get_statistics()
        self.metrics.add_result('LRU', stats['page_faults'], stats['page_hits'])
        self.all_results['LRU'] = lru_results
        
        # Run Optimal
        optimal_results = self.engine.run_optimal(self.reference_string, self.num_frames)
        stats = self.engine.get_statistics()
        self.metrics.add_result('Optimal', stats['page_faults'], stats['page_hits'])
        self.all_results['Optimal'] = optimal_results
        
        # Run Clock
        clock_results = self.engine.run_clock(self.reference_string, self.num_frames)
        stats = self.engine.get_statistics()
        self.metrics.add_result('Clock', stats['page_faults'], stats['page_hits'])
        self.all_results['Clock'] = clock_results
        
        # Run LFU
        lfu_results = self.engine.run_lfu(self.reference_string, self.num_frames)
        stats = self.engine.get_statistics()
        self.metrics.add_result('LFU', stats['page_faults'], stats['page_hits'])
        self.all_results['LFU'] = lfu_results
        
        # Update comparison text
        self.comparison_text.delete(1.0, tk.END)
        report = self.metrics.generate_report(self.reference_string, self.num_frames)
        self.comparison_text.insert(tk.END, report)
        
        # Show chart in new window
        self._show_comparison_chart()
    
    def _show_comparison_chart(self):
        """Show the comparison bar chart in a new window."""
        chart_window = tk.Toplevel(self.root)
        chart_window.title("📊 Algorithm Comparison Chart")
        chart_window.geometry("800x500")
        chart_window.configure(bg=self.COLORS['bg_dark'])
        
        # Create matplotlib figure
        fig = self.metrics.create_comparison_chart()
        
        if fig:
            # Embed in Tkinter
            canvas = FigureCanvasTkAgg(fig, master=chart_window)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def export_results(self):
        """Export simulation results to a TXT file."""
        if not self._validate_input():
            return
        
        # Make sure we have results by running comparison
        if not self.all_results:
            self.compare_algorithms()
        
        # Ask user for save location
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Simulation Results",
            initialfile="simulation_results.txt"
        )
        
        if not filename:
            return  # User cancelled
        
        try:
            # Export using metrics module
            saved_path = self.metrics.export_to_txt(
                self.reference_string, 
                self.num_frames,
                self.all_results,
                filename
            )
            messagebox.showinfo("Export Successful", 
                              f"Results saved to:\n{saved_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to save file:\n{str(e)}")
    
    def generate_random(self):
        """Generate a random reference string."""
        try:
            # Get current frame count for appropriate page range
            num_frames = int(self.frame_spinbox.get() or 3)
            max_page = num_frames + 3  # Slightly more pages than frames
            
            # Generate random reference string with locality
            random_ref = self.engine.generate_locality_reference(
                length=20, 
                max_page=max_page,
                locality_factor=0.5  # 50% chance of locality
            )
            
            # Update the entry field
            self.ref_entry.delete(0, tk.END)
            self.ref_entry.insert(0, ','.join(map(str, random_ref)))
            
            # Reset simulation
            self.reset_simulation()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate: {str(e)}")


def run_gui():
    """Run the GUI application."""
    root = tk.Tk()
    app = PageReplacementGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
