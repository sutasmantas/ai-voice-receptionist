const initial = JSON.parse(document.getElementById("initial-run").textContent);
let currentRun = initial;
let browserRuns;

function isBrowserWorkspace() {
  return location.hostname.endsWith("github.io") || new URLSearchParams(location.search).has("static");
}

async function loadBrowserRuns() {
  if (!browserRuns) {
    const response = await fetch("./runs.json");
    browserRuns = (await response.json()).runs;
  }
  return browserRuns;
}

const lanes = {
  caller: document.querySelector('[data-lane="caller"]'),
  receptionist: document.querySelector('[data-lane="receptionist"]'),
  tool: document.querySelector('[data-lane="tool"]'),
  system: document.querySelector('[data-lane="system"]'),
};

function selectEvent(event) {
  document.getElementById("event-kind").textContent = event.kind.replaceAll("_", " ");
  document.getElementById("event-text").textContent = event.text || "Structured workflow event";
  document.getElementById("event-data").textContent = JSON.stringify(event.data, null, 2);
}

function markerWidthPercent(lane) {
  if (window.innerWidth <= 560) return 31;
  const width = Math.min(210, Math.max(74, window.innerWidth * 0.16));
  return (width / lane.clientWidth) * 100;
}

function collisionFreePositions(events, lane, maxMs) {
  const span = window.innerWidth <= 560 ? 68 : 84;
  // Mobile interruption cards are skewed, so their visual bounds need extra
  // separation beyond the untransformed CSS width.
  const gap = window.innerWidth <= 560 ? 5.5 : 1.1;
  const availableWidth = Math.max(12, (100 - gap * Math.max(0, events.length - 1)) / Math.max(1, events.length));
  const width = Math.min(markerWidthPercent(lane), availableWidth);
  const step = width + gap;
  const maxLeft = 100 - width;
  const positions = events.map((event) => Math.min(span, (event.at_ms / maxMs) * span));

  for (let index = 1; index < positions.length; index += 1) {
    positions[index] = Math.max(positions[index], positions[index - 1] + step);
  }
  if (positions.length && positions.at(-1) > maxLeft) {
    positions[positions.length - 1] = maxLeft;
    for (let index = positions.length - 2; index >= 0; index -= 1) {
      positions[index] = Math.min(positions[index], positions[index + 1] - step);
    }
  }
  return { positions, width };
}

function render(run) {
  currentRun = run;
  Object.values(lanes).forEach((lane) => lane.replaceChildren());
  const maxMs = Math.max(...run.events.map((event) => event.at_ms), 1000);

  Object.entries(lanes).forEach(([laneName, lane]) => {
    const laneEvents = run.events.filter((event) => event.lane === laneName);
    const layout = collisionFreePositions(laneEvents, lane, maxMs);
    laneEvents.forEach((event, index) => {
      const marker = document.createElement("button");
      marker.className = `event-marker ${event.kind.includes("interrupt") ? "interrupted" : ""}`;
      marker.style.left = `${layout.positions[index]}%`;
      marker.style.width = `${layout.width}%`;
      marker.innerHTML = `<small>${event.at_ms} ms · ${event.kind}</small>${event.text || event.kind.replaceAll("_", " ")}`;
      marker.addEventListener("click", () => selectEvent(event));
      lane.appendChild(marker);
    });
  });

  document.getElementById("scenario-title").textContent = run.title;
  document.getElementById("run-outcome").textContent = run.outcome.toUpperCase();
  document.getElementById("run-id").textContent = run.id;
  document.getElementById("ticket-state").textContent = run.outcome.toUpperCase();
  document.getElementById("ticket-caller").textContent = run.summary.caller.name || "Not captured";
  document.getElementById("ticket-booking").textContent = run.booking ? "30 min confirmed" : "None";
  document.getElementById("ticket-handoff").textContent = run.handoff_state;
  document.getElementById("ticket-accuracy").textContent = `${Math.round(run.metrics.entity_accuracy * 100)}%`;
  document.getElementById("ticket-latency").textContent = `${run.metrics.max_response_latency_ms} ms`;
  document.getElementById("replay-button").hidden = run.handoff_state !== "dead_letter";
  selectEvent(run.events[0]);
}

async function runSelected() {
  const id = document.getElementById("scenario-select").value;
  if (isBrowserWorkspace()) {
    const runs = await loadBrowserRuns();
    render(structuredClone(runs[id]));
    return;
  }
  const response = await fetch(`/api/runs/${id}`, { method: "POST" });
  if (!response.ok) throw new Error(await response.text());
  render(await response.json());
}

async function replayHandoff() {
  if (isBrowserWorkspace()) {
    const replayed = structuredClone(currentRun);
    replayed.handoff_state = "delivered";
    replayed.events.push({ kind: "handoff_replayed", at_ms: Math.max(...replayed.events.map((event) => event.at_ms)) + 120, lane: "tool", text: "Dead letter delivered on replay", data: { state: "delivered" } });
    render(replayed);
    return;
  }
  const response = await fetch(`/api/runs/${currentRun.id}/replay-handoff`, { method: "POST" });
  if (!response.ok) throw new Error(await response.text());
  render(await response.json());
}

document.getElementById("run-button").addEventListener("click", runSelected);
document.getElementById("replay-button").addEventListener("click", replayHandoff);
window.addEventListener("resize", () => render(currentRun));
if (initial) {
  render(initial);
} else {
  loadBrowserRuns().then((runs) => render(structuredClone(runs["successful-booking"])));
}
