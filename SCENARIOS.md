## Hackathon scenarios (pick one or create your own)

Select one of the scenarios below, if you really want to come up with your own scenarios feel free, but please keep it feasable within the limited time we have.

**⚠ Important Note:** The top scenario is already setup in the agent directory, so will just need modifying to add weather mcp and any other any other modifications.

Each scenario requires:  
- 1) adding/curating content in an MCP server  
- 2) configuring the agent to call that MCP to complete an end-to-end task. Keep scope tight so you can demo in a day.

### 1) City day planner (Attractions + Weather)
- **Objective**: Build a one-day itinerary given preferences and date.
- **MCPs/Data**:
  - Use `src/mcp/attractions-mcp` with curated content you add.
  - Use `src/mcp/weather-mcp` for weather by location/date.
  - Suggested attractions schema:

```json
{
  "id": "att_001",
  "name": "Modern Art Museum",
  "category": "museum",
  "lat": 47.6205,
  "lon": -122.3493,
  "hours": [{"day": "Mon", "open": "10:00", "close": "17:00"}],
  "avg_visit_minutes": 90,
  "price": 20,
  "tags": ["indoor", "art", "family"]
}
```

- **Endpoints**:
  - Attractions MCP: `search_attractions(filters)`, `get_attraction(id)`
  - Weather MCP: `forecast(lat, lon, date)`
- **Agent flow**: Elicit user prefs → fetch forecast → pick open/nearby attractions → sequence by hours/weather → output itinerary with times.
- **Done criteria**: Given preferences and date, agent returns a feasible timeline with 3–5 stops and notes weather.
- **Stretch**: Add simple transit time estimates; budget constraint.

### 2) On-call runbook assistant
- **Objective**: Guide an engineer through an incident using internal runbooks.
- **MCP/Data**: Create `runbooks-mcp` with playbooks and checklists.

```json
{
  "service": "payments",
  "incident_type": "elevated_5xx",
  "severity": "SEV-2",
  "steps": [
    {"id": "s1", "text": "Check dashboard X for 5xx spikes."},
    {"id": "s2", "text": "Tail logs for error Y and capture trace."}
  ],
  "mitigations": ["scale up worker pool", "rollback last deploy"]
}
```

- **Endpoints**: `search_runbooks(query)`, `get_playbook(service, incident_type)`, `start_checklist(playbook_id)`, `update_checklist(step_id, status)`
- **Agent flow**: Summarize incident → select playbook → walk user step-by-step, tracking completion.
- **Done criteria**: Agent selects the correct playbook and tracks completion status through all steps.
- **Stretch**: Add `create_incident_note` endpoint to log actions.

### 3) Internal product catalog and stock checker
- **Objective**: Answer “Can I order X items?” and assemble a cart if in stock.
- **MCP/Data**: Create `inventory-mcp` with a small catalog.

```json
{
  "sku": "HDSK-001",
  "name": "USB-C Docking Station",
  "price": 89.99,
  "stock": 12,
  "location": "Aisle 4",
  "tags": ["office", "peripherals"]
}
```

- **Endpoints**: `search_products(query|filters)`, `get_product(sku)`, `reserve_stock(sku, qty)`
- **Agent flow**: Parse user request → find matching SKUs → confirm quantities → reserve or report shortages.
- **Done criteria**: Agent returns cart with SKUs and reserved quantities or a clear shortage report.
- **Stretch**: Add `suggest_alternatives(sku)` when out of stock.

### 4) Restaurant finder with menu and dietary filters
- **Objective**: Recommend a dinner plan that fits cuisine, budget, and dietary needs.
- **MCP/Data**: Create `restaurants-mcp` with venues and menus.

```json
{
  "id": "rest_101",
  "name": "Green Bowl",
  "cuisine": ["Asian", "Vegetarian"],
  "avg_price": 18,
  "hours": [{"day": "Fri", "open": "11:00", "close": "22:00"}],
  "menu": [
    {"item": "Tofu Stir Fry", "price": 14, "diet": ["vegan", "gluten-free"]},
    {"item": "Udon Soup", "price": 12, "diet": ["vegetarian"]}
  ]
}
```

- **Endpoints**: `search_restaurants(filters)`, `get_menu(restaurant_id)`
- **Agent flow**: Collect constraints → filter restaurants → cite matching menu items → output 2–3 picks with rationale.
- **Done criteria**: Agent produces personalized recommendations that honor all constraints and hours.
- **Stretch**: Integrate Weather MCP to prefer indoor/outdoor seating by forecast.

### 5) Travel packing list generator
- **Objective**: Produce a packing list given destination, dates, activities, and forecast.
- **MCPs/Data**:
  - Weather MCP for forecast.
  - Create `packing-mcp` with gear by activity and weather thresholds.

```json
{
  "activity": "day_hike",
  "base_items": ["daypack", "water bottle", "snacks"],
  "cold_addons_below_c": 10,
  "cold_items": ["insulated jacket", "beanie"],
  "rain_items": ["rain shell", "pack cover"]
}
```

- **Endpoints**: `items_for(activity, temp_c, precipitation)`, `extras_for(duration_hours)`
- **Agent flow**: Ask destination/dates/activities → fetch forecast → compose list with reasoning and counts.
- **Done criteria**: Agent outputs a categorized list tailored to activities and expected weather.
- **Stretch**: Add `pack_weight_estimate(list)` and a max-weight constraint.

---

Tips
- Keep data small (10–50 items). Quality beats quantity.
- Design 2–4 clear MCP tools; name them action-first (e.g., `search_*`, `get_*`).
- Ensure each tool’s inputs/outputs are concise JSON.
- Make the agent’s system prompt state the goal, tools available, and success criteria.

