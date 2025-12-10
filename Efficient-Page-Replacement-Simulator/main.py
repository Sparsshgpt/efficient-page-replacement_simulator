"""
Efficient Page Replacement Algorithm Simulator
===============================================

A Python-based simulator to test and compare different page replacement algorithms:
- FIFO (First-In-First-Out)
- LRU (Least Recently Used)
- Optimal (Belady's Algorithm)

Features:
- Interactive GUI with step-by-step visualization
- Color-coded page faults and hits
- Performance metrics (page faults, hits, hit ratio)
- Algorithm comparison with bar charts

Usage:
    python main.py          # Launch GUI
    python main.py --console  # Console mode (for testing)

Modules:
    1. modules/simulation_engine.py - Input handling and algorithm implementation
    2. modules/visualization.py     - Tkinter GUI for visualization
    3. modules/metrics.py           - Performance metrics and comparison

Author: OS Project
Date: December 2024
"""

import sys
from modules.simulation_engine import SimulationEngine
from modules.metrics import MetricsCalculator


def run_console_mode():
    """Run simulator in console mode for quick testing."""
    print("=" * 70)
    print("EFFICIENT PAGE REPLACEMENT ALGORITHM SIMULATOR")
    print("Console Mode")
    print("=" * 70)
    
    # Get input
    print("\nEnter reference string (comma-separated, e.g., 7,0,1,2,0,3,0,4,2,3):")
    ref_input = input("> ").strip()
    
    if not ref_input:
        # Use default
        ref_input = "7,0,1,2,0,3,0,4,2,3,0,3,2,1,2,0,1,7,0,1"
        print(f"Using default: {ref_input}")
    
    print("\nEnter number of frames (1-10):")
    frame_input = input("> ").strip()
    
    try:
        num_frames = int(frame_input) if frame_input else 3
    except ValueError:
        num_frames = 3
        print(f"Using default: {num_frames}")
    
    # Validate input
    engine = SimulationEngine()
    valid, reference_string, error = engine.validate_reference_string(ref_input)
    
    if not valid:
        print(f"\n❌ Error: {error}")
        return
    
    valid, error = engine.validate_frame_count(num_frames)
    if not valid:
        print(f"\n❌ Error: {error}")
        return
    
    print(f"\n📋 Reference String: {reference_string}")
    print(f"🖼️  Number of Frames: {num_frames}")
    print(f"📊 Total References: {len(reference_string)}")
    
    # Initialize metrics
    metrics = MetricsCalculator()
    
    # Run all algorithms
    algorithms = [
        ("FIFO", engine.run_fifo),
        ("LRU", engine.run_lru),
        ("Optimal", engine.run_optimal)
    ]
    
    for algo_name, algo_func in algorithms:
        print(f"\n{'='*40}")
        print(f"🔄 {algo_name} Algorithm")
        print("="*40)
        
        results = algo_func(reference_string, num_frames)
        stats = engine.get_statistics()
        
        # Store for comparison
        metrics.add_result(algo_name, stats['page_faults'], stats['page_hits'])
        
        # Print step-by-step results
        print(f"\n{'Step':<6} {'Page':<8} {'Frames':<25} {'Status':<10}")
        print("-" * 55)
        
        for i, result in enumerate(results):
            status = "❌ FAULT" if result.is_fault else "✅ HIT"
            frames_str = str(result.frames)
            print(f"{i+1:<6} {result.page:<8} {frames_str:<25} {status}")
        
        print("-" * 55)
        print(f"📊 Page Faults: {stats['page_faults']} | Page Hits: {stats['page_hits']} | Hit Ratio: {stats['hit_ratio']}%")
    
    # Show comparison
    print(metrics.generate_report(reference_string, num_frames))
    
    # Ask to show chart
    print("\nShow comparison chart? (y/n)")
    show_chart = input("> ").strip().lower()
    
    if show_chart == 'y':
        import matplotlib.pyplot as plt
        metrics.create_comparison_chart()
        plt.show()


def run_gui_mode():
    """Run simulator in GUI mode."""
    from modules.visualization import run_gui
    run_gui()


def main():
    """Main entry point."""
    # Check for console mode flag
    if len(sys.argv) > 1 and sys.argv[1] == "--console":
        run_console_mode()
    else:
        # Default: GUI mode
        run_gui_mode()


if __name__ == "__main__":
    main()
