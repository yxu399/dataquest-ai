#!/usr/bin/env python3
"""
Measure API Response Times
Simple script to measure real API endpoint response times
"""

import requests
import time
import statistics
import json
from typing import Tuple


BASE_URL = "http://localhost:8000"
ITERATIONS = 10


def measure_request(
    url: str, method: str = "GET", data: dict = None, files: dict = None
) -> Tuple[float, int, str]:
    """
    Measure a single request
    Returns: (response_time_ms, status_code, error_message)
    """
    try:
        start = time.time()

        if method == "GET":
            response = requests.get(url, timeout=30)
        elif method == "POST":
            if files:
                response = requests.post(url, files=files, timeout=30)
            else:
                response = requests.post(url, json=data, timeout=30)
        else:
            return 0, 0, f"Unsupported method: {method}"

        elapsed = (time.time() - start) * 1000  # Convert to ms

        return elapsed, response.status_code, None

    except requests.exceptions.Timeout:
        return 0, 0, "Request timeout"
    except requests.exceptions.ConnectionError:
        return 0, 0, "Connection error - is the server running?"
    except Exception as e:
        return 0, 0, str(e)


def measure_endpoint(
    name: str,
    url: str,
    method: str = "GET",
    data: dict = None,
    files: dict = None,
    iterations: int = ITERATIONS,
) -> dict:
    """
    Measure an endpoint multiple times and return statistics
    """
    print(f"\nTesting: {name}")
    print(f"  {method} {url}")

    times = []
    errors = 0

    for i in range(iterations):
        elapsed, status_code, error = measure_request(url, method, data, files)

        if error:
            errors += 1
            if i == 0:  # Print error on first iteration
                print(f"  ❌ Error: {error}")
            continue

        times.append(elapsed)

        # Print progress
        if i == 0:
            print(f"  Status: {status_code}")

    if not times:
        print(f"  ❌ All requests failed ({errors} errors)")
        return {
            "name": name,
            "endpoint": url,
            "method": method,
            "error": "All requests failed",
            "success_count": 0,
            "error_count": errors,
        }

    # Calculate statistics
    mean_time = statistics.mean(times)
    min_time = min(times)
    max_time = max(times)
    median_time = statistics.median(times)

    if len(times) > 1:
        stddev = statistics.stdev(times)
    else:
        stddev = 0

    # Print results
    print(f"  ✅ Mean: {mean_time:.2f}ms")
    print(
        f"  📊 Min: {min_time:.2f}ms | Max: {max_time:.2f}ms | Median: {median_time:.2f}ms"
    )
    if stddev > 0:
        print(f"  📈 Std Dev: {stddev:.2f}ms")
    if errors > 0:
        print(f"  ⚠️  Errors: {errors}/{iterations}")

    return {
        "name": name,
        "endpoint": url,
        "method": method,
        "mean_ms": round(mean_time, 2),
        "min_ms": round(min_time, 2),
        "max_ms": round(max_time, 2),
        "median_ms": round(median_time, 2),
        "stddev_ms": round(stddev, 2),
        "success_count": len(times),
        "error_count": errors,
        "total_iterations": iterations,
    }


def main():
    """Main function to measure all endpoints"""
    print("=" * 60)
    print("API Response Time Measurement")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}")
    print(f"Iterations per endpoint: {ITERATIONS}")

    results = []

    # Basic Endpoints
    print("\n" + "=" * 60)
    print("BASIC ENDPOINTS")
    print("=" * 60)

    results.append(measure_endpoint("Root Endpoint", f"{BASE_URL}/"))

    results.append(measure_endpoint("Health Check", f"{BASE_URL}/health"))

    results.append(measure_endpoint("API Test", f"{BASE_URL}/api/v1/test"))

    results.append(measure_endpoint("OpenAPI JSON", f"{BASE_URL}/openapi.json"))

    # File Endpoints
    print("\n" + "=" * 60)
    print("FILE ENDPOINTS")
    print("=" * 60)

    results.append(
        measure_endpoint("List Analyses", f"{BASE_URL}/api/v1/files/analyses")
    )

    # Test with a non-existent ID (should return 404)
    results.append(
        measure_endpoint(
            "Get Analysis Status (404)",
            f"{BASE_URL}/api/v1/files/analysis/999999/status",
        )
    )

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    # Filter successful results
    successful = [r for r in results if r.get("mean_ms")]

    if successful:
        print(f"\nTotal Endpoints Tested: {len(results)}")
        print(f"Successful: {len(successful)}")
        print(f"Failed: {len(results) - len(successful)}")

        print("\n📊 Response Time Rankings (fastest to slowest):")
        print("-" * 60)

        # Sort by mean response time
        sorted_results = sorted(successful, key=lambda x: x["mean_ms"])

        for i, result in enumerate(sorted_results, 1):
            status_icon = (
                "🟢"
                if result["mean_ms"] < 10
                else "🟡"
                if result["mean_ms"] < 50
                else "🔴"
            )
            print(f"{i}. {status_icon} {result['name']}: {result['mean_ms']:.2f}ms")

        # Overall statistics
        all_means = [r["mean_ms"] for r in successful]
        print("\n📈 Overall Statistics:")
        print(f"  Average response time: {statistics.mean(all_means):.2f}ms")
        print(f"  Fastest endpoint: {min(all_means):.2f}ms")
        print(f"  Slowest endpoint: {max(all_means):.2f}ms")

        # Save results to JSON
        output_file = "api_response_times_results.json"
        with open(output_file, "w") as f:
            json.dump(
                {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "base_url": BASE_URL,
                    "iterations": ITERATIONS,
                    "results": results,
                },
                f,
                indent=2,
            )

        print(f"\n💾 Results saved to: {output_file}")
    else:
        print("\n❌ No successful requests - is the server running?")
        print("   Start the server with: uv run python main.py")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
