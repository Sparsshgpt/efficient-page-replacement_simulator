"""
Module 3: Metrics and Comparison
================================
Purpose: Calculate and present performance metrics for page replacement algorithms.

Features:
- Page faults and hits count
- Hit ratio calculation
- Algorithm comparison summary
- Bar chart visualization using matplotlib
"""

from typing import Dict, List
import matplotlib.pyplot as plt
from matplotlib.figure import Figure


class MetricsCalculator:
    """
    Calculates and stores performance metrics for algorithm comparison.
    
    Responsibilities:
    - Store results from multiple algorithm runs
    - Calculate comparative statistics
    - Generate comparison tables and charts
    """
    
    def __init__(self):
        self.algorithm_results: Dict[str, Dict] = {}
    
    def add_result(self, algorithm_name: str, page_faults: int, page_hits: int):
        """
        Store results from an algorithm run.
        
        Args:
            algorithm_name: Name of the algorithm (FIFO, LRU, Optimal)
            page_faults: Number of page faults
            page_hits: Number of page hits
        """
        total = page_faults + page_hits
        hit_ratio = (page_hits / total * 100) if total > 0 else 0
        fault_ratio = (page_faults / total * 100) if total > 0 else 0
        
        self.algorithm_results[algorithm_name] = {
            'page_faults': page_faults,
            'page_hits': page_hits,
            'total_references': total,
            'hit_ratio': round(hit_ratio, 2),
            'fault_ratio': round(fault_ratio, 2)
        }
    
    def clear_results(self):
        """Clear all stored results."""
        self.algorithm_results.clear()
    
    def get_comparison_table(self) -> str:
        """
        Generate a formatted comparison table string.
        
        Returns:
            Formatted string table comparing all algorithms
        """
        if not self.algorithm_results:
            return "No results to compare."
        
        # Header
        table = "\n" + "=" * 70 + "\n"
        table += "ALGORITHM COMPARISON TABLE\n"
        table += "=" * 70 + "\n"
        table += f"{'Algorithm':<15} {'Page Faults':<15} {'Page Hits':<15} {'Hit Ratio':<15}\n"
        table += "-" * 70 + "\n"
        
        # Data rows
        for algo_name, stats in self.algorithm_results.items():
            table += f"{algo_name:<15} {stats['page_faults']:<15} {stats['page_hits']:<15} {stats['hit_ratio']:.2f}%\n"
        
        table += "=" * 70 + "\n"
        
        # Find best algorithm
        if len(self.algorithm_results) > 1:
            best_algo = min(self.algorithm_results.items(), key=lambda x: x[1]['page_faults'])
            table += f"\n>>> Best Algorithm: {best_algo[0]} (Only {best_algo[1]['page_faults']} page faults)\n"
        
        return table
    
    def get_summary_data(self) -> List[Dict]:
        """
        Get summary data for all algorithms.
        
        Returns:
            List of dictionaries with algorithm statistics
        """
        summary = []
        for algo_name, stats in self.algorithm_results.items():
            summary.append({
                'algorithm': algo_name,
                **stats
            })
        return summary
    
    def create_comparison_chart(self) -> Figure:
        """
        Create a matplotlib bar chart comparing algorithms.
        
        Returns:
            matplotlib Figure object
        """
        if not self.algorithm_results:
            return None
        
        algorithms = list(self.algorithm_results.keys())
        page_faults = [self.algorithm_results[a]['page_faults'] for a in algorithms]
        page_hits = [self.algorithm_results[a]['page_hits'] for a in algorithms]
        
        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        fig.suptitle('Page Replacement Algorithm Comparison', fontsize=14, fontweight='bold')
        
        # Color scheme
        colors_faults = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        colors_hits = ['#95E1D3', '#F38181', '#FCE38A']
        
        # Bar chart 1: Page Faults
        bars1 = ax1.bar(algorithms, page_faults, color=colors_faults[:len(algorithms)], 
                        edgecolor='black', linewidth=1.2)
        ax1.set_ylabel('Count', fontsize=11)
        ax1.set_title('Page Faults Comparison', fontsize=12, fontweight='bold')
        ax1.set_ylim(0, max(page_faults) * 1.2)
        
        # Add value labels on bars
        for bar, val in zip(bars1, page_faults):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3, 
                    str(val), ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        # Bar chart 2: Hit Ratio
        hit_ratios = [self.algorithm_results[a]['hit_ratio'] for a in algorithms]
        bars2 = ax2.bar(algorithms, hit_ratios, color=colors_hits[:len(algorithms)], 
                        edgecolor='black', linewidth=1.2)
        ax2.set_ylabel('Percentage (%)', fontsize=11)
        ax2.set_title('Hit Ratio Comparison', fontsize=12, fontweight='bold')
        ax2.set_ylim(0, 100)
        
        # Add value labels on bars
        for bar, val in zip(bars2, hit_ratios):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                    f'{val:.1f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        plt.tight_layout()
        return fig
    
    def save_chart(self, filename: str = 'comparison_chart.png'):
        """Save the comparison chart to a file."""
        fig = self.create_comparison_chart()
        if fig:
            fig.savefig(filename, dpi=150, bbox_inches='tight')
            plt.close(fig)
            print(f"Chart saved to {filename}")
    
    def generate_report(self, reference_string: List[int], num_frames: int) -> str:
        """
        Generate a complete text report.
        
        Args:
            reference_string: The page reference string used
            num_frames: Number of memory frames
        
        Returns:
            Formatted report string
        """
        report = "\n" + "=" * 70 + "\n"
        report += "PAGE REPLACEMENT ALGORITHM COMPARISON REPORT\n"
        report += "=" * 70 + "\n\n"
        
        report += f"Reference String: {reference_string}\n"
        report += f"Number of Frames: {num_frames}\n"
        report += f"Total Page References: {len(reference_string)}\n\n"
        
        report += self.get_comparison_table()
        
        # Analysis
        if len(self.algorithm_results) >= 3:
            fifo_faults = self.algorithm_results.get('FIFO', {}).get('page_faults', 0)
            lru_faults = self.algorithm_results.get('LRU', {}).get('page_faults', 0)
            optimal_faults = self.algorithm_results.get('Optimal', {}).get('page_faults', 0)
            
            report += "\n[ANALYSIS]\n"
            report += "-" * 40 + "\n"
            
            if optimal_faults > 0:
                fifo_overhead = ((fifo_faults - optimal_faults) / optimal_faults) * 100
                lru_overhead = ((lru_faults - optimal_faults) / optimal_faults) * 100
                
                report += f"* FIFO has {fifo_overhead:.1f}% more faults than Optimal\n"
                report += f"* LRU has {lru_overhead:.1f}% more faults than Optimal\n"
                report += f"* LRU is {'better' if lru_faults < fifo_faults else 'worse'} than FIFO by {abs(fifo_faults - lru_faults)} fault(s)\n"
        
        report += "\n" + "=" * 70 + "\n"
        return report
    
    def export_to_txt(self, reference_string: List[int], num_frames: int, 
                      step_results: Dict[str, List] = None, filename: str = None) -> str:
        """
        Export simulation results to a TXT file.
        
        Args:
            reference_string: The page reference string used
            num_frames: Number of memory frames
            step_results: Dict mapping algorithm name to list of step results
            filename: Output filename (auto-generated if None)
        
        Returns:
            Path to the saved file
        """
        import os
        from datetime import datetime
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"simulation_results_{timestamp}.txt"
        
        # Build content
        content = []
        content.append("=" * 70)
        content.append("PAGE REPLACEMENT ALGORITHM SIMULATION RESULTS")
        content.append("=" * 70)
        content.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        content.append(f"\nReference String: {', '.join(map(str, reference_string))}")
        content.append(f"Number of Frames: {num_frames}")
        content.append(f"Total Page References: {len(reference_string)}")
        
        # Add step-by-step results for each algorithm
        if step_results:
            for algo_name, results in step_results.items():
                content.append("\n" + "-" * 70)
                content.append(f"{algo_name} ALGORITHM - Step by Step")
                content.append("-" * 70)
                content.append(f"{'Step':<6} {'Page':<8} {'Frames':<30} {'Status':<10}")
                content.append("-" * 60)
                
                for i, result in enumerate(results):
                    status = "FAULT" if result.is_fault else "HIT"
                    frames_str = str(result.frames)
                    content.append(f"{i+1:<6} {result.page:<8} {frames_str:<30} {status}")
        
        # Add comparison table
        content.append("\n")
        content.append(self.get_comparison_table())
        
        # Add analysis
        content.append(self.generate_report(reference_string, num_frames))
        
        # Write to file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))
        
        return os.path.abspath(filename)


# ==================== STANDALONE TEST ====================

if __name__ == "__main__":
    # Test the metrics module
    metrics = MetricsCalculator()
    
    # Add sample results
    metrics.add_result('FIFO', page_faults=15, page_hits=5)
    metrics.add_result('LRU', page_faults=12, page_hits=8)
    metrics.add_result('Optimal', page_faults=9, page_hits=11)
    
    # Print comparison table
    print(metrics.get_comparison_table())
    
    # Generate full report
    ref_string = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
    print(metrics.generate_report(ref_string, 3))
    
    # Create and show chart
    fig = metrics.create_comparison_chart()
    if fig:
        plt.show()
