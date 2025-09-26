import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from collections import deque
import random

if 'processes' not in st.session_state:
    st.session_state.processes = []
if 'run_simulation' not in st.session_state:
    st.session_state.run_simulation = False
if 'compare_all' not in st.session_state:
    st.session_state.compare_all = False

st.set_page_config(
    page_title="CPU Scheduling Simulator",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("CPU Scheduling Simulator")
st.markdown("**Operating Systems Project - CPU Scheduling Module**")
st.markdown("---")

st.markdown("""
### Module Overview
This module demonstrates various CPU scheduling algorithms with interactive visualizations.
You can input processes manually, upload CSV files, or generate sample data to compare different scheduling strategies.
""")

st.markdown("---")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Process Input")
    
    input_method = st.radio(
        "Choose input method:",
        ["Manual Entry", "Upload CSV", "Generate Sample"]
    )
    
    if input_method == "Manual Entry":
        st.markdown("#### Add New Process")
        
        with st.form("add_process"):
            process_name = st.text_input("Process Name", value=f"P{len(st.session_state.processes) + 1}")
            arrival_time = st.number_input("Arrival Time", min_value=0, value=0)
            burst_time = st.number_input("Burst Time", min_value=1, value=1)
            priority = st.number_input("Priority (lower = higher priority)", min_value=1, value=1)
            
            submitted = st.form_submit_button("Add Process")
            
            if submitted:
                new_process = {
                    'Process': process_name,
                    'Arrival Time': arrival_time,
                    'Burst Time': burst_time,
                    'Priority': priority
                }
                st.session_state.processes.append(new_process)
                st.success(f"Added {process_name}!")
                st.rerun()
    
    elif input_method == "Upload CSV":
        st.markdown("#### Upload CSV File")
        st.info("CSV should have columns: Process, Arrival Time, Burst Time, Priority")
        
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv", key="csv_uploader")
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                
                required_columns = ['Process', 'Arrival Time', 'Burst Time', 'Priority']
                if all(col in df.columns for col in required_columns):
                    st.write("Preview of uploaded data:")
                    st.dataframe(df)
                    
                    if st.button("Confirm Upload"):
                        st.session_state.processes = df.to_dict('records')
                        st.success(f"Successfully uploaded {len(st.session_state.processes)} processes!")
                        
                else:
                    st.error(f"CSV must contain columns: {', '.join(required_columns)}")
                    st.write("Your CSV columns:", list(df.columns))
                    
            except Exception as e:
                st.error(f"Error reading CSV: {str(e)}")
        
        st.markdown("#### Download Template")
        sample_data = {
            'Process': ['P1', 'P2', 'P3', 'P4'],
            'Arrival Time': [0, 1, 2, 3],
            'Burst Time': [4, 3, 1, 2],
            'Priority': [1, 2, 3, 1]
        }
        sample_df = pd.DataFrame(sample_data)
        csv = sample_df.to_csv(index=False)
        st.download_button(
            label="Download CSV Template",
            data=csv,
            file_name='cpu_processes_template.csv',
            mime='text/csv'
        )
    
    elif input_method == "Generate Sample":
        sample_type = st.selectbox(
            "Sample Data Type:",
            ["Random", "Batch System", "Interactive System", "Real-time System"]
        )
        num_processes = st.slider("Number of processes", 3, 8, 5)
        
        if st.button("Generate Sample Processes"):
            st.session_state.processes = []
            
            if sample_type == "Random":
                for i in range(num_processes):
                    process = {
                        'Process': f"P{i+1}",
                        'Arrival Time': random.randint(0, 5),
                        'Burst Time': random.randint(1, 10),
                        'Priority': random.randint(1, 5)
                    }
                    st.session_state.processes.append(process)
                    
            elif sample_type == "Batch System":
                for i in range(num_processes):
                    process = {
                        'Process': f"P{i+1}",
                        'Arrival Time': 0,
                        'Burst Time': random.randint(5, 15),
                        'Priority': 1
                    }
                    st.session_state.processes.append(process)
                    
            elif sample_type == "Interactive System":
                arrival = 0
                for i in range(num_processes):
                    process = {
                        'Process': f"P{i+1}",
                        'Arrival Time': arrival,
                        'Burst Time': random.randint(1, 5),
                        'Priority': random.randint(1, 3)
                    }
                    st.session_state.processes.append(process)
                    arrival += random.randint(1, 3)
                    
            elif sample_type == "Real-time System":
                arrival = 0
                for i in range(num_processes):
                    process = {
                        'Process': f"P{i+1}",
                        'Arrival Time': arrival,
                        'Burst Time': random.randint(1, 3),
                        'Priority': random.randint(1, 2)
                    }
                    st.session_state.processes.append(process)
                    arrival += random.randint(0, 2)
                    
            st.success(f"Generated {num_processes} {sample_type.lower()} processes!")
            st.rerun()
    
    if st.button("Clear All Processes"):
        st.session_state.processes = []
        st.success("All processes cleared!")
        st.rerun()

with col2:
    st.subheader("Current Processes")
    
    if st.session_state.processes:
        df = pd.DataFrame(st.session_state.processes)
        st.dataframe(df, use_container_width=True)
        
        st.info(f"Total Processes: {len(st.session_state.processes)}")
    else:
        st.info("No processes added yet. Please add some processes to begin simulation.")

def validate_processes(processes):
    for p in processes:
        if p["Arrival Time"] < 0:
            return False, f"Process {p['Process']}: Arrival time cannot be negative"
        if p["Burst Time"] <= 0:
            return False, f"Process {p['Process']}: Burst time must be positive"
        if p["Priority"] <= 0:
            return False, f"Process {p['Process']}: Priority must be positive"
    return True, "Valid"

if st.session_state.processes:
    is_valid, message = validate_processes(st.session_state.processes)
    
    if not is_valid:
        st.error(f"Invalid input: {message}")
    else:
        col_sim1, col_sim2 = st.columns(2)
        
        with col_sim1:
            if st.button("Run Single Algorithm", type="primary"):
                st.session_state.run_simulation = True
                st.rerun()
        
        with col_sim2:
            if st.button("Compare All Algorithms"):
                st.session_state.compare_all = True
                st.rerun()
else:
    st.warning("Please add at least one process to run the simulation.")

st.markdown("---")
st.subheader("Algorithm Configuration")

alg_col1, alg_col2 = st.columns([2, 1])

with alg_col1:
    algorithm = st.selectbox(
        "Select CPU Scheduling Algorithm:",
        [
            "First Come First Serve (FCFS)",
            "Shortest Job First - Non-preemptive (SJF)",
            "Shortest Job First - Preemptive (SRTF)",
            "Priority - Non-preemptive",
            "Priority - Preemptive",
            "Round Robin (RR)"
        ]
    )

with alg_col2:
    if "Round Robin" in algorithm:
        time_quantum = st.number_input(
            "Time Quantum", 
            min_value=1, 
            value=2,
            help="Time slice for each process in Round Robin scheduling"
        )
    else:
        time_quantum = None

algorithm_descriptions = {
    "First Come First Serve (FCFS)": "Processes are executed in the order they arrive. Simple but can cause convoy effect.",
    "Shortest Job First - Non-preemptive (SJF)": "Process with shortest burst time is selected next. Optimal for average waiting time.",
    "Shortest Job First - Preemptive (SRTF)": "Currently running process can be preempted by a shorter job. Also called Shortest Remaining Time First.",
    "Priority - Non-preemptive": "Process with highest priority (lowest number) is selected. No preemption once started.",
    "Priority - Preemptive": "Currently running process can be preempted by higher priority process.",
    "Round Robin (RR)": "Each process gets equal time quantum in circular order. Good for interactive systems."
}

algorithm_complexities = {
    "First Come First Serve (FCFS)": "O(n)",
    "Shortest Job First - Non-preemptive (SJF)": "O(n²)",
    "Shortest Job First - Preemptive (SRTF)": "O(n²)",
    "Priority - Non-preemptive": "O(n²)",
    "Priority - Preemptive": "O(n²)",
    "Round Robin (RR)": "O(n)"
}

st.info(f"**Algorithm Info:** {algorithm_descriptions[algorithm]}")
st.success(f"**Time Complexity:** {algorithm_complexities[algorithm]}")

def fcfs_scheduling(processes):
    processes_copy = processes.copy()
    processes_copy.sort(key=lambda x: x['Arrival Time'])
    
    current_time = 0
    gantt_chart = []
    results = []
    
    for process in processes_copy:
        if current_time < process['Arrival Time']:
            if current_time < process['Arrival Time']:
                gantt_chart.append({
                    'Process': 'Idle',
                    'Start': current_time,
                    'End': process['Arrival Time'],
                    'Duration': process['Arrival Time'] - current_time
                })
            current_time = process['Arrival Time']
        
        start_time = current_time
        end_time = start_time + process['Burst Time']
        waiting_time = start_time - process['Arrival Time']
        turnaround_time = end_time - process['Arrival Time']
        response_time = waiting_time  
        
        gantt_chart.append({
            'Process': process['Process'],
            'Start': start_time,
            'End': end_time,
            'Duration': process['Burst Time']
        })
        
        results.append({
            'Process': process['Process'],
            'Arrival Time': process['Arrival Time'],
            'Burst Time': process['Burst Time'],
            'Start Time': start_time,
            'End Time': end_time,
            'Waiting Time': waiting_time,
            'Turnaround Time': turnaround_time,
            'Response Time': response_time
        })
        
        current_time = end_time
    
    return gantt_chart, results

def sjf_non_preemptive(processes):
    processes_copy = processes.copy()
    current_time = 0
    gantt_chart = []
    results = []
    completed = []
    
    while len(completed) < len(processes):
        available = [p for p in processes_copy if p['Arrival Time'] <= current_time and p not in completed]
        
        if not available:
            next_arrival = min([p['Arrival Time'] for p in processes_copy if p not in completed])
            gantt_chart.append({
                'Process': 'Idle',
                'Start': current_time,
                'End': next_arrival,
                'Duration': next_arrival - current_time
            })
            current_time = next_arrival
            continue
        
        selected = min(available, key=lambda x: x['Burst Time'])
        
        start_time = current_time
        end_time = start_time + selected['Burst Time']
        waiting_time = start_time - selected['Arrival Time']
        turnaround_time = end_time - selected['Arrival Time']
        response_time = waiting_time
        
        gantt_chart.append({
            'Process': selected['Process'],
            'Start': start_time,
            'End': end_time,
            'Duration': selected['Burst Time']
        })
        
        results.append({
            'Process': selected['Process'],
            'Arrival Time': selected['Arrival Time'],
            'Burst Time': selected['Burst Time'],
            'Start Time': start_time,
            'End Time': end_time,
            'Waiting Time': waiting_time,
            'Turnaround Time': turnaround_time,
            'Response Time': response_time
        })
        
        completed.append(selected)
        current_time = end_time
    
    return gantt_chart, results

def round_robin(processes, time_quantum):
    processes_copy = [{**p, 'Remaining Time': p['Burst Time'], 'First Response': None} for p in processes]
    current_time = 0
    gantt_chart = []
    results = []
    ready_queue = deque()
    completed = []
    
    while len(completed) < len(processes) or ready_queue:
        for process in processes_copy:
            if (process['Arrival Time'] <= current_time and 
                process not in ready_queue and 
                process not in completed and
                process['Remaining Time'] > 0):
                ready_queue.append(process)
        
        if not ready_queue:
            next_arrivals = [p for p in processes_copy if p['Arrival Time'] > current_time and p not in completed]
            if next_arrivals:
                next_time = min(p['Arrival Time'] for p in next_arrivals)
                gantt_chart.append({
                    'Process': 'Idle',
                    'Start': current_time,
                    'End': next_time,
                    'Duration': next_time - current_time
                })
                current_time = next_time
            continue
        
        current_process = ready_queue.popleft()
        
        if current_process['First Response'] is None:
            current_process['First Response'] = current_time
        
        execution_time = min(time_quantum, current_process['Remaining Time'])
        
        gantt_chart.append({
            'Process': current_process['Process'],
            'Start': current_time,
            'End': current_time + execution_time,
            'Duration': execution_time
        })
        
        current_time += execution_time
        current_process['Remaining Time'] -= execution_time
        
        for process in processes_copy:
            if (process['Arrival Time'] <= current_time and 
                process not in ready_queue and 
                process not in completed and
                process['Remaining Time'] > 0 and
                process != current_process):
                ready_queue.append(process)
        
        if current_process['Remaining Time'] == 0:
            end_time = current_time
            turnaround_time = end_time - current_process['Arrival Time']
            waiting_time = turnaround_time - current_process['Burst Time']
            response_time = current_process['First Response'] - current_process['Arrival Time']
            
            results.append({
                'Process': current_process['Process'],
                'Arrival Time': current_process['Arrival Time'],
                'Burst Time': current_process['Burst Time'],
                'End Time': end_time,
                'Waiting Time': waiting_time,
                'Turnaround Time': turnaround_time,
                'Response Time': response_time
            })
            completed.append(current_process)
        else:
            ready_queue.append(current_process)
    
    return gantt_chart, results

def srtf_scheduling(processes):
    processes_copy = [{**p, 'Remaining Time': p['Burst Time'], 'First Response': None} for p in processes]
    current_time = 0
    gantt_chart = []
    results = []
    completed = []
    
    while len(completed) < len(processes):
        available = [p for p in processes_copy 
                    if p['Arrival Time'] <= current_time 
                    and p['Remaining Time'] > 0 
                    and p not in completed]
        
        if not available:
            next_arrival = min([p['Arrival Time'] for p in processes_copy if p not in completed])
            gantt_chart.append({
                'Process': 'Idle',
                'Start': current_time,
                'End': next_arrival,
                'Duration': next_arrival - current_time
            })
            current_time = next_arrival
            continue
        
        current_process = min(available, key=lambda x: x['Remaining Time'])
        
        if current_process['First Response'] is None:
            current_process['First Response'] = current_time
        
        next_events = []
        
        completion_time = current_time + current_process['Remaining Time']
        next_events.append(completion_time)
        
        for p in processes_copy:
            if p['Arrival Time'] > current_time and p not in completed:
                next_events.append(p['Arrival Time'])
        
        next_event_time = min(next_events)
        execution_time = min(next_event_time - current_time, current_process['Remaining Time'])
        
        gantt_chart.append({
            'Process': current_process['Process'],
            'Start': current_time,
            'End': current_time + execution_time,
            'Duration': execution_time
        })
        
        current_time += execution_time
        current_process['Remaining Time'] -= execution_time
        
        if current_process['Remaining Time'] == 0:
            end_time = current_time
            turnaround_time = end_time - current_process['Arrival Time']
            waiting_time = turnaround_time - current_process['Burst Time']
            response_time = current_process['First Response'] - current_process['Arrival Time']
            
            results.append({
                'Process': current_process['Process'],
                'Arrival Time': current_process['Arrival Time'],
                'Burst Time': current_process['Burst Time'],
                'End Time': end_time,
                'Waiting Time': waiting_time,
                'Turnaround Time': turnaround_time,
                'Response Time': response_time
            })
            completed.append(current_process)
    
    return gantt_chart, results

def priority_non_preemptive(processes):
    processes_copy = processes.copy()
    current_time = 0
    gantt_chart = []
    results = []
    completed = []
    
    while len(completed) < len(processes):
        available = [p for p in processes_copy if p['Arrival Time'] <= current_time and p not in completed]
        
        if not available:
            next_arrival = min([p['Arrival Time'] for p in processes_copy if p not in completed])
            gantt_chart.append({
                'Process': 'Idle',
                'Start': current_time,
                'End': next_arrival,
                'Duration': next_arrival - current_time
            })
            current_time = next_arrival
            continue
        
        selected = min(available, key=lambda x: (x['Priority'], x['Arrival Time']))
        
        start_time = current_time
        end_time = start_time + selected['Burst Time']
        waiting_time = start_time - selected['Arrival Time']
        turnaround_time = end_time - selected['Arrival Time']
        response_time = waiting_time
        
        gantt_chart.append({
            'Process': selected['Process'],
            'Start': start_time,
            'End': end_time,
            'Duration': selected['Burst Time']
        })
        
        results.append({
            'Process': selected['Process'],
            'Arrival Time': selected['Arrival Time'],
            'Burst Time': selected['Burst Time'],
            'Priority': selected['Priority'],
            'Start Time': start_time,
            'End Time': end_time,
            'Waiting Time': waiting_time,
            'Turnaround Time': turnaround_time,
            'Response Time': response_time
        })
        
        completed.append(selected)
        current_time = end_time
    
    return gantt_chart, results

def priority_preemptive(processes):
    processes_copy = [{**p, 'Remaining Time': p['Burst Time'], 'First Response': None} for p in processes]
    current_time = 0
    gantt_chart = []
    results = []
    completed = []
    
    while len(completed) < len(processes):
        available = [p for p in processes_copy 
                    if p['Arrival Time'] <= current_time 
                    and p['Remaining Time'] > 0 
                    and p not in completed]
        
        if not available:
            next_arrival = min([p['Arrival Time'] for p in processes_copy if p not in completed])
            gantt_chart.append({
                'Process': 'Idle',
                'Start': current_time,
                'End': next_arrival,
                'Duration': next_arrival - current_time
            })
            current_time = next_arrival
            continue
        
        current_process = min(available, key=lambda x: (x['Priority'], x['Arrival Time']))
        
        if current_process['First Response'] is None:
            current_process['First Response'] = current_time
        
        next_events = []
        
        completion_time = current_time + current_process['Remaining Time']
        next_events.append(completion_time)
        
        for p in processes_copy:
            if (p['Arrival Time'] > current_time and 
                p not in completed and 
                p['Priority'] < current_process['Priority']):
                next_events.append(p['Arrival Time'])
        
        next_event_time = min(next_events)
        execution_time = min(next_event_time - current_time, current_process['Remaining Time'])
        
        gantt_chart.append({
            'Process': current_process['Process'],
            'Start': current_time,
            'End': current_time + execution_time,
            'Duration': execution_time
        })
        
        current_time += execution_time
        current_process['Remaining Time'] -= execution_time
        
        if current_process['Remaining Time'] == 0:
            end_time = current_time
            turnaround_time = end_time - current_process['Arrival Time']
            waiting_time = turnaround_time - current_process['Burst Time']
            response_time = current_process['First Response'] - current_process['Arrival Time']
            
            results.append({
                'Process': current_process['Process'],
                'Arrival Time': current_process['Arrival Time'],
                'Burst Time': current_process['Burst Time'],
                'Priority': current_process['Priority'],
                'End Time': end_time,
                'Waiting Time': waiting_time,
                'Turnaround Time': turnaround_time,
                'Response Time': response_time
            })
            completed.append(current_process)
    
    return gantt_chart, results

def compare_all_algorithms(processes):
    algorithms_to_compare = [
        ("FCFS", fcfs_scheduling),
        ("SJF", sjf_non_preemptive),
        ("SRTF", srtf_scheduling),
        ("Priority NP", priority_non_preemptive),
        ("Priority P", priority_preemptive),
        ("Round Robin", lambda p: round_robin(p, 2))
    ]
    
    comparison_results = []
    
    for name, func in algorithms_to_compare:
        try:
            gantt_data, results = func(processes)
            metrics = calculate_average_metrics(results)
            
            comparison_results.append({
                'Algorithm': name,
                'Avg Waiting Time': metrics['Average Waiting Time'],
                'Avg Turnaround Time': metrics['Average Turnaround Time'],
                'Avg Response Time': metrics['Average Response Time']
            })
        except:
            comparison_results.append({
                'Algorithm': name,
                'Avg Waiting Time': 'Error',
                'Avg Turnaround Time': 'Error',
                'Avg Response Time': 'Error'
            })
    
    return comparison_results

def create_gantt_chart(gantt_data, algorithm_name):
    if not gantt_data:
        return None
    
    processes = list(set([item['Process'] for item in gantt_data if item['Process'] != 'Idle']))
    colors = px.colors.qualitative.Set3[:len(processes)]
    color_map = dict(zip(processes, colors))
    color_map['Idle'] = '#E5E5E5'
    
    fig = go.Figure()
    
    for i, item in enumerate(gantt_data):
        fig.add_trace(go.Scatter(
            x=[item['Start'], item['End'], item['End'], item['Start'], item['Start']],
            y=[i, i, i+0.8, i+0.8, i],
            fill="toself",
            fillcolor=color_map.get(item['Process'], '#1f77b4'),
            line=dict(color="black", width=1),
            name=item['Process'],
            text=f"{item['Process']}<br>Time: {item['Start']}-{item['End']}<br>Duration: {item['Duration']}",
            hovertemplate="<b>%{text}</b><extra></extra>",
            showlegend=True if i == 0 or item['Process'] not in [gantt_data[j]['Process'] for j in range(i)] else False
        ))
    
    fig.update_layout(
        title=f"Gantt Chart - {algorithm_name}",
        xaxis_title="Time",
        yaxis_title="Execution Sequence",
        height=max(400, len(gantt_data) * 40),
        showlegend=True,
        yaxis=dict(showticklabels=False),
        hovermode='closest'
    )
    
    return fig

def calculate_average_metrics(results):
    if not results:
        return {}
    
    total_waiting = sum(r['Waiting Time'] for r in results)
    total_turnaround = sum(r['Turnaround Time'] for r in results)
    total_response = sum(r['Response Time'] for r in results)
    num_processes = len(results)
    
    return {
        'Average Waiting Time': round(total_waiting / num_processes, 2),
        'Average Turnaround Time': round(total_turnaround / num_processes, 2),
        'Average Response Time': round(total_response / num_processes, 2),
        'Total Processes': num_processes
    }

if st.session_state.get('run_simulation', False):
    st.markdown("---")
    st.subheader("Simulation Results")
    
    gantt_data = None
    results = None
    
    try:
        if algorithm == "First Come First Serve (FCFS)":
            gantt_data, results = fcfs_scheduling(st.session_state.processes)
        
        elif algorithm == "Shortest Job First - Non-preemptive (SJF)":
            gantt_data, results = sjf_non_preemptive(st.session_state.processes)
        
        elif algorithm == "Shortest Job First - Preemptive (SRTF)":
            gantt_data, results = srtf_scheduling(st.session_state.processes)
        
        elif algorithm == "Priority - Non-preemptive":
            gantt_data, results = priority_non_preemptive(st.session_state.processes)
        
        elif algorithm == "Priority - Preemptive":
            gantt_data, results = priority_preemptive(st.session_state.processes)
        
        elif algorithm == "Round Robin (RR)":
            if time_quantum:
                gantt_data, results = round_robin(st.session_state.processes, time_quantum)
            else:
                st.error("Please specify time quantum for Round Robin scheduling.")
        
        if gantt_data and results:
            fig = create_gantt_chart(gantt_data, algorithm)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("Detailed Results")
            results_df = pd.DataFrame(results)
            st.dataframe(results_df, use_container_width=True)
            
            csv = results_df.to_csv(index=False)
            st.download_button(
                label="Download Results as CSV",
                data=csv,
                file_name=f'{algorithm}_results.csv',
                mime='text/csv'
            )
            
            metrics = calculate_average_metrics(results)
            if metrics:
                st.subheader("Performance Metrics")
                
                metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
                
                with metric_col1:
                    st.metric("Avg Waiting Time", f"{metrics['Average Waiting Time']} ms")
                
                with metric_col2:
                    st.metric("Avg Turnaround Time", f"{metrics['Average Turnaround Time']} ms")
                
                with metric_col3:
                    st.metric("Avg Response Time", f"{metrics['Average Response Time']} ms")
                
                with metric_col4:
                    st.metric("Total Processes", metrics['Total Processes'])
                
                st.subheader("Performance Comparison")
                metrics_chart_data = {
                    'Metric': ['Waiting Time', 'Turnaround Time', 'Response Time'],
                    'Average Time': [
                        metrics['Average Waiting Time'],
                        metrics['Average Turnaround Time'], 
                        metrics['Average Response Time']
                    ]
                }
                
                fig_metrics = px.bar(
                    metrics_chart_data, 
                    x='Metric', 
                    y='Average Time',
                    title=f"Average Performance Metrics - {algorithm}",
                    color='Metric'
                )
                st.plotly_chart(fig_metrics, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error in simulation: {str(e)}")
    
    st.session_state.run_simulation = False

if st.session_state.get('compare_all', False):
    st.markdown("---")
    st.subheader("Algorithm Comparison Results")
    
    comparison_results = compare_all_algorithms(st.session_state.processes)
    comparison_df = pd.DataFrame(comparison_results)
    
    st.dataframe(comparison_df, use_container_width=True)
    
    csv_comparison = comparison_df.to_csv(index=False)
    st.download_button(
        label="Download Comparison as CSV",
        data=csv_comparison,
        file_name='algorithm_comparison.csv',
        mime='text/csv'
    )
    
    fig_comparison = px.bar(
        comparison_df, 
        x='Algorithm', 
        y=['Avg Waiting Time', 'Avg Turnaround Time', 'Avg Response Time'],
        title="Algorithm Performance Comparison",
        barmode='group'
    )
    st.plotly_chart(fig_comparison, use_container_width=True)
    
    st.session_state.compare_all = False
