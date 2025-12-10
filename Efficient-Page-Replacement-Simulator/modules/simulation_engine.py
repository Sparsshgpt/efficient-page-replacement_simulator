"""
Module 1: Input and Simulation Engine
======================================
Purpose: Handle user input validation and run page replacement algorithms.

Algorithms Implemented:
- FIFO (First-In-First-Out)
- LRU (Least Recently Used)
- Optimal (Belady's Algorithm)
"""

from collections import deque
from typing import List, Tuple, Dict


class SimulationResult:
    """Stores the result of a single simulation step."""
    
    def __init__(self, page: int, frames: List[int], is_fault: bool, replaced_page: int = None):
        self.page = page                    # Current page being accessed
        self.frames = frames.copy()         # State of frames after this step
        self.is_fault = is_fault            # True if page fault occurred
        self.replaced_page = replaced_page  # Page that was replaced (if any)
    
    def __repr__(self):
        status = "FAULT" if self.is_fault else "HIT"
        return f"Page {self.page}: {self.frames} [{status}]"


class SimulationEngine:
    """
    Core simulation engine for page replacement algorithms.
    
    Responsibilities:
    - Validate input reference string and frame count
    - Execute FIFO, LRU, and Optimal algorithms
    - Track step-by-step results for visualization
    """
    
    def __init__(self):
        self.results: List[SimulationResult] = []
        self.page_faults = 0
        self.page_hits = 0
    
    # ==================== INPUT VALIDATION ====================
    
    @staticmethod
    def validate_reference_string(ref_string: str) -> Tuple[bool, List[int], str]:
        """
        Validate and parse the reference string.
        
        Args:
            ref_string: Comma-separated page numbers (e.g., "7,0,1,2,0,3")
        
        Returns:
            Tuple of (is_valid, parsed_list, error_message)
        """
        if not ref_string or not ref_string.strip():
            return False, [], "Reference string cannot be empty"
        
        try:
            # Parse comma or space separated values
            ref_string = ref_string.replace(" ", ",")
            pages = [int(x.strip()) for x in ref_string.split(",") if x.strip()]
            
            if not pages:
                return False, [], "No valid page numbers found"
            
            if any(p < 0 for p in pages):
                return False, [], "Page numbers must be non-negative"
            
            return True, pages, ""
            
        except ValueError:
            return False, [], "Invalid input: Please enter comma-separated integers"
    
    @staticmethod
    def validate_frame_count(frame_count: int) -> Tuple[bool, str]:
        """
        Validate the number of frames.
        
        Args:
            frame_count: Number of memory frames
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if frame_count < 1:
            return False, "Frame count must be at least 1"
        if frame_count > 10:
            return False, "Frame count should not exceed 10 for visualization"
        return True, ""
    
    # ==================== FIFO ALGORITHM ====================
    
    def run_fifo(self, reference_string: List[int], num_frames: int) -> List[SimulationResult]:
        """
        First-In-First-Out (FIFO) Page Replacement Algorithm.
        
        Logic: When a page fault occurs and frames are full,
               replace the page that was loaded first (oldest page).
        
        Uses a queue to track the order of page arrival.
        """
        self.results = []
        self.page_faults = 0
        self.page_hits = 0
        
        frames = []         # Current pages in memory
        queue = deque()     # Tracks order of arrival (FIFO order)
        
        for page in reference_string:
            if page in frames:
                # PAGE HIT: Page already in memory
                self.page_hits += 1
                self.results.append(SimulationResult(page, frames, is_fault=False))
            else:
                # PAGE FAULT: Page not in memory
                self.page_faults += 1
                replaced = None
                
                if len(frames) < num_frames:
                    # Frames not full: Simply add the page
                    frames.append(page)
                    queue.append(page)
                else:
                    # Frames full: Remove oldest (first in queue)
                    replaced = queue.popleft()
                    replace_idx = frames.index(replaced)
                    frames[replace_idx] = page
                    queue.append(page)
                
                self.results.append(SimulationResult(page, frames, is_fault=True, replaced_page=replaced))
        
        return self.results
    
    # ==================== LRU ALGORITHM ====================
    
    def run_lru(self, reference_string: List[int], num_frames: int) -> List[SimulationResult]:
        """
        Least Recently Used (LRU) Page Replacement Algorithm.
        
        Logic: When a page fault occurs and frames are full,
               replace the page that hasn't been used for the longest time.
        
        Uses a dictionary to track the last access time of each page.
        """
        self.results = []
        self.page_faults = 0
        self.page_hits = 0
        
        frames = []             # Current pages in memory
        last_used = {}          # Tracks last access time for each page
        
        for time, page in enumerate(reference_string):
            if page in frames:
                # PAGE HIT: Update last used time
                self.page_hits += 1
                last_used[page] = time
                self.results.append(SimulationResult(page, frames, is_fault=False))
            else:
                # PAGE FAULT
                self.page_faults += 1
                replaced = None
                
                if len(frames) < num_frames:
                    # Frames not full: Simply add the page
                    frames.append(page)
                else:
                    # Frames full: Find LRU page (smallest last_used time)
                    lru_page = min(frames, key=lambda p: last_used.get(p, -1))
                    replace_idx = frames.index(lru_page)
                    replaced = lru_page
                    frames[replace_idx] = page
                    del last_used[lru_page]
                
                last_used[page] = time
                self.results.append(SimulationResult(page, frames, is_fault=True, replaced_page=replaced))
        
        return self.results
    
    # ==================== OPTIMAL ALGORITHM ====================
    
    def run_optimal(self, reference_string: List[int], num_frames: int) -> List[SimulationResult]:
        """
        Optimal (Belady's) Page Replacement Algorithm.
        
        Logic: When a page fault occurs and frames are full,
               replace the page that will not be used for the longest time
               in the future (or never used again).
        
        This is the theoretical best - gives minimum page faults.
        """
        self.results = []
        self.page_faults = 0
        self.page_hits = 0
        
        frames = []
        
        for current_idx, page in enumerate(reference_string):
            if page in frames:
                # PAGE HIT
                self.page_hits += 1
                self.results.append(SimulationResult(page, frames, is_fault=False))
            else:
                # PAGE FAULT
                self.page_faults += 1
                replaced = None
                
                if len(frames) < num_frames:
                    # Frames not full: Simply add the page
                    frames.append(page)
                else:
                    # Frames full: Find page used furthest in future
                    future_use = {}
                    
                    for frame_page in frames:
                        # Look for next occurrence in future
                        try:
                            next_use = reference_string[current_idx + 1:].index(frame_page)
                            future_use[frame_page] = next_use
                        except ValueError:
                            # Page not used again - best candidate for replacement
                            future_use[frame_page] = float('inf')
                    
                    # Replace page with largest future use distance
                    victim_page = max(frames, key=lambda p: future_use[p])
                    replace_idx = frames.index(victim_page)
                    replaced = victim_page
                    frames[replace_idx] = page
                
                self.results.append(SimulationResult(page, frames, is_fault=True, replaced_page=replaced))
        
        return self.results
    
    # ==================== CLOCK (SECOND CHANCE) ALGORITHM ====================
    
    def run_clock(self, reference_string: List[int], num_frames: int) -> List[SimulationResult]:
        """
        Clock (Second Chance) Page Replacement Algorithm.
        
        Logic: Uses a circular queue with a reference bit for each page.
               When replacing, scan for a page with reference bit = 0.
               If reference bit = 1, give it a "second chance" by setting
               bit to 0 and moving the clock hand forward.
        
        This is a practical approximation of LRU used in real operating systems.
        """
        self.results = []
        self.page_faults = 0
        self.page_hits = 0
        
        frames = []             # Current pages in memory
        reference_bits = {}     # Reference bit for each page (0 or 1)
        clock_hand = 0          # Current position of clock hand
        
        for page in reference_string:
            if page in frames:
                # PAGE HIT: Set reference bit to 1 (recently used)
                self.page_hits += 1
                reference_bits[page] = 1
                self.results.append(SimulationResult(page, frames, is_fault=False))
            else:
                # PAGE FAULT
                self.page_faults += 1
                replaced = None
                
                if len(frames) < num_frames:
                    # Frames not full: Simply add the page
                    frames.append(page)
                    reference_bits[page] = 1
                else:
                    # Frames full: Use clock algorithm to find victim
                    while True:
                        current_page = frames[clock_hand]
                        
                        if reference_bits[current_page] == 0:
                            # Found a page to replace
                            replaced = current_page
                            frames[clock_hand] = page
                            del reference_bits[current_page]
                            reference_bits[page] = 1
                            clock_hand = (clock_hand + 1) % num_frames
                            break
                        else:
                            # Give second chance: set bit to 0
                            reference_bits[current_page] = 0
                            clock_hand = (clock_hand + 1) % num_frames
                
                self.results.append(SimulationResult(page, frames, is_fault=True, replaced_page=replaced))
        
        return self.results
    
    # ==================== LFU (LEAST FREQUENTLY USED) ALGORITHM ====================
    
    def run_lfu(self, reference_string: List[int], num_frames: int) -> List[SimulationResult]:
        """
        Least Frequently Used (LFU) Page Replacement Algorithm.
        
        Logic: When a page fault occurs and frames are full,
               replace the page with the lowest access count.
               If multiple pages have the same count, use FIFO as tiebreaker.
        
        Tracks how many times each page has been accessed.
        """
        self.results = []
        self.page_faults = 0
        self.page_hits = 0
        
        frames = []             # Current pages in memory
        frequency = {}          # Access count for each page
        arrival_time = {}       # Arrival time for FIFO tiebreaker
        
        for time, page in enumerate(reference_string):
            if page in frames:
                # PAGE HIT: Increment frequency
                self.page_hits += 1
                frequency[page] += 1
                self.results.append(SimulationResult(page, frames, is_fault=False))
            else:
                # PAGE FAULT
                self.page_faults += 1
                replaced = None
                
                if len(frames) < num_frames:
                    # Frames not full: Simply add the page
                    frames.append(page)
                else:
                    # Frames full: Find page with minimum frequency
                    # Use arrival_time as tiebreaker (FIFO among same frequency)
                    min_freq = min(frequency[p] for p in frames)
                    candidates = [p for p in frames if frequency[p] == min_freq]
                    
                    # Among candidates, pick the one that arrived first
                    victim_page = min(candidates, key=lambda p: arrival_time[p])
                    replace_idx = frames.index(victim_page)
                    replaced = victim_page
                    
                    # Remove victim's tracking data
                    del frequency[victim_page]
                    del arrival_time[victim_page]
                    
                    frames[replace_idx] = page
                
                # Initialize tracking for new page
                frequency[page] = 1
                arrival_time[page] = time
                self.results.append(SimulationResult(page, frames, is_fault=True, replaced_page=replaced))
        
        return self.results
    
    # ==================== RANDOM REFERENCE STRING GENERATOR ====================
    
    @staticmethod
    def generate_random_reference(length: int = 20, max_page: int = 9) -> List[int]:
        """
        Generate a random page reference string.
        
        Args:
            length: Number of page references to generate (default: 20)
            max_page: Maximum page number (0 to max_page, default: 9)
        
        Returns:
            List of random page numbers
        """
        import random
        return [random.randint(0, max_page) for _ in range(length)]
    
    @staticmethod
    def generate_locality_reference(length: int = 20, max_page: int = 9, 
                                    locality_factor: float = 0.7) -> List[int]:
        """
        Generate a reference string with locality of reference.
        
        Simulates real-world memory access patterns where recently accessed
        pages are more likely to be accessed again.
        
        Args:
            length: Number of page references to generate
            max_page: Maximum page number
            locality_factor: Probability of accessing a recent page (0.0-1.0)
        
        Returns:
            List of page numbers with locality pattern
        """
        import random
        
        result = []
        recent_pages = []
        
        for _ in range(length):
            if recent_pages and random.random() < locality_factor:
                # Access a recently used page
                page = random.choice(recent_pages[-5:])  # Last 5 pages
            else:
                # Access a random page
                page = random.randint(0, max_page)
            
            result.append(page)
            recent_pages.append(page)
        
        return result
    
    # ==================== HELPER METHODS ====================
    
    def get_statistics(self) -> Dict:
        """Return statistics from the last simulation run."""
        total = self.page_faults + self.page_hits
        hit_ratio = (self.page_hits / total * 100) if total > 0 else 0
        fault_ratio = (self.page_faults / total * 100) if total > 0 else 0
        
        return {
            'page_faults': self.page_faults,
            'page_hits': self.page_hits,
            'total_references': total,
            'hit_ratio': round(hit_ratio, 2),
            'fault_ratio': round(fault_ratio, 2)
        }


# ==================== STANDALONE TEST ====================

if __name__ == "__main__":
    # Test with standard reference string
    engine = SimulationEngine()
    ref_string = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
    num_frames = 3
    
    print("=" * 60)
    print("PAGE REPLACEMENT ALGORITHM SIMULATOR - Module 1 Test")
    print("=" * 60)
    print(f"\nReference String: {ref_string}")
    print(f"Number of Frames: {num_frames}")
    
    # Test FIFO
    print("\n" + "-" * 40)
    print("FIFO Algorithm:")
    print("-" * 40)
    results = engine.run_fifo(ref_string, num_frames)
    for r in results:
        print(r)
    stats = engine.get_statistics()
    print(f"\nPage Faults: {stats['page_faults']}, Hit Ratio: {stats['hit_ratio']}%")
    
    # Test LRU
    print("\n" + "-" * 40)
    print("LRU Algorithm:")
    print("-" * 40)
    results = engine.run_lru(ref_string, num_frames)
    for r in results:
        print(r)
    stats = engine.get_statistics()
    print(f"\nPage Faults: {stats['page_faults']}, Hit Ratio: {stats['hit_ratio']}%")
    
    # Test Optimal
    print("\n" + "-" * 40)
    print("Optimal Algorithm:")
    print("-" * 40)
    results = engine.run_optimal(ref_string, num_frames)
    for r in results:
        print(r)
    stats = engine.get_statistics()
    print(f"\nPage Faults: {stats['page_faults']}, Hit Ratio: {stats['hit_ratio']}%")
    
    # Test Clock
    print("\n" + "-" * 40)
    print("Clock (Second Chance) Algorithm:")
    print("-" * 40)
    results = engine.run_clock(ref_string, num_frames)
    for r in results:
        print(r)
    stats = engine.get_statistics()
    print(f"\nPage Faults: {stats['page_faults']}, Hit Ratio: {stats['hit_ratio']}%")

