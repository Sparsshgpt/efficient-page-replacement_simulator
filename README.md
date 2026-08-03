# Efficient Page Replacement Algorithm Simulator

A Python-based simulator that allows users to test and compare different page replacement algorithms (FIFO, LRU, LFU, Optimal, Clock) with visualizations and performance metrics.

## 📁 Project Structure

```
Efficient Page Replacement Simulator/
├── main.py                 # Main application entry point
├── modules/
│   ├── __init__.py
│   ├── simulation_engine.py    # Module 1: Input & Algorithms
│   ├── visualization.py        # Module 2: GUI Visualization
│   └── metrics.py              # Module 3: Performance Metrics
├── requirements.txt
└── README.md
```

## 🚀 How to Run

1. Make sure you have Python 3.x installed
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the simulator:
   ```
   python main.py
   ```

## 🎯 Features

### Algorithms (5 Total)
- **FIFO**: First-In-First-Out page replacement
- **LRU**: Least Recently Used page replacement  
- **LFU**: Least Frequently Used (tracks access count)
- **Optimal**: Belady's optimal page replacement
- **Clock**: Second Chance algorithm (real OS algorithm)

### Visualization
- Step-by-step frame visualization
- Color-coded faults (red) and hits (green)
- Performance metrics dashboard
- Algorithm comparison with bar charts

### Utilities
- 🎲 Random Reference Generator (with locality)
- 💾 Export results to TXT file

## 📊 Test Cases

| Frames | FIFO | LRU | LFU | Optimal | Clock |
|--------|------|-----|-----|---------|-------|
| 3      | 15   | 12  | ~13 | 9       | ~12-14 |

Reference String: `7,0,1,2,0,3,0,4,2,3,0,3,2,1,2,0,1,7,0,1`

## 👨‍💻 Author

Created for Operating Systems CA2 Project
Sparsh Gupta (12415691)
Lakshya Pandey(12408450)
Kushagra Chouhan(12408848)

---
## 📄 License

This project is licensed under the **MIT License**.

You are free to use, modify, and distribute this project for personal or commercial purposes, provided that the original copyright and license notice are included.

For more details, see the [LICENSE](LICENSE) file.

