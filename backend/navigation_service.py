import heapq
import math

class NavigationService:
    def __init__(self):
        # Mock Graph Representation of ACL Venue (Zilker Park)
        # Nodes: id -> {lat, lng, type (stage, exit, medical, path)}
        self.nodes = {
            "entry_main": {"lat": 30.2690, "lng": -97.7710, "type": "entry"},
            "stage_amex": {"lat": 30.2675, "lng": -97.7690, "type": "stage"},
            "stage_tmobile": {"lat": 30.2650, "lng": -97.7750, "type": "stage"},
            "food_court": {"lat": 30.2665, "lng": -97.7720, "type": "food"},
            "medical_tent": {"lat": 30.2680, "lng": -97.7730, "type": "medical"},
            "exit_south": {"lat": 30.2640, "lng": -97.7760, "type": "exit"},
            # Path nodes (intersection points)
            "path_1": {"lat": 30.2685, "lng": -97.7700, "type": "path"},
            "path_2": {"lat": 30.2670, "lng": -97.7710, "type": "path"},
            "path_3": {"lat": 30.2660, "lng": -97.7735, "type": "path"},
            # "Hazard" node (e.g. mud, steep hill)
            "path_steep": {"lat": 30.2655, "lng": -97.7740, "type": "path"},
        }

        # Edges: (from, to) -> {distance (m), accessible (bool), base_risk (0-1)}
        # Connected bi-directionally
        self.edges = [
            ("entry_main", "path_1", 100, True, 0.1),
            ("path_1", "stage_amex", 150, True, 0.8), # High crowd risk
            ("path_1", "medical_tent", 200, True, 0.0), # Safe path
            ("medical_tent", "path_2", 120, True, 0.1),
            ("path_2", "food_court", 80, True, 0.4),
            ("path_2", "path_3", 150, True, 0.2),
            ("path_3", "stage_tmobile", 100, True, 0.7),
            ("path_3", "exit_south", 300, True, 0.0),
            ("stage_tmobile", "path_steep", 50, False, 0.3), # Not accessible!
            ("path_steep", "exit_south", 250, False, 0.3),   # Not accessible!
        ]

        # Build adjacency list
        self.graph = {node: [] for node in self.nodes}
        for u, v, dist, access, risk in self.edges:
            self.graph[u].append({"to": v, "dist": dist, "access": access, "risk": risk})
            self.graph[v].append({"to": u, "dist": dist, "access": access, "risk": risk})

    def get_closest_node(self, lat, lng):
        """Finds the nearest graph node to a coordinate."""
        min_dist = float('inf')
        closest = None
        for node, data in self.nodes.items():
            dist = math.sqrt((data["lat"] - lat)**2 + (data["lng"] - lng)**2)
            if dist < min_dist:
                min_dist = dist
                closest = node
        return closest

    def calculate_route(self, start_lat, start_lng, end_lat=None, end_lng=None,
                        wheelchair=False, avoid_crowds=False, closest_exit=False):

        start_node = self.get_closest_node(start_lat, start_lng)

        # Determine target(s)
        targets = []
        if closest_exit:
            targets = [n for n, d in self.nodes.items() if d["type"] == "exit"]
        elif end_lat and end_lng:
            targets = [self.get_closest_node(end_lat, end_lng)]

        if not start_node or not targets:
            return []

        # Dijkstra
        pq = [(0, start_node, [])] # (cost, current_node, path)
        visited = set()

        while pq:
            cost, u, path = heapq.heappop(pq)

            if u in visited:
                continue
            visited.add(u)

            path = path + [self.nodes[u]] # Store node data in path

            if u in targets:
                return path # Found valid route

            for edge in self.graph[u]:
                v = edge["to"]

                # Accessibility Constraint
                if wheelchair and not edge["access"]:
                    continue

                # Weight Calculation
                # Base distance
                edge_weight = edge["dist"]

                # Crowd Penalty (if avoid_crowds is ON)
                if avoid_crowds:
                    edge_weight *= (1 + edge["risk"] * 5) # High penalty for crowds

                if v not in visited:
                    heapq.heappush(pq, (cost + edge_weight, v, path))

        return [] # No route found

    def get_markers(self):
        """Returns accessibility landmarks."""
        markers = []
        for id, data in self.nodes.items():
            if data["type"] in ["medical", "exit", "entry", "stage"]:
                markers.append({"id": id, **data})
        return markers
