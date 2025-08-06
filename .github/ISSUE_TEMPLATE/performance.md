---
name: Performance Issue
about: Report performance problems or suggest optimizations
title: '[PERFORMANCE] '
labels: performance, needs-investigation
assignees: ''

---

## ⚡ Performance Issue

**Type of performance issue:**

- [ ] Slow processing speed
- [ ] High memory usage
- [ ] Long startup time
- [ ] Inefficient file scanning
- [ ] Pattern matching bottleneck
- [ ] Large file handling issues
- [ ] Resource usage concerns
- [ ] Scalability limitations

## 🔍 Problem Description

**Brief summary:**
<!-- Describe the performance issue you're experiencing -->

**Performance impact:**

- [ ] Minor delay (< 5 seconds)
- [ ] Noticeable delay (5-30 seconds)
- [ ] Significant delay (30+ seconds)
- [ ] Unusable (> 2 minutes)
- [ ] Out of memory errors
- [ ] System becomes unresponsive

## 📊 Performance Metrics

**Current performance:**

- **Processing time**: <!-- e.g., 45 seconds for 100 files -->
- **Memory usage**: <!-- e.g., 2GB RAM peak usage -->
- **CPU usage**: <!-- e.g., 100% for 30 seconds -->
- **Files processed**: <!-- e.g., 500 .py files, 50 .ipynb files -->

**Expected performance:**

- **Target processing time**: <!-- What would be acceptable? -->
- **Target memory usage**: <!-- What should it use? -->

## 🔄 Reproduction Steps

**Command used:**

```bash
sparkgrep [your command with all options]
```

**File details:**

- **Number of files**: <!-- e.g., 500 files -->
- **File types**: <!-- .py, .ipynb, etc. -->
- **Average file size**: <!-- e.g., 200 lines, 5KB each -->
- **Largest file size**: <!-- e.g., 5000 lines, 200KB -->
- **Total directory size**: <!-- e.g., 50MB -->

**Patterns used:**

- [ ] Default patterns only
- [ ] Custom patterns added
- [ ] Complex regex patterns
- [ ] Many patterns (>10)
- **Pattern count**: <!-- e.g., 15 patterns -->

## 🖥️ Environment Details

**System specifications:**

- **CPU**: <!-- e.g., Intel i7-9750H, 6 cores -->
- **RAM**: <!-- e.g., 16GB -->
- **Storage**: <!-- e.g., SSD, HDD -->
- **OS**: <!-- e.g., Ubuntu 20.04, macOS 13.1 -->

**Python environment:**

- **Python version**: <!-- python --version -->
- **SparkGrep version**: <!-- sparkgrep --version -->
- **Installation type**: <!-- pip, development install -->

## 📈 Profiling Data

**Time measurement:**

```bash
# Use time command to measure
time sparkgrep [your command]

# Results:
# real: [time]
# user: [time]
# sys:  [time]
```

**Memory profiling** (if available):
<!-- Use tools like memory_profiler, psutil, or system monitor -->

**CPU profiling** (if available):
<!-- Use tools like py-spy, cProfile, or system monitor -->

## 🔧 Analysis and Investigation

**Suspected bottleneck:**

- [ ] File I/O operations
- [ ] Regular expression matching
- [ ] JSON parsing (notebooks)
- [ ] Memory allocation
- [ ] String processing
- [ ] Pattern compilation
- [ ] Directory traversal
- [ ] Output formatting

**Performance comparison:**
<!-- Compare with similar tools or previous versions -->

**File type impact:**

- **Python files (.py)**: <!-- performance notes -->
- **Jupyter notebooks (.ipynb)**: <!-- performance notes -->

## 💡 Suggested Optimizations

**Potential improvements:**

- [ ] Parallel processing
- [ ] Memory optimization
- [ ] Caching mechanisms
- [ ] Algorithm improvements
- [ ] Early termination optimizations
- [ ] Streaming processing
- [ ] Index/preprocessing
- [ ] Configuration optimizations

**Specific suggestions:**
<!-- Describe any specific optimization ideas you have -->

## 📋 Test Cases

**Small dataset test:**

- **Files**: <!-- e.g., 10 files, 100 lines each -->
- **Performance**: <!-- current behavior -->

**Medium dataset test:**

- **Files**: <!-- e.g., 100 files, 500 lines each -->
- **Performance**: <!-- current behavior -->

**Large dataset test:**

- **Files**: <!-- e.g., 1000+ files, large notebooks -->
- **Performance**: <!-- current behavior -->

## 🔍 Workarounds

**Current workarounds used:**

- [ ] Processing smaller batches
- [ ] Excluding large files
- [ ] Using fewer patterns
- [ ] Running on smaller datasets
- [ ] Other: <!-- specify -->

## 📊 Benchmarking

**Comparative performance:**
<!-- How does it compare to other similar tools? -->

**Regression testing:**

- [ ] Performance was better in previous version
- [ ] Performance has always been this way
- [ ] Performance degraded after specific change
- **Previous version tested**: <!-- if applicable -->

## 🎯 Success Criteria

**Performance goals:**

- **Target processing time**: <!-- e.g., <10 seconds for 100 files -->
- **Memory usage limit**: <!-- e.g., <500MB peak usage -->
- **Scalability target**: <!-- e.g., handle 10,000 files -->

---

**Checklist before submitting:**

- [ ] I have measured the actual performance impact
- [ ] I have provided specific reproduction steps
- [ ] I have tested with different dataset sizes
- [ ] I have included system specifications
- [ ] I have considered potential optimization approaches
