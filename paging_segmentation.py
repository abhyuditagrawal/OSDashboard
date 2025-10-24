import streamlit as st
import pandas as pd
from collections import deque

# =========== Paging Simulator ===========
class PagingSimulator:
    def __init__(self, logical_memory_size, physical_memory_size, page_size):
        self.logical_memory_size = logical_memory_size
        self.physical_memory_size = physical_memory_size
        self.page_size = page_size
        self.num_pages = logical_memory_size // page_size
        self.num_frames = physical_memory_size // page_size
        self.page_table = {}
        
    def create_page_table(self, mappings):
        self.page_table = mappings
        
    def translate_address(self, logical_address):
        page_number = logical_address // self.page_size
        offset = logical_address % self.page_size
        if page_number >= self.num_pages:
            return {'valid': False, 'error': 'Invalid page number', 'page_number': page_number, 'offset': offset}
        if page_number not in self.page_table:
            return {'valid': False, 'error': 'Page fault - Page not in memory', 'page_number': page_number, 'offset': offset}
        frame_number = self.page_table[page_number]
        physical_address = (frame_number * self.page_size) + offset
        return {'valid': True, 'logical_address': logical_address, 'page_number': page_number, 
                'offset': offset, 'frame_number': frame_number, 'physical_address': physical_address}
    
    def calculate_internal_fragmentation(self):
        if self.logical_memory_size % self.page_size == 0:
            return 0
        return self.page_size - (self.logical_memory_size % self.page_size)

# =========== Segmentation Simulator ===========
class SegmentationSimulator:
    def __init__(self):
        self.segment_table = {}
        
    def add_segment(self, segment_number, base, limit, name="Segment"):
        self.segment_table[segment_number] = {'base': base, 'limit': limit, 'name': name}
    
    def translate_address(self, segment_number, offset):
        if segment_number not in self.segment_table:
            return {'valid': False, 'error': 'Invalid segment number'}
        segment = self.segment_table[segment_number]
        if offset >= segment['limit']:
            return {'valid': False, 'error': f'Segmentation fault - Offset {offset} exceeds limit {segment["limit"]}'}
        physical_address = segment['base'] + offset
        return {'valid': True, 'segment_number': segment_number, 'segment_name': segment['name'],
                'offset': offset, 'base': segment['base'], 'limit': segment['limit'], 
                'physical_address': physical_address}

# =========== Page Replacement Algorithms ===========
class PageReplacementSimulator:
    def __init__(self, num_frames):
        self.num_frames = num_frames
        
    def fifo(self, reference_string):
        frames, queue = [], []
        page_faults, page_hits = 0, 0
        steps = []
        for page in reference_string:
            if page in frames:
                page_hits += 1
                status = "Hit"
            else:
                page_faults += 1
                status = "Fault"
                if len(frames) < self.num_frames:
                    frames.append(page)
                    queue.append(page)
                else:
                    removed = queue.pop(0)
                    frames[frames.index(removed)] = page
                    queue.append(page)
            steps.append({'Page': page, 'Frames': str(frames.copy()), 'Status': status})
        return {'page_faults': page_faults, 'page_hits': page_hits, 'steps': steps}
    
    def lru(self, reference_string):
        frames, recent = [], []
        page_faults, page_hits = 0, 0
        steps = []
        for page in reference_string:
            if page in frames:
                page_hits += 1
                status = "Hit"
                recent.remove(page)
                recent.append(page)
            else:
                page_faults += 1
                status = "Fault"
                if len(frames) < self.num_frames:
                    frames.append(page)
                    recent.append(page)
                else:
                    lru_page = recent.pop(0)
                    frames[frames.index(lru_page)] = page
                    recent.append(page)
            steps.append({'Page': page, 'Frames': str(frames.copy()), 'Status': status})
        return {'page_faults': page_faults, 'page_hits': page_hits, 'steps': steps}
    
    def optimal(self, reference_string):
        frames = []
        page_faults, page_hits, steps = 0, 0, []
        for i, page in enumerate(reference_string):
            if page in frames:
                page_hits += 1
                status = "Hit"
            else:
                page_faults += 1
                status = "Fault"
                if len(frames) < self.num_frames:
                    frames.append(page)
                else:
                    future_use = {}
                    for frame in frames:
                        try:
                            future_use[frame] = reference_string[i+1:].index(frame)
                        except ValueError:
                            future_use[frame] = float('inf')
                    replace = max(future_use, key=future_use.get)
                    frames[frames.index(replace)] = page
            steps.append({'Page': page, 'Frames': str(frames.copy()), 'Status': status})
        return {'page_faults': page_faults, 'page_hits': page_hits, 'steps': steps}

# =========== Memory Allocation Algorithms ===========
class MemoryAllocation:
    def __init__(self, memory_blocks):
        self.memory_blocks = memory_blocks.copy()
        
    def first_fit(self, process_sizes):
        allocation = [-1] * len(process_sizes)
        blocks = self.memory_blocks.copy()
        
        for i, process_size in enumerate(process_sizes):
            for j, block_size in enumerate(blocks):
                if block_size >= process_size:
                    allocation[i] = j
                    blocks[j] -= process_size
                    break
        return allocation, blocks
    
    def best_fit(self, process_sizes):
        allocation = [-1] * len(process_sizes)
        blocks = self.memory_blocks.copy()
        
        for i, process_size in enumerate(process_sizes):
            best_idx = -1
            for j, block_size in enumerate(blocks):
                if block_size >= process_size:
                    if best_idx == -1 or blocks[best_idx] > block_size:
                        best_idx = j
            
            if best_idx != -1:
                allocation[i] = best_idx
                blocks[best_idx] -= process_size
        
        return allocation, blocks
    
    def worst_fit(self, process_sizes):
        allocation = [-1] * len(process_sizes)
        blocks = self.memory_blocks.copy()
        
        for i, process_size in enumerate(process_sizes):
            worst_idx = -1
            for j, block_size in enumerate(blocks):
                if block_size >= process_size:
                    if worst_idx == -1 or blocks[worst_idx] < block_size:
                        worst_idx = j
            
            if worst_idx != -1:
                allocation[i] = worst_idx
                blocks[worst_idx] -= process_size
        
        return allocation, blocks

# =========== Streamlit App ===========
st.set_page_config(page_title="Memory Management Simulator", page_icon="🧠", layout="wide")

st.title("🧠 Operating Systems - Memory Management Simulator")
st.markdown("**SVKM's NMIMS | Unit 5: Memory Management**")

st.sidebar.title("🎯 Select Module")
module = st.sidebar.radio("Choose Simulator", 
    ["Paging", "Segmentation", "Page Replacement", "Memory Allocation"])

# ========== Paging ==========#
if module == "Paging":
    st.header("🔢 Paging Simulator")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        logical_memory = st.selectbox("Logical Memory (bytes)", [256, 512, 1024, 2048, 4096], index=2)
    with col2:
        physical_memory = st.selectbox("Physical Memory (bytes)", [256, 512, 1024, 2048, 4096], index=2)
    with col3:
        page_size = st.selectbox("Page Size (bytes)", [16, 32, 64, 128, 256], index=2)

    simulator = PagingSimulator(logical_memory, physical_memory, page_size)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Number of Pages", simulator.num_pages)
    col2.metric("Number of Frames", simulator.num_frames)
    col3.metric("Internal Fragmentation", f"{simulator.calculate_internal_fragmentation()} bytes")
    col4.metric("Memory Utilization", f"{((logical_memory - simulator.calculate_internal_fragmentation()) / logical_memory * 100):.1f}%")
    
    st.markdown("### Page Table Configuration")
    num_mappings = st.number_input("Number of page mappings", 1, simulator.num_pages, min(5, simulator.num_pages))
    page_table = {}
    cols = st.columns(min(3, int(num_mappings)))
    for i in range(int(num_mappings)):
        with cols[i % len(cols)]:
            page = st.number_input(f"Page {i}", 0, simulator.num_pages-1, i, key=f"page_{i}")
            frame = st.number_input(f"→ Frame", 0, simulator.num_frames-1, i, key=f"frame_{i}")
            page_table[page] = frame
    
    simulator.create_page_table(page_table)
    if page_table:
        st.dataframe(pd.DataFrame(list(page_table.items()), columns=['Page', 'Frame']), use_container_width=True)
    
    st.markdown("### Address Translation")
    logical_address = st.number_input("Logical Address", 0, logical_memory-1, 0)
    if st.button("🔄 Translate", type="primary"):
        result = simulator.translate_address(logical_address)
        if result['valid']:
            st.success(f"✅ Physical Address: **{result['physical_address']}** | Page: {result['page_number']} | Frame: {result['frame_number']} | Offset: {result['offset']}")
        else:
            st.error(f"❌ {result['error']}")

# ========== Segmentation ==========#
elif module == "Segmentation":
    st.header("📊 Segmentation Simulator")
    
    num_segments = st.slider("Number of Segments", 2, 8, 4)
    simulator = SegmentationSimulator()
    segments = []
    
    for i in range(num_segments):
        with st.expander(f"Segment {i}", expanded=(i<3)):
            cols = st.columns(3)
            name = cols[0].text_input("Name", f"Segment_{i}", key=f"seg_name_{i}")
            base = cols[1].number_input("Base Address", 0, 10000, i*1000, 100, key=f"seg_base_{i}")
            limit = cols[2].number_input("Limit (Size)", 1, 2000, 500, 50, key=f"seg_limit_{i}")
            segments.append({'name': name, 'base': base, 'limit': limit})
            simulator.add_segment(i, base, limit, name)
    
    st.dataframe(pd.DataFrame([
        {'Segment': i, 'Name': s['name'], 'Base': s['base'], 'Limit': s['limit'], 'End': s['base']+s['limit']}
        for i, s in enumerate(segments)
    ]), use_container_width=True)
    
    st.markdown("### Address Translation")
    col1, col2 = st.columns(2)
    segment_num = col1.number_input("Segment Number", 0, num_segments-1, 0)
    offset = col2.number_input("Offset", 0, 5000, 100)
    
    if st.button("🔄 Translate", type="primary", key="seg_translate"):
        result = simulator.translate_address(segment_num, offset)
        if result['valid']:
            st.success(f"✅ Physical Address: **{result['physical_address']}** | Base: {result['base']} + Offset: {result['offset']}")
        else:
            st.error(f"❌ {result['error']}")

# ========== Page Replacement ==========#
elif module == "Page Replacement":
    st.header("🔄 Page Replacement Algorithms")
    
    col1, col2 = st.columns([1, 2])
    num_frames = col1.slider("Number of Frames", 2, 7, 3)
    reference_input = col2.text_input("Page Reference String (comma-separated)", "7,0,1,2,0,3,0,4,2,3,0,3,2")
    
    try:
        reference_string = [int(x.strip()) for x in reference_input.split(',')]
        st.info(f"✅ Valid reference string with {len(reference_string)} page requests")
    except:
        st.error("❌ Invalid input")
        st.stop()
    
    algorithms = st.multiselect("Select Algorithms", ["FIFO", "LRU", "Optimal"], default=["FIFO", "LRU", "Optimal"])
    
    if st.button("▶️ Run Simulation", type="primary"):
        results = {}
        for algo in algorithms:
            sim = PageReplacementSimulator(num_frames)
            if algo == "FIFO":
                results[algo] = sim.fifo(reference_string)
            elif algo == "LRU":
                results[algo] = sim.lru(reference_string)
            elif algo == "Optimal":
                results[algo] = sim.optimal(reference_string)
        
        tabs = st.tabs(algorithms + ["Comparison"])
        
        for idx, algo in enumerate(algorithms):
            with tabs[idx]:
                result = results[algo]
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Page Faults", result['page_faults'])
                col2.metric("Page Hits", result['page_hits'])
                col3.metric("Hit Ratio", f"{(result['page_hits']/len(reference_string)*100):.1f}%")
                col4.metric("Fault Ratio", f"{(result['page_faults']/len(reference_string)*100):.1f}%")
                st.dataframe(pd.DataFrame(result['steps']), use_container_width=True)
        
        if len(results) > 1:
            with tabs[-1]:
                comparison_df = pd.DataFrame([
                    {'Algorithm': algo, 'Faults': r['page_faults'], 'Hits': r['page_hits'], 
                     'Hit Ratio %': round(r['page_hits']/len(reference_string)*100, 2)}
                    for algo, r in results.items()
                ])
                st.dataframe(comparison_df, use_container_width=True)
                st.bar_chart(comparison_df.set_index('Algorithm')[['Faults', 'Hits']])
                best = min(results.items(), key=lambda x: x[1]['page_faults'])
                st.success(f"🏆 **Best Algorithm:** {best[0]} with {best[1]['page_faults']} page faults")

# ========== Memory Allocation ==========#
elif module == "Memory Allocation":
    st.header("💾 Memory Allocation Algorithms")
    st.markdown("**First Fit, Best Fit, Worst Fit**")
    
    st.markdown("### Configuration")
    col1, col2 = st.columns(2)
    
    with col1:
        memory_input = st.text_input("Memory Block Sizes (comma-separated)", "100,500,200,300,600")
        try:
            memory_blocks = [int(x.strip()) for x in memory_input.split(',')]
        except:
            st.error("Invalid memory blocks")
            st.stop()
    
    with col2:
        process_input = st.text_input("Process Sizes (comma-separated)", "212,417,112,426")
        try:
            process_sizes = [int(x.strip()) for x in process_input.split(',')]
        except:
            st.error("Invalid process sizes")
            st.stop()
    
    if st.button("🚀 Run All Algorithms", type="primary"):
        allocator = MemoryAllocation(memory_blocks)
        
        results = {
            'First Fit': allocator.first_fit(process_sizes),
            'Best Fit': allocator.best_fit(process_sizes),
            'Worst Fit': allocator.worst_fit(process_sizes)
        }
        
        for algo_name, (allocation, remaining_blocks) in results.items():
            st.markdown(f"### {algo_name}")
            
            data = []
            for i, process_size in enumerate(process_sizes):
                block_num = allocation[i]
                if block_num != -1:
                    data.append({
                        'Process': f"P{i}",
                        'Size': process_size,
                        'Allocated Block': f"Block {block_num}",
                        'Block Size': memory_blocks[block_num],
                        'Status': '✅ Allocated'
                    })
                else:
                    data.append({
                        'Process': f"P{i}",
                        'Size': process_size,
                        'Allocated Block': 'None',
                        'Block Size': '-',
                        'Status': '❌ Not Allocated'
                    })
            
            st.dataframe(pd.DataFrame(data), use_container_width=True)
            
            col1, col2 = st.columns(2)
            col1.metric("Allocated Processes", sum(1 for x in allocation if x != -1))
            col2.metric("Unallocated Processes", sum(1 for x in allocation if x == -1))
            
            st.markdown("---")

st.sidebar.markdown("---")