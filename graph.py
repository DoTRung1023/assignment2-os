#!/usr/bin/env python3
"""
Complete Report Graph Generator
Creates all graphs needed for the Page Replacement Algorithm Performance Analysis Report
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import subprocess
import os

# Set consistent styling
plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 11
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['legend.fontsize'] = 10

# Color scheme
ALGORITHM_COLORS = {'rand': '#e74c3c', 'lru': '#3498db', 'clock': '#27ae60'}

def run_simulator(trace_file, frames, algorithm, mode='quiet'):
    """Run simulator and return results"""
    if frames <= 0 or algorithm not in ['rand', 'lru', 'clock']:
        return None
    
    try:
        result = subprocess.run([
            './memsim', trace_file, str(frames), algorithm, mode
        ], capture_output=True, text=True, timeout=60, 
          cwd='/Users/dotrung67/Documents/Adelaide/2025 Sem 2/OS/assignment2-os')
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            page_faults, disk_writes, fault_rate, events = 0, 0, 0.0, 0
            
            for line in lines:
                try:
                    if "events in trace:" in line:
                        events = int(line.split(":")[-1].strip())
                    elif "total disk reads:" in line:
                        page_faults = int(line.split(":")[-1].strip())
                    elif "total disk writes:" in line:
                        disk_writes = int(line.split(":")[-1].strip())
                    elif "page fault rate:" in line:
                        fault_rate = float(line.split(":")[-1].strip()) * 100
                except (ValueError, IndexError):
                    continue
            
            return {
                'frames': frames, 'algorithm': algorithm, 'page_faults': page_faults,
                'disk_writes': disk_writes, 'fault_rate': fault_rate, 'events': events
            }
        return None
    except:
        return None

def collect_trace_data(trace, frame_ranges):
    """Collect data for a specific trace across frame ranges"""
    results = []
    for frames in frame_ranges:
        for algorithm in ['rand', 'lru', 'clock']:
            result = run_simulator(f"{trace}.trace", frames, algorithm)
            if result:
                result['trace'] = trace
                results.append(result)
    return results

def plot_swim_analysis():
    """Generate swim trace analysis plots"""
    # Phase 1: Broad overview
    phase1_frames = [5, 10, 20, 50, 100, 200, 500, 1000]
    data = collect_trace_data('swim', phase1_frames)
    df = pd.DataFrame(data)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    for algorithm in ['rand', 'lru', 'clock']:
        alg_data = df[df['algorithm'] == algorithm].sort_values('frames')
        ax1.plot(alg_data['frames'], alg_data['fault_rate'], 'o-', 
                color=ALGORITHM_COLORS[algorithm], label=algorithm.upper(), 
                markersize=6, linewidth=2.5)
        ax2.plot(alg_data['frames'], alg_data['disk_writes'], 'o-',
                color=ALGORITHM_COLORS[algorithm], label=algorithm.upper(),
                markersize=6, linewidth=2.5)
    
    ax1.set_xlabel('Memory Size (Frames)')
    ax1.set_ylabel('Page Fault Rate (%)')
    ax1.set_title('SWIM - Page Fault Rate vs Frames (Phase 1)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xscale('log')
    
    ax2.set_xlabel('Memory Size (Frames)')
    ax2.set_ylabel('Total Disk Writes')
    ax2.set_title('SWIM - Disk Writes vs Frames (Phase 1)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_xscale('log')
    
    plt.tight_layout()
    plt.savefig('swim_phase1_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Phase 2: Detailed critical region
    phase2_frames = list(range(20, 101, 10)) + list(range(100, 201, 20))
    data2 = collect_trace_data('swim', phase2_frames)
    df2 = pd.DataFrame(data2)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    for algorithm in ['rand', 'lru', 'clock']:
        alg_data = df2[df2['algorithm'] == algorithm].sort_values('frames')
        ax1.plot(alg_data['frames'], alg_data['fault_rate'], 'o-',
                color=ALGORITHM_COLORS[algorithm], label=algorithm.upper(),
                markersize=6, linewidth=2.5)
        ax2.plot(alg_data['frames'], alg_data['disk_writes'], 'o-',
                color=ALGORITHM_COLORS[algorithm], label=algorithm.upper(),
                markersize=6, linewidth=2.5)
    
    ax1.set_xlabel('Memory Size (Frames)')
    ax1.set_ylabel('Page Fault Rate (%)')
    ax1.set_title('SWIM - Page Fault Rate vs Frames (Phase 2: Critical Region)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    ax2.set_xlabel('Memory Size (Frames)')
    ax2.set_ylabel('Total Disk Writes')
    ax2.set_title('SWIM - Disk Writes vs Frames (Phase 2: Critical Region)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('swim_phase2_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_bzip_analysis():
    """Generate bzip trace analysis plots"""
    phase1_frames = [2, 4, 8, 16, 24, 32, 48, 64, 96, 128]
    data = collect_trace_data('bzip', phase1_frames)
    df = pd.DataFrame(data)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    for algorithm in ['rand', 'lru', 'clock']:
        alg_data = df[df['algorithm'] == algorithm].sort_values('frames')
        ax1.plot(alg_data['frames'], alg_data['fault_rate'], 'o-',
                color=ALGORITHM_COLORS[algorithm], label=algorithm.upper(),
                markersize=6, linewidth=2.5)
        ax2.plot(alg_data['frames'], alg_data['disk_writes'], 'o-',
                color=ALGORITHM_COLORS[algorithm], label=algorithm.upper(),
                markersize=6, linewidth=2.5)
    
    ax1.set_xlabel('Memory Size (Frames)')
    ax1.set_ylabel('Page Fault Rate (%)')
    ax1.set_title('BZIP - Page Fault Rate vs Frames (Phase 1)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    ax2.set_xlabel('Memory Size (Frames)')
    ax2.set_ylabel('Total Disk Writes')
    ax2.set_title('BZIP - Disk Writes vs Frames (Phase 1)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('bzip_phase1_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Phase 2: Detailed view of critical region (8-24 frames)
    phase2_frames = list(range(8, 25, 2))
    data2 = collect_trace_data('bzip', phase2_frames)
    df2 = pd.DataFrame(data2)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    for algorithm in ['rand', 'lru', 'clock']:
        alg_data = df2[df2['algorithm'] == algorithm].sort_values('frames')
        ax1.plot(alg_data['frames'], alg_data['fault_rate'], 'o-',
                color=ALGORITHM_COLORS[algorithm], label=algorithm.upper(),
                markersize=6, linewidth=2.5)
        ax2.plot(alg_data['frames'], alg_data['disk_writes'], 'o-',
                color=ALGORITHM_COLORS[algorithm], label=algorithm.upper(),
                markersize=6, linewidth=2.5)
    
    ax1.set_xlabel('Memory Size (Frames)')
    ax1.set_ylabel('Page Fault Rate (%)')
    ax1.set_title('BZIP - Page Fault Rate vs Frames (Phase 2: Critical Region)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    ax2.set_xlabel('Memory Size (Frames)')
    ax2.set_ylabel('Total Disk Writes')
    ax2.set_title('BZIP - Disk Writes vs Frames (Phase 2: Critical Region)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('bzip_phase2_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_gcc_analysis():
    """Generate gcc trace analysis plots"""
    phase1_frames = [50, 100, 200, 400, 600, 800, 1000]
    data = collect_trace_data('gcc', phase1_frames)
    df = pd.DataFrame(data)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    for algorithm in ['rand', 'lru', 'clock']:
        alg_data = df[df['algorithm'] == algorithm].sort_values('frames')
        ax1.plot(alg_data['frames'], alg_data['fault_rate'], 'o-',
                color=ALGORITHM_COLORS[algorithm], label=algorithm.upper(),
                markersize=6, linewidth=2.5)
        ax2.plot(alg_data['frames'], alg_data['disk_writes'], 'o-',
                color=ALGORITHM_COLORS[algorithm], label=algorithm.upper(),
                markersize=6, linewidth=2.5)
    
    ax1.set_xlabel('Memory Size (Frames)')
    ax1.set_ylabel('Page Fault Rate (%)')
    ax1.set_title('GCC - Page Fault Rate vs Frames (Phase 1)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    ax2.set_xlabel('Memory Size (Frames)')
    ax2.set_ylabel('Total Disk Writes')
    ax2.set_title('GCC - Disk Writes vs Frames (Phase 1)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('gcc_phase1_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Phase 2: Critical transition region
    phase2_frames = list(range(50, 201, 25)) + list(range(200, 401, 50))
    data2 = collect_trace_data('gcc', phase2_frames)
    df2 = pd.DataFrame(data2)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    for algorithm in ['rand', 'lru', 'clock']:
        alg_data = df2[df2['algorithm'] == algorithm].sort_values('frames')
        ax1.plot(alg_data['frames'], alg_data['fault_rate'], 'o-',
                color=ALGORITHM_COLORS[algorithm], label=algorithm.upper(),
                markersize=6, linewidth=2.5)
        ax2.plot(alg_data['frames'], alg_data['disk_writes'], 'o-',
                color=ALGORITHM_COLORS[algorithm], label=algorithm.upper(),
                markersize=6, linewidth=2.5)
    
    ax1.set_xlabel('Memory Size (Frames)')
    ax1.set_ylabel('Page Fault Rate (%)')
    ax1.set_title('GCC - Page Fault Rate vs Frames (Phase 2: Critical Region)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    ax2.set_xlabel('Memory Size (Frames)')
    ax2.set_ylabel('Total Disk Writes')
    ax2.set_title('GCC - Disk Writes vs Frames (Phase 2: Critical Region)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('gcc_phase2_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_sixpack_analysis():
    """Generate sixpack trace analysis plots"""
    phase1_frames = [30, 50, 80, 100, 150, 200, 300, 500]
    data = collect_trace_data('sixpack', phase1_frames)
    df = pd.DataFrame(data)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    for algorithm in ['rand', 'lru', 'clock']:
        alg_data = df[df['algorithm'] == algorithm].sort_values('frames')
        ax1.plot(alg_data['frames'], alg_data['fault_rate'], 'o-',
                color=ALGORITHM_COLORS[algorithm], label=algorithm.upper(),
                markersize=6, linewidth=2.5)
        ax2.plot(alg_data['frames'], alg_data['disk_writes'], 'o-',
                color=ALGORITHM_COLORS[algorithm], label=algorithm.upper(),
                markersize=6, linewidth=2.5)
    
    ax1.set_xlabel('Memory Size (Frames)')
    ax1.set_ylabel('Page Fault Rate (%)')
    ax1.set_title('SIXPACK - Page Fault Rate vs Frames (Phase 1)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    ax2.set_xlabel('Memory Size (Frames)')
    ax2.set_ylabel('Total Disk Writes')
    ax2.set_title('SIXPACK - Disk Writes vs Frames (Phase 1)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('sixpack_phase1_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Phase 2: Critical region
    phase2_frames = list(range(30, 101, 10)) + list(range(100, 151, 15))
    data2 = collect_trace_data('sixpack', phase2_frames)
    df2 = pd.DataFrame(data2)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    for algorithm in ['rand', 'lru', 'clock']:
        alg_data = df2[df2['algorithm'] == algorithm].sort_values('frames')
        ax1.plot(alg_data['frames'], alg_data['fault_rate'], 'o-',
                color=ALGORITHM_COLORS[algorithm], label=algorithm.upper(),
                markersize=6, linewidth=2.5)
        ax2.plot(alg_data['frames'], alg_data['disk_writes'], 'o-',
                color=ALGORITHM_COLORS[algorithm], label=algorithm.upper(),
                markersize=6, linewidth=2.5)
    
    ax1.set_xlabel('Memory Size (Frames)')
    ax1.set_ylabel('Page Fault Rate (%)')
    ax1.set_title('SIXPACK - Page Fault Rate vs Frames (Phase 2: Critical Region)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    ax2.set_xlabel('Memory Size (Frames)')
    ax2.set_ylabel('Total Disk Writes')
    ax2.set_title('SIXPACK - Disk Writes vs Frames (Phase 2: Critical Region)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('sixpack_phase2_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_cross_trace_comparison():
    """Generate comprehensive cross-trace comparison table and summary graphs"""
    # Collect data from all traces at key frame sizes
    test_frames = [16, 32, 64, 128, 256, 512]
    traces = ['bzip', 'sixpack', 'swim', 'gcc']
    
    all_data = []
    for trace in traces:
        trace_data = collect_trace_data(trace, test_frames)
        all_data.extend(trace_data)
    
    df = pd.DataFrame(all_data)
    
    # Create memory requirements comparison
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Plot 1: Memory requirements by trace
    memory_req_1pct = []
    memory_req_5pct = []
    trace_names = []
    
    for trace in traces:
        trace_df = df[df['trace'] == trace]
        lru_data = trace_df[trace_df['algorithm'] == 'lru'].sort_values('frames')
        
        # Find frames needed for <1% and <5% fault rates
        frames_1pct = lru_data[lru_data['fault_rate'] < 1.0]
        frames_5pct = lru_data[lru_data['fault_rate'] < 5.0]
        
        req_1pct = frames_1pct.iloc[0]['frames'] if not frames_1pct.empty else 512
        req_5pct = frames_5pct.iloc[0]['frames'] if not frames_5pct.empty else 512
        
        memory_req_1pct.append(req_1pct)
        memory_req_5pct.append(req_5pct)
        trace_names.append(trace.upper())
    
    x_pos = np.arange(len(traces))
    width = 0.35
    
    ax1.bar(x_pos - width/2, memory_req_1pct, width, label='<1% fault rate', 
            color='#3498db', alpha=0.8)
    ax1.bar(x_pos + width/2, memory_req_5pct, width, label='<5% fault rate',
            color='#e74c3c', alpha=0.8)
    
    ax1.set_xlabel('Application Trace')
    ax1.set_ylabel('Memory Requirements (Frames)')
    ax1.set_title('Memory Requirements by Performance Threshold')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(trace_names)
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Plot 2: Algorithm effectiveness across traces
    for trace in traces:
        trace_df = df[df['trace'] == trace]
        frames_64 = trace_df[trace_df['frames'] == 64]
        
        if len(frames_64) == 3:
            fault_rates = []
            for alg in ['rand', 'lru', 'clock']:
                rate = frames_64[frames_64['algorithm'] == alg]['fault_rate'].iloc[0]
                fault_rates.append(rate)
            
            x_alg = [0, 1, 2]
            ax2.plot(x_alg, fault_rates, 'o-', label=trace.upper(), 
                    markersize=8, linewidth=2.5)
    
    ax2.set_xlabel('Algorithm')
    ax2.set_ylabel('Page Fault Rate (%) at 64 Frames')
    ax2.set_title('Algorithm Performance Comparison')
    ax2.set_xticks([0, 1, 2])
    ax2.set_xticklabels(['RAND', 'LRU', 'CLOCK'])
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: LRU improvement over Random
    improvements = []
    for trace in traces:
        trace_df = df[df['trace'] == trace]
        avg_improvement = 0
        count = 0
        
        for frames in test_frames:
            frame_data = trace_df[trace_df['frames'] == frames]
            if len(frame_data) == 3:
                rand_rate = frame_data[frame_data['algorithm'] == 'rand']['fault_rate'].iloc[0]
                lru_rate = frame_data[frame_data['algorithm'] == 'lru']['fault_rate'].iloc[0]
                if rand_rate > 0:
                    improvement = ((rand_rate - lru_rate) / rand_rate) * 100
                    avg_improvement += improvement
                    count += 1
        
        improvements.append(avg_improvement / count if count > 0 else 0)
    
    colors = ['#3498db', '#e74c3c', '#27ae60', '#f39c12']
    bars = ax3.bar(trace_names, improvements, color=colors, alpha=0.8)
    ax3.set_xlabel('Application Trace')
    ax3.set_ylabel('Average LRU Improvement over Random (%)')
    ax3.set_title('Algorithm Sensitivity Analysis')
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for bar, value in zip(bars, improvements):
        ax3.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.5,
                f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    # Plot 4: Performance efficiency heatmap
    matrix_data = []
    frames_subset = [16, 32, 64, 128, 256]
    
    for trace in traces:
        trace_row = []
        for frames in frames_subset:
            trace_frame_data = df[(df['trace'] == trace) & (df['frames'] == frames) & 
                                 (df['algorithm'] == 'lru')]
            if not trace_frame_data.empty:
                fault_rate = trace_frame_data['fault_rate'].iloc[0]
                trace_row.append(fault_rate)
            else:
                trace_row.append(np.nan)
        matrix_data.append(trace_row)
    
    im = ax4.imshow(matrix_data, cmap='RdYlBu_r', aspect='auto', vmin=0, vmax=30)
    
    ax4.set_xticks(range(len(frames_subset)))
    ax4.set_xticklabels(frames_subset)
    ax4.set_yticks(range(len(traces)))
    ax4.set_yticklabels(trace_names)
    ax4.set_xlabel('Memory Size (Frames)')
    ax4.set_ylabel('Application Trace')
    ax4.set_title('LRU Performance Matrix\n(Fault Rate %)')
    
    # Add text annotations
    for i in range(len(traces)):
        for j in range(len(frames_subset)):
            if not np.isnan(matrix_data[i][j]):
                text_color = "white" if matrix_data[i][j] > 15 else "black"
                ax4.text(j, i, f'{matrix_data[i][j]:.1f}',
                        ha="center", va="center", color=text_color, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('cross_trace_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

def generate_all_report_plots():
    """Main function to generate all plots for the report"""
    plot_swim_analysis()
    plot_bzip_analysis()
    plot_gcc_analysis()  
    plot_sixpack_analysis()
    plot_cross_trace_comparison()

# Main execution
if __name__ == "__main__":
    generate_all_report_plots()