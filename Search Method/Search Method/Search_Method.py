import csv
import time
import heapq
from collections import deque
from math import radians, sin, cos, sqrt, atan2

# Load city data from a CSV file, storing city names with their latitude and longitude
def load_cities(filename):
    cities = {}
    try:
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) < 3:
                    continue  # Skip malformed lines
                name, lat, lon = row
                cities[name] = (float(lat), float(lon))
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        exit(1)
    return cities

# Load adjacency list from a file, representing the connectivity of cities
def load_adjacency(filename):
    adjacency_list = {}
    try:
        with open(filename, 'r') as file:
            for line in file:
                parts = line.strip().split()
                if len(parts) < 2:
                    continue  # Skip malformed lines
                city1, city2 = parts
                adjacency_list.setdefault(city1, []).append(city2)
                adjacency_list.setdefault(city2, []).append(city1)  # Ensure bidirectionality
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        exit(1)
    return adjacency_list

# Calculate the Haversine distance between two latitude-longitude coordinates
def haversine(coord1, coord2):
    R = 6371  # Earth's radius in km
    lat1, lon1 = map(radians, coord1)
    lat2, lon2 = map(radians, coord2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return 2 * R * atan2(sqrt(a), sqrt(1 - a))


# Brute force search (DFS) exploring all possible paths
def brute_force_search(start, goal, adjacency_list, cities):
    stack = [(start, [start])]
    while stack:
        city, path = stack.pop()
        if city == goal:
            return path
        for neighbor in adjacency_list.get(city, []):
            if neighbor not in path:
                stack.append((neighbor, path + [neighbor]))
    return None

# Breadth-First Search (BFS) for shortest unweighted path
def bfs(start, goal, adjacency_list):
    queue = deque([(start, [start])])
    while queue:
        city, path = queue.popleft()
        if city == goal:
            return path
        for neighbor in adjacency_list.get(city, []):
            if neighbor not in path:
                queue.append((neighbor, path + [neighbor]))
    return None

# Depth-First Search (DFS) for pathfinding
def dfs(start, goal, adjacency_list):
    stack = [(start, [start])]
    while stack:
        city, path = stack.pop()
        if city == goal:
            return path
        for neighbor in adjacency_list.get(city, []):
            if neighbor not in path:
                stack.append((neighbor, path + [neighbor]))
    return None

# Best-First Search using Haversine heuristic
def best_first_search(start, goal, adjacency_list, cities):
    pq = [(haversine(cities[start], cities[goal]), start, [start])]
    while pq:
        _, city, path = heapq.heappop(pq)
        if city == goal:
            return path
        for neighbor in adjacency_list.get(city, []):
            if neighbor not in path:
                heapq.heappush(pq, (haversine(cities[neighbor], cities[goal]), neighbor, path + [neighbor]))
    return None

# A* Search using g(n) + h(n) heuristic
def a_star_search(start, goal, adjacency_list, cities):
    pq = [(0, start, [start], 0)]  # (f-score, city, path, g-score)
    visited = {}
    while pq:
        f, city, path, g = heapq.heappop(pq)
        if city == goal:
            return path
        for neighbor in adjacency_list.get(city, []):
            new_g = g + haversine(cities[city], cities[neighbor])
            new_f = new_g + haversine(cities[neighbor], cities[goal])
            if neighbor not in visited or new_g < visited[neighbor]:
                visited[neighbor] = new_g
                heapq.heappush(pq, (new_f, neighbor, path + [neighbor], new_g))
    return None

# Format the elapsed time for better readability
def format_time(elapsed_time):
    if elapsed_time < 1e-6:
        return f"{elapsed_time * 1e9:.2f} ns"
    elif elapsed_time < 1e-3:
        return f"{elapsed_time * 1e6:.2f} us"
    elif elapsed_time < 1:
        return f"{elapsed_time * 1e3:.2f} ms"
    else:
        return f"{elapsed_time:.4f} s"

def main():
    cities_file = input("Enter the cities file path: ")
    adjacency_file = input("Enter the adjacency file path: ")
    
    cities = load_cities(cities_file)
    adjacency_list = load_adjacency(adjacency_file)
    
    while True:
        print("Available cities:")
        print(", ".join(cities.keys()))
        
        start = input("Enter the starting city (or type 'list' to show all cities): ")
        if start.lower() == 'list':
            print(", ".join(cities.keys()))
            continue
        
        goal = input("Enter the destination city: ")
        
        if start not in cities or goal not in cities:
            print("Invalid city names.")
            continue
        
        while True:
            print("Choose a search method:")
            print("1. Brute Force Search")
            print("2. Breadth-First Search")
            print("3. Depth-First Search")
            print("4. Best-First Search")
            print("5. A* Search")
            
            choice = input("Enter your choice (1-5): ")
            
            search_methods = {
                '1': brute_force_search,
                '2': lambda s, g, adj, cities: bfs(s, g, adj),
                '3': lambda s, g, adj, cities: dfs(s, g, adj),
                '4': best_first_search,
                '5': a_star_search
            }
            
            if choice in search_methods:
                start_time = time.perf_counter()
                route = search_methods[choice](start, goal, adjacency_list, cities)
                end_time = time.perf_counter()
                elapsed_time = end_time - start_time
                
                if route:
                    print("Route found:", " -> ".join(route))
                    print(f"Time taken: {format_time(elapsed_time)}")
                    total_distance = sum(haversine(cities[route[i]], cities[route[i+1]]) for i in range(len(route)-1))
                    print("Total Distance: {:.2f} km".format(total_distance))
                else:
                    print("No route found.")
            else:
                print("Invalid choice.")
                continue
            
            next_action = input("Would you like to: (1) Try another method, (2) Choose different cities, or (3) Exit? ")
            if next_action == '2':
                break
            elif next_action == '3':
                return

if __name__ == "__main__":
    main()