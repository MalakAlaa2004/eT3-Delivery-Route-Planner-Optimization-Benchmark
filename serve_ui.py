"""
Lightweight HTTP Server for the eT3 Delivery Route Planner Visualizer.
Runs with ZERO external dependencies (Python standard library only).
"""

import http.server
import socketserver
import json
import os
import webbrowser
import sys
from urllib.parse import urlparse
from src.models import Delivery
from src.solvers.greedy import GreedySolver
from src.solvers.metaheuristics import SimulatedAnnealingSolver, GeneticAlgorithmSolver

PORT = 8080
WEB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")


class DeliveryApiHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/solve":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            try:
                data = json.loads(body)
                algo = data.get("algorithm", "greedy")
                raw_deliveries = data.get("deliveries", [])

                deliveries = [
                    Delivery(
                        id=d.get("id"),
                        area=d.get("area"),
                        priority=d.get("priority", 2),
                        weight=d.get("weight", 0.0)
                    )
                    for d in raw_deliveries
                ]

                if algo == "sa":
                    solver = SimulatedAnnealingSolver()
                elif algo == "ga":
                    solver = GeneticAlgorithmSolver()
                else:
                    solver = GreedySolver()

                plan = solver.solve(deliveries)

                response_payload = {
                    "algorithm": plan.algorithm_name,
                    "time_ms": plan.execution_time_ms,
                    "trips": [
                        {
                            "trip_id": t.trip_id,
                            "deliveries": [
                                {
                                    "id": d.id,
                                    "area": d.area,
                                    "priority": d.priority,
                                    "weight": d.weight
                                }
                                for d in t.deliveries
                            ]
                        }
                        for t in plan.trips
                    ],
                    "unassigned": [
                        {
                            "delivery": {
                                "id": d.id,
                                "area": d.area,
                                "priority": d.priority,
                                "weight": d.weight
                            },
                            "reason": reason
                        }
                        for d, reason in plan.unassigned
                    ]
                }

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(response_payload).encode("utf-8"))
                return

            except Exception as err:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(err)}).encode("utf-8"))
                return

        self.send_response(404)
        self.end_headers()


def start_server():
    print("=" * 76)
    print(f"eT3 Delivery Route Planner - Visualizer Server")
    print(f"Serving UI at: http://localhost:{PORT}")
    print("Press Ctrl+C to stop the server.")
    print("=" * 76)

    # Allow immediate reuse of address
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), DeliveryApiHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")
            sys.exit(0)


if __name__ == "__main__":
    start_server()
