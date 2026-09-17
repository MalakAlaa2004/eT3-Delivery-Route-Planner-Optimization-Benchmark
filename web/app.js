/**
 * eT3 Delivery Route Planner - Interactive Visualizer & Solver
 * Works standalone (file://) and connected with Python backend (http://)
 */

// Cairo Area Geographic Coordinates (normalized 0.0 - 1.0)
const AREA_COORDINATES = {
  "Nasr City": { x: 0.65, y: 0.35, color: "#38bdf8" },
  "Maadi": { x: 0.55, y: 0.75, color: "#10b981" },
  "Zamalek": { x: 0.38, y: 0.42, color: "#f59e0b" },
  "Heliopolis": { x: 0.70, y: 0.18, color: "#ec4899" },
  "Dokki": { x: 0.32, y: 0.52, color: "#a855f7" },
  "New Cairo": { x: 0.85, y: 0.48, color: "#06b6d4" },
  "6th of October": { x: 0.15, y: 0.72, color: "#f97316" }
};

// Embedded Datasets for 100% offline standalone capability
const EMBEDDED_DATASETS = {
  sample: [
    { id: 1, area: "Nasr City", priority: 2, weight: 4.5 },
    { id: 2, area: "Maadi", priority: 1, weight: 2.0 },
    { id: 3, area: "Nasr City", priority: 3, weight: 1.2 },
    { id: 4, area: "Zamalek", priority: 1, weight: 7.0 },
    { id: 5, area: "Maadi", priority: 2, weight: 3.5 }
  ],
  edge_cases: [
    { id: 101, area: "Nasr City", priority: 1, weight: 6.0 },
    { id: 102, area: "Nasr City", priority: 1, weight: 4.0 },
    { id: 103, area: "Nasr City", priority: 1, weight: 1.5 },
    { id: 104, area: "Maadi", priority: 2, weight: 10.0 },
    { id: 105, area: "Zamalek", priority: 1, weight: 14.5 },
    { id: 106, area: "Heliopolis", priority: 2, weight: 0.5 },
    { id: 107, area: "Heliopolis", priority: 2, weight: 3.0 },
    { id: 108, area: "Dokki", priority: 3, weight: 8.0 },
    { id: 109, area: "Dokki", priority: 3, weight: 2.0 }
  ],
  cairo_large: [
    { id: 1, area: "Nasr City", priority: 1, weight: 3.2 },
    { id: 2, area: "Maadi", priority: 2, weight: 4.1 },
    { id: 3, area: "New Cairo", priority: 1, weight: 5.5 },
    { id: 4, area: "Zamalek", priority: 1, weight: 2.8 },
    { id: 5, area: "Heliopolis", priority: 3, weight: 1.5 },
    { id: 6, area: "Nasr City", priority: 1, weight: 2.0 },
    { id: 7, area: "Dokki", priority: 2, weight: 6.2 },
    { id: 8, area: "Maadi", priority: 1, weight: 1.8 },
    { id: 9, area: "New Cairo", priority: 2, weight: 3.0 },
    { id: 10, area: "6th of October", priority: 3, weight: 7.5 },
    { id: 11, area: "Zamalek", priority: 2, weight: 4.0 },
    { id: 12, area: "Heliopolis", priority: 1, weight: 3.5 },
    { id: 13, area: "Nasr City", priority: 2, weight: 4.8 },
    { id: 14, area: "Maadi", priority: 3, weight: 2.2 },
    { id: 15, area: "Dokki", priority: 1, weight: 1.5 },
    { id: 16, area: "New Cairo", priority: 1, weight: 4.0 },
    { id: 17, area: "6th of October", priority: 2, weight: 2.0 },
    { id: 18, area: "Heliopolis", priority: 2, weight: 2.8 },
    { id: 19, area: "Zamalek", priority: 1, weight: 3.1 },
    { id: 20, area: "Nasr City", priority: 3, weight: 0.9 },
    { id: 21, area: "Maadi", priority: 1, weight: 5.0 },
    { id: 22, area: "Dokki", priority: 2, weight: 2.5 },
    { id: 23, area: "New Cairo", priority: 3, weight: 1.2 },
    { id: 24, area: "6th of October", priority: 1, weight: 4.5 },
    { id: 25, area: "Heliopolis", priority: 1, weight: 2.2 },
    { id: 26, area: "Nasr City", priority: 2, weight: 3.0 },
    { id: 27, area: "Maadi", priority: 2, weight: 1.5 },
    { id: 28, area: "Zamalek", priority: 3, weight: 1.0 },
    { id: 29, area: "Dokki", priority: 1, weight: 4.2 },
    { id: 30, area: "New Cairo", priority: 2, weight: 2.8 },
    { id: 31, area: "6th of October", priority: 2, weight: 3.0 },
    { id: 32, area: "Heliopolis", priority: 3, weight: 4.0 },
    { id: 33, area: "Nasr City", priority: 1, weight: 1.5 },
    { id: 34, area: "Maadi", priority: 3, weight: 3.0 },
    { id: 35, area: "Dokki", priority: 3, weight: 1.8 },
    { id: 36, area: "New Cairo", priority: 1, weight: 2.5 },
    { id: 37, area: "Zamalek", priority: 2, weight: 2.0 },
    { id: 38, area: "6th of October", priority: 3, weight: 1.2 },
    { id: 39, area: "Heliopolis", priority: 2, weight: 1.9 },
    { id: 40, area: "Nasr City", priority: 2, weight: 2.1 },
    { id: 41, area: "Maadi", priority: 1, weight: 2.8 },
    { id: 42, area: "Dokki", priority: 1, weight: 3.0 },
    { id: 43, area: "New Cairo", priority: 2, weight: 3.7 },
    { id: 44, area: "Zamalek", priority: 1, weight: 1.5 },
    { id: 45, area: "6th of October", priority: 1, weight: 2.5 },
    { id: 46, area: "Heliopolis", priority: 1, weight: 1.8 },
    { id: 47, area: "Nasr City", priority: 3, weight: 3.5 },
    { id: 48, area: "Maadi", priority: 2, weight: 2.0 },
    { id: 49, area: "Dokki", priority: 2, weight: 1.2 },
    { id: 50, area: "New Cairo", priority: 3, weight: 2.0 }
  ]
};

// Distinct trip colors for visual distinction
const TRIP_COLORS = [
  "#38bdf8", "#818cf8", "#34d399", "#fbbf24", "#f472b6",
  "#c084fc", "#60a5fa", "#4ade80", "#f87171", "#2dd4bf",
  "#e879f9", "#fb923c", "#a3e635", "#38bdf8", "#818cf8"
];

// App State
let currentDeliveries = [];
let currentPlan = null;
let searchQuery = "";

// DOM Elements
const datasetSelect = document.getElementById("datasetSelect");
const algoSelect = document.getElementById("algoSelect");
const searchInput = document.getElementById("searchInput");
const solveBtn = document.getElementById("solveBtn");
const warningBanner = document.getElementById("warningBanner");
const warningMessage = document.getElementById("warningMessage");
const benchmarkSection = document.getElementById("benchmarkSection");
const benchmarkTableBody = document.getElementById("benchmarkTableBody");
const tripsGrid = document.getElementById("tripsGrid");
const mapCanvas = document.getElementById("mapCanvas");
const ctx = mapCanvas.getContext("2d");

// KPI Elements
const metricTrips = document.getElementById("metricTrips");
const metricUtilization = document.getElementById("metricUtilization");
const metricPurity = document.getElementById("metricPurity");
const metricTime = document.getElementById("metricTime");
const metricAlgoName = document.getElementById("metricAlgoName");
const pointCountBadge = document.getElementById("pointCountBadge");
const tripCountBadge = document.getElementById("tripCountBadge");

// Setup Canvas Resolution
function resizeCanvas() {
  const rect = mapCanvas.parentElement.getBoundingClientRect();
  mapCanvas.width = rect.width;
  mapCanvas.height = Math.max(rect.height, 440);
  drawCanvas();
}

window.addEventListener("resize", resizeCanvas);

// Client-Side Deterministic Greedy Solver
function solveGreedy(deliveries, maxCapacity = 10.0) {
  const startTime = performance.now();
  const valid = [];
  const unassigned = [];

  for (const d of deliveries) {
    if (d.weight > maxCapacity) {
      unassigned.push({ delivery: d, reason: `Weight (${d.weight} kg) exceeds vehicle max capacity (10.0 kg)` });
    } else {
      valid.push(d);
    }
  }

  // Sort: Priority asc (urgent first), then Area, then Weight desc
  valid.sort((a, b) => {
    if (a.priority !== b.priority) return a.priority - b.priority;
    if (a.area !== b.area) return a.area.localeCompare(b.area);
    return b.weight - a.weight;
  });

  const trips = [];
  let tripId = 1;

  for (const pkg of valid) {
    let assigned = false;
    // Best-fit same area
    let bestTrip = null;
    let minRemaining = Infinity;

    for (const trip of trips) {
      const areas = new Set(trip.deliveries.map(d => d.area));
      const currentWeight = trip.deliveries.reduce((sum, d) => sum + d.weight, 0);
      if (areas.has(pkg.area) && currentWeight + pkg.weight <= maxCapacity + 0.0001) {
        const remaining = maxCapacity - (currentWeight + pkg.weight);
        if (remaining < minRemaining) {
          minRemaining = remaining;
          bestTrip = trip;
        }
      }
    }

    if (bestTrip) {
      bestTrip.deliveries.push(pkg);
      assigned = true;
    } else {
      trips.push({ trip_id: tripId++, deliveries: [pkg] });
    }
  }

  // Sort trips by minimum priority
  trips.sort((a, b) => {
    const minPrioA = Math.min(...a.deliveries.map(d => d.priority));
    const minPrioB = Math.min(...b.deliveries.map(d => d.priority));
    return minPrioA - minPrioB;
  });

  // Re-index trip ids
  trips.forEach((t, i) => t.trip_id = i + 1);

  const elapsed = performance.now() - startTime;
  return {
    algorithm: "Greedy Heuristic",
    trips,
    unassigned,
    time_ms: elapsed
  };
}

// Client-Side Simulated Annealing Solver
function solveSimulatedAnnealing(deliveries, maxCapacity = 10.0) {
  const startTime = performance.now();
  const valid = deliveries.filter(d => d.weight <= maxCapacity);
  const unassigned = deliveries
    .filter(d => d.weight > maxCapacity)
    .map(d => ({ delivery: d, reason: `Weight (${d.weight} kg) exceeds vehicle max capacity (10.0 kg)` }));

  if (valid.length === 0) {
    return { algorithm: "Simulated Annealing", trips: [], unassigned, time_ms: performance.now() - startTime };
  }

  // Cost function
  function evalCost(assignment) {
    const buckets = {};
    for (const d of valid) {
      const tid = assignment[d.id];
      if (!buckets[tid]) buckets[tid] = [];
      buckets[tid].push(d);
    }
    let cost = Object.keys(buckets).length * 80;
    for (const tid in buckets) {
      const pkgs = buckets[tid];
      const weight = pkgs.reduce((s, p) => s + p.weight, 0);
      if (weight > maxCapacity) {
        cost += 10000 + (weight - maxCapacity) * 5000;
      }
      const areas = new Set(pkgs.map(p => p.area));
      if (areas.size > 1) {
        cost += (areas.size - 1) * 40;
      }
    }
    return cost;
  }

  // Initial greedy-like assignment
  let current = {};
  let tid = 1;
  let curW = 0;
  let curArea = null;
  for (const d of valid) {
    if (curArea !== d.area || curW + d.weight > maxCapacity) {
      tid++;
      curW = 0;
      curArea = d.area;
    }
    current[d.id] = tid;
    curW += d.weight;
  }

  let currentCost = evalCost(current);
  let best = { ...current };
  let bestCost = currentCost;

  let temp = 100.0;
  const cooling = 0.95;

  while (temp > 0.5) {
    for (let iter = 0; iter < 25; iter++) {
      const candidate = { ...current };
      const d = valid[Math.floor(Math.random() * valid.length)];
      const activeTids = Array.from(new Set(Object.values(candidate)));
      const targetTid = Math.random() < 0.85
        ? activeTids[Math.floor(Math.random() * activeTids.length)]
        : Math.max(...activeTids) + 1;

      candidate[d.id] = targetTid;
      const candCost = evalCost(candidate);
      const delta = candCost - currentCost;

      if (delta < 0 || Math.exp(-delta / temp) > Math.random()) {
        current = candidate;
        currentCost = candCost;
        if (currentCost < bestCost) {
          bestCost = currentCost;
          best = { ...candidate };
        }
      }
    }
    temp *= cooling;
  }

  // Build trips
  const buckets = {};
  for (const d of valid) {
    const t = best[d.id];
    if (!buckets[t]) buckets[t] = [];
    buckets[t].push(d);
  }

  const trips = Object.values(buckets).map((pkgs, i) => ({
    trip_id: i + 1,
    deliveries: pkgs
  }));

  trips.sort((a, b) => {
    const pA = Math.min(...a.deliveries.map(d => d.priority));
    const pB = Math.min(...b.deliveries.map(d => d.priority));
    return pA - pB;
  });
  trips.forEach((t, i) => t.trip_id = i + 1);

  return {
    algorithm: "Simulated Annealing",
    trips,
    unassigned,
    time_ms: performance.now() - startTime
  };
}

// Solver Execution Handler
async function runSolver() {
  const algo = algoSelect.value;
  benchmarkSection.classList.remove("active");

  if (algo === "compare") {
    runComparativeBenchmark();
    return;
  }

  // Attempt backend API, fallback to local JS solver
  let plan = null;
  try {
    const res = await fetch("/api/solve", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ algorithm: algo, deliveries: currentDeliveries })
    });
    if (res.ok) {
      plan = await res.json();
    }
  } catch (err) {
    // Backend offline / opened via file://, using pure JS solver
  }

  if (!plan) {
    if (algo === "sa" || algo === "ga") {
      plan = solveSimulatedAnnealing(currentDeliveries);
    } else {
      plan = solveGreedy(currentDeliveries);
    }
  }

  currentPlan = plan;
  updateUI(plan);
}

// Comparative Benchmark
function runComparativeBenchmark() {
  const greedyRes = solveGreedy(currentDeliveries);
  const saRes = solveSimulatedAnnealing(currentDeliveries);

  const results = [greedyRes, saRes];
  benchmarkSection.classList.add("active");
  benchmarkTableBody.innerHTML = "";

  results.forEach(res => {
    const totalW = res.trips.reduce((sum, t) => sum + t.deliveries.reduce((s, d) => s + d.weight, 0), 0);
    const util = res.trips.length > 0 ? ((totalW / (res.trips.length * 10)) * 100).toFixed(1) : 0;
    const pureTrips = res.trips.filter(t => new Set(t.deliveries.map(d => d.area)).size === 1).length;
    const purity = res.trips.length > 0 ? ((pureTrips / res.trips.length) * 100).toFixed(1) : 0;

    const row = document.createElement("tr");
    row.innerHTML = `
      <td><strong>${res.algorithm}</strong></td>
      <td>${res.trips.length}</td>
      <td><span style="color: var(--primary); font-weight: bold;">${util}%</span></td>
      <td>${purity}%</td>
      <td>${res.time_ms.toFixed(2)} ms</td>
      <td>${res.unassigned.length}</td>
    `;
    benchmarkTableBody.appendChild(row);
  });

  // Display greedy as primary visual
  currentPlan = greedyRes;
  updateUI(greedyRes);
}

// Update DOM and Visuals
function updateUI(plan) {
  // Update Warnings
  if (plan.unassigned && plan.unassigned.length > 0) {
    warningBanner.classList.add("active");
    warningMessage.innerHTML = `${plan.unassigned.length} package(s) exceeded the 10.0 kg limit: ` +
      plan.unassigned.map(u => `<b>#${u.delivery.id} (${u.delivery.weight} kg)</b>`).join(", ") +
      ` &bull; Flagged for heavy freight vehicle handling.`;
  } else {
    warningBanner.classList.remove("active");
  }

  // Update KPIs
  const totalTrips = plan.trips.length;
  const totalWeight = plan.trips.reduce((sum, t) => sum + t.deliveries.reduce((s, d) => s + d.weight, 0), 0);
  const utilization = totalTrips > 0 ? ((totalWeight / (totalTrips * 10.0)) * 100).toFixed(1) : 0;
  const pureTrips = plan.trips.filter(t => new Set(t.deliveries.map(d => d.area)).size === 1).length;
  const purity = totalTrips > 0 ? ((pureTrips / totalTrips) * 100).toFixed(0) : 0;

  metricTrips.textContent = totalTrips;
  metricUtilization.textContent = `${utilization}%`;
  metricPurity.textContent = `${purity}%`;
  metricTime.textContent = `${plan.time_ms.toFixed(2)} ms`;
  metricAlgoName.textContent = plan.algorithm;

  pointCountBadge.textContent = `${currentDeliveries.length} Deliveries`;
  tripCountBadge.textContent = `${totalTrips} Trips`;

  // Render Trip Cards
  renderTripCards(plan.trips);

  // Render Map Canvas
  drawCanvas();
}

function renderTripCards(trips) {
  tripsGrid.innerHTML = "";

  const query = searchQuery.toLowerCase().trim();

  trips.forEach((trip, idx) => {
    const tripWeight = trip.deliveries.reduce((s, d) => s + d.weight, 0);
    const minPrio = Math.min(...trip.deliveries.map(d => d.priority));
    const tripColor = TRIP_COLORS[idx % TRIP_COLORS.length];
    const fillPct = Math.min(100, (tripWeight / 10.0) * 100);

    // Filter check
    const matchesSearch = !query || trip.deliveries.some(d =>
      d.area.toLowerCase().includes(query) ||
      d.id.toString().includes(query) ||
      `p${d.priority}`.includes(query)
    );

    if (!matchesSearch) return;

    const card = document.createElement("div");
    card.className = "trip-card";
    card.style.borderLeft = `4px solid ${tripColor}`;

    let pkgHtml = "";
    trip.deliveries.forEach(d => {
      pkgHtml += `
        <div class="package-item">
          <span class="pkg-area">#${d.id} ${d.area}</span>
          <span><span class="prio-tag prio-${d.priority}">P${d.priority}</span> <span class="pkg-weight">${d.weight.toFixed(1)}kg</span></span>
        </div>
      `;
    });

    card.innerHTML = `
      <div class="trip-card-header">
        <span class="trip-num"><span style="color:${tripColor}">●</span> Trip #${trip.trip_id}</span>
        <span class="prio-tag prio-${minPrio}">Top Urgency P${minPrio}</span>
      </div>
      <div class="weight-meter">
        <div class="weight-labels">
          <span>Capacity: <b>${tripWeight.toFixed(1)} / 10.0 kg</b></span>
          <span>${(10.0 - tripWeight).toFixed(1)} kg left</span>
        </div>
        <div class="progress-track">
          <div class="progress-fill ${tripWeight >= 9.9 ? 'full' : ''}" style="width: ${fillPct}%; background: ${tripColor};"></div>
        </div>
      </div>
      <div class="package-list">
        ${pkgHtml}
      </div>
    `;

    tripsGrid.appendChild(card);
  });
}

// Draw Interactive Canvas
function drawCanvas() {
  ctx.clearRect(0, 0, mapCanvas.width, mapCanvas.height);

  const w = mapCanvas.width;
  const h = mapCanvas.height;

  // Background Grid Lines
  ctx.strokeStyle = "rgba(71, 85, 105, 0.2)";
  ctx.lineWidth = 1;
  for (let x = 0; x < w; x += 40) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, h);
    ctx.stroke();
  }
  for (let y = 0; y < h; y += 40) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(w, y);
    ctx.stroke();
  }

  // Map package delivery ID to Trip index
  const deliveryToTrip = {};
  if (currentPlan && currentPlan.trips) {
    currentPlan.trips.forEach((trip, tIdx) => {
      trip.deliveries.forEach(d => {
        deliveryToTrip[d.id] = tIdx;
      });
    });
  }

  // Draw Trip Connection Lines (Grouping hulls)
  if (currentPlan && currentPlan.trips) {
    currentPlan.trips.forEach((trip, tIdx) => {
      if (trip.deliveries.length > 1) {
        const tripColor = TRIP_COLORS[tIdx % TRIP_COLORS.length];
        ctx.strokeStyle = tripColor;
        ctx.lineWidth = 2;
        ctx.setLineDash([4, 4]);

        const points = trip.deliveries.map((d, i) => {
          const areaCoord = AREA_COORDINATES[d.area] || { x: 0.5, y: 0.5 };
          // Cluster offset around area hub
          const angle = (i / trip.deliveries.length) * Math.PI * 2;
          const radius = 22 + (d.id % 4) * 6;
          return {
            x: areaCoord.x * w + Math.cos(angle) * radius,
            y: areaCoord.y * h + Math.sin(angle) * radius
          };
        });

        ctx.beginPath();
        ctx.moveTo(points[0].x, points[0].y);
        for (let i = 1; i < points.length; i++) {
          ctx.lineTo(points[i].x, points[i].y);
        }
        ctx.closePath();
        ctx.stroke();
        ctx.setLineDash([]);
      }
    });
  }

  // Draw Area Hubs
  Object.keys(AREA_COORDINATES).forEach(areaName => {
    const coord = AREA_COORDINATES[areaName];
    const hx = coord.x * w;
    const hy = coord.y * h;

    // Glowing halo
    const grad = ctx.createRadialGradient(hx, hy, 5, hx, hy, 45);
    grad.addColorStop(0, "rgba(56, 189, 248, 0.18)");
    grad.addColorStop(1, "rgba(56, 189, 248, 0.0)");
    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.arc(hx, hy, 45, 0, Math.PI * 2);
    ctx.fill();

    // Central hub marker
    ctx.fillStyle = "rgba(148, 163, 184, 0.5)";
    ctx.beginPath();
    ctx.arc(hx, hy, 6, 0, Math.PI * 2);
    ctx.fill();

    // Area Label
    ctx.fillStyle = "#cbd5e1";
    ctx.font = "bold 11px sans-serif";
    ctx.textAlign = "center";
    ctx.fillText(areaName, hx, hy - 14);
  });

  // Draw Deliveries
  currentDeliveries.forEach((d, i) => {
    const areaCoord = AREA_COORDINATES[d.area] || { x: 0.5, y: 0.5 };
    const angle = (i / Math.max(1, currentDeliveries.length)) * Math.PI * 2;
    const radius = 22 + (d.id % 4) * 6;
    const px = areaCoord.x * w + Math.cos(angle) * radius;
    const py = areaCoord.y * h + Math.sin(angle) * radius;

    const tIdx = deliveryToTrip[d.id];
    const pkgColor = tIdx !== undefined ? TRIP_COLORS[tIdx % TRIP_COLORS.length] : "#64748b";

    // Circle Node
    ctx.fillStyle = d.weight > 10.0 ? "#ef4444" : pkgColor;
    ctx.beginPath();
    ctx.arc(px, py, 9, 0, Math.PI * 2);
    ctx.fill();

    ctx.strokeStyle = "#0f172a";
    ctx.lineWidth = 2;
    ctx.stroke();

    // Package ID Text
    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 9px sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(d.id.toString(), px, py);
  });
}

// Load Dataset
function loadSelectedDataset() {
  const dsKey = datasetSelect.value;
  currentDeliveries = JSON.parse(JSON.stringify(EMBEDDED_DATASETS[dsKey] || EMBEDDED_DATASETS.sample));
  runSolver();
}

// Event Listeners
datasetSelect.addEventListener("change", loadSelectedDataset);
algoSelect.addEventListener("change", runSolver);
solveBtn.addEventListener("click", runSolver);

searchInput.addEventListener("input", (e) => {
  searchQuery = e.target.value;
  if (currentPlan && currentPlan.trips) {
    renderTripCards(currentPlan.trips);
  }
});

// Initial startup
window.addEventListener("DOMContentLoaded", () => {
  resizeCanvas();
  loadSelectedDataset();
});
