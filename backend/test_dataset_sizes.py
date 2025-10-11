#!/usr/bin/env python3
"""
Test Dataset Size Limits
Measures real performance with various dataset sizes
"""

import pandas as pd
import numpy as np
import time
import psutil
import os
import sys
import tempfile
from datetime import datetime

# Add backend root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.agents.simple_workflow import run_data_analysis


def format_size(size_bytes):
    """Format bytes to human readable"""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def format_time(seconds):
    """Format seconds to human readable"""
    if seconds < 0.001:
        return f"{seconds * 1000000:.0f}μs"
    elif seconds < 1:
        return f"{seconds * 1000:.2f}ms"
    else:
        return f"{seconds:.2f}s"


def generate_test_dataset(rows: int, cols: int) -> pd.DataFrame:
    """Generate test dataset with realistic data"""
    np.random.seed(42)  # For reproducibility

    data = {}

    # Add ID column
    data["id"] = range(1, rows + 1)

    # Add numeric columns
    for i in range(cols // 2):
        data[f"numeric_{i}"] = np.random.uniform(0, 1000, rows)

    # Add categorical columns
    categories = ["Category_A", "Category_B", "Category_C", "Category_D", "Category_E"]
    for i in range(cols - (cols // 2) - 1):
        data[f"category_{i}"] = np.random.choice(categories, rows)

    return pd.DataFrame(data)


def test_dataset_size(rows: int, cols: int, description: str):
    """Test analysis with specific dataset size"""
    print(f"\n{'=' * 80}")
    print(f"Testing: {description}")
    print(f"{'=' * 80}")
    print(f"Dataset: {rows:,} rows × {cols} columns")

    # Get memory before
    process = psutil.Process()
    mem_before = process.memory_info().rss

    # Generate dataset
    print("Generating test data...")
    gen_start = time.time()
    df = generate_test_dataset(rows, cols)
    gen_time = time.time() - gen_start
    print(f"  ✅ Generated in {format_time(gen_time)}")

    # Save to temp CSV
    temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False)
    temp_path = temp_file.name
    temp_file.close()

    print("Writing to CSV...")
    write_start = time.time()
    df.to_csv(temp_path, index=False)
    write_time = time.time() - write_start

    file_size = os.path.getsize(temp_path)
    print(f"  ✅ Written in {format_time(write_time)}")
    print(f"  📁 File size: {format_size(file_size)}")

    # Memory after CSV write
    mem_after_write = process.memory_info().rss
    mem_csv = mem_after_write - mem_before

    # Run analysis
    print("\nRunning analysis...")
    analysis_start = time.time()

    try:
        result = run_data_analysis(temp_path, f"test_{rows}x{cols}.csv")
        analysis_time = time.time() - analysis_start

        # Memory after analysis
        mem_after_analysis = process.memory_info().rss
        mem_peak = mem_after_analysis - mem_before

        print(f"  ✅ Analysis completed in {format_time(analysis_time)}")

        if result.get("success"):
            print("  ✅ Status: SUCCESS")

            # Show some results
            data_profile = result.get("data_profile", {})
            analysis_results = result.get("analysis_results", {})
            insights = result.get("insights", [])

            print("\n  📊 Results:")
            print(f"     Shape: {data_profile.get('shape', 'N/A')}")
            print(
                f"     Numeric columns: {len(data_profile.get('numeric_columns', []))}"
            )
            print(
                f"     Categorical columns: {len(data_profile.get('categorical_columns', []))}"
            )
            print(
                f"     Correlations found: {len(analysis_results.get('correlations', []))}"
            )
            print(f"     Insights generated: {len(insights)}")

            # Estimate database JSON size
            import json

            full_data_size = len(json.dumps(data_profile.get("full_data", [])))
            print(f"     Full data JSON size: {format_size(full_data_size)}")

        else:
            print("  ❌ Status: FAILED")
            print(f"     Error: {result.get('error', 'Unknown error')}")

        # Performance metrics
        print("\n  📈 Performance Metrics:")
        print(f"     CSV read + analysis: {format_time(analysis_time)}")
        print(f"     Memory used: {format_size(mem_peak)}")
        print(f"     Memory efficiency: {mem_peak / file_size:.1f}x file size")
        print(f"     Processing rate: {rows / analysis_time:.0f} rows/sec")

        # Performance rating
        if analysis_time < 0.1:
            rating = "✅ EXCELLENT"
        elif analysis_time < 1:
            rating = "✅ GOOD"
        elif analysis_time < 5:
            rating = "🟡 ACCEPTABLE"
        elif analysis_time < 30:
            rating = "🟠 SLOW"
        else:
            rating = "🔴 VERY SLOW"

        print(f"     Rating: {rating}")

        return {
            "rows": rows,
            "cols": cols,
            "file_size_bytes": file_size,
            "generation_time_s": gen_time,
            "write_time_s": write_time,
            "analysis_time_s": analysis_time,
            "memory_peak_bytes": mem_peak,
            "success": result.get("success", False),
            "error": result.get("error"),
            "rating": rating,
        }

    except Exception as e:
        analysis_time = time.time() - analysis_start
        mem_after_error = process.memory_info().rss
        mem_peak = mem_after_error - mem_before

        print(f"  ❌ ERROR after {format_time(analysis_time)}")
        print(f"     {type(e).__name__}: {str(e)}")
        print(f"     Memory at error: {format_size(mem_peak)}")

        return {
            "rows": rows,
            "cols": cols,
            "file_size_bytes": file_size,
            "analysis_time_s": analysis_time,
            "memory_peak_bytes": mem_peak,
            "success": False,
            "error": str(e),
            "rating": "❌ FAILED",
        }

    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)

        # Force garbage collection
        import gc

        gc.collect()


def main():
    """Run dataset size tests"""
    print("=" * 80)
    print("DATASET SIZE PERFORMANCE TESTING")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Pandas: {pd.__version__}")

    # Test configurations
    test_configs = [
        # (rows, cols, description)
        (1_000, 10, "Small Dataset (Baseline)"),
        (5_000, 10, "Small-Medium Dataset"),
        (10_000, 10, "Medium Dataset"),
        (25_000, 10, "Medium-Large Dataset"),
        (50_000, 10, "Large Dataset"),
        (100_000, 10, "Very Large Dataset"),
        (250_000, 10, "Extra Large Dataset"),
    ]

    results = []

    for rows, cols, description in test_configs:
        try:
            result = test_dataset_size(rows, cols, description)
            results.append(result)

            # Give system time to cool down
            time.sleep(2)

        except KeyboardInterrupt:
            print("\n\n⚠️  Testing interrupted by user")
            break
        except Exception as e:
            print(f"\n\n❌ Unexpected error: {e}")
            continue

    # Summary
    print(f"\n{'=' * 80}")
    print("SUMMARY")
    print(f"{'=' * 80}\n")

    if results:
        print(
            f"{'Rows':<12} {'File Size':<12} {'Time':<12} {'Memory':<12} {'Rate':<15} {'Status'}"
        )
        print("-" * 80)

        for r in results:
            if r.get("success") is not False:
                rate = f"{r['rows'] / r['analysis_time_s']:.0f} rows/s"
                status = r["rating"]
            else:
                rate = "N/A"
                status = "❌ Failed"

            print(
                f"{r['rows']:<12,} "
                f"{format_size(r['file_size_bytes']):<12} "
                f"{format_time(r['analysis_time_s']):<12} "
                f"{format_size(r.get('memory_peak_bytes', 0)):<12} "
                f"{rate:<15} "
                f"{status}"
            )

        # Recommendations
        print(f"\n{'=' * 80}")
        print("RECOMMENDATIONS")
        print(f"{'=' * 80}\n")

        excellent = [r for r in results if "EXCELLENT" in r.get("rating", "")]
        good = [r for r in results if "GOOD" in r.get("rating", "")]
        acceptable = [r for r in results if "ACCEPTABLE" in r.get("rating", "")]
        slow = [r for r in results if "SLOW" in r.get("rating", "")]
        failed = [r for r in results if r.get("success") is False]

        if excellent:
            max_excellent = max(excellent, key=lambda x: x["rows"])
            print(f"✅ Excellent performance up to: {max_excellent['rows']:,} rows")

        if good:
            max_good = max(good, key=lambda x: x["rows"])
            print(f"✅ Good performance up to: {max_good['rows']:,} rows")

        if acceptable:
            max_acceptable = max(acceptable, key=lambda x: x["rows"])
            print(f"🟡 Acceptable performance up to: {max_acceptable['rows']:,} rows")

        if slow:
            min_slow = min(slow, key=lambda x: x["rows"])
            print(f"🟠 Performance degrades at: {min_slow['rows']:,} rows")

        if failed:
            min_failed = min(failed, key=lambda x: x["rows"])
            print(f"❌ System fails at: {min_failed['rows']:,} rows")
            print(f"   Error: {min_failed.get('error', 'Unknown')}")

        # Save results to file
        import json

        output_file = "dataset_size_test_results.json"
        with open(output_file, "w") as f:
            json.dump(
                {
                    "timestamp": datetime.now().isoformat(),
                    "python_version": sys.version.split()[0],
                    "pandas_version": pd.__version__,
                    "results": results,
                },
                f,
                indent=2,
            )

        print(f"\n💾 Results saved to: {output_file}")

    print(f"\n{'=' * 80}")
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 80}\n")


if __name__ == "__main__":
    main()
