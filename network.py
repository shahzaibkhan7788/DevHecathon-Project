import time
import requests

def measure_latency(host="https://www.google.com", timeout=2):
    """
    Measures latency to a reliable host to determine network conditions.
    Returns average latency in milliseconds.
    """
    latencies = []
    # Take 3 measurements
    for _ in range(3):
        try:
            start_time = time.time()
            requests.get(host, timeout=timeout)
            end_time = time.time()
            latencies.append((end_time - start_time) * 1000)
        except requests.RequestException:
            # If request fails, assume very high latency
            latencies.append(9999) 
    
    avg_latency = sum(latencies) / len(latencies)
    return avg_latency

def get_network_mode(latency_ms):
    """
    Determines reasoning mode based on latency.
    < 100ms: DEEP (Tree of Thought)
    100ms - 300ms: STANDARD (Chain of Thought)
    > 300ms: FAST (Direct)
    """
    if latency_ms < 100:
        return "DEEP"
    elif latency_ms < 300:
        return "STANDARD"
    else:
        return "FAST"

if __name__ == "__main__":
    lat = measure_latency()
    mode = get_network_mode(lat)
    print(f"Latency: {lat:.2f}ms | Mode: {mode}")
