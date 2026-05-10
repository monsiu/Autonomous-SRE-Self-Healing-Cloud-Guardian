# Autonomous SRE - Frontend Dashboard

Real-time monitoring and visualization dashboard for the Autonomous SRE system.

## Features

### 🍔 Hamburger Sidebar Navigation
- Collapsible sidebar with panel selection
- Mobile-responsive design
- Quick access to all dashboard panels:
  - Live Log Stream
  - System Health Score
  - Agent Thinking Display
  - Remediation Action Log
  - Incident History Timeline
- View individual panels or all panels at once
- Smooth transitions and animations

### 🔴 Live Log Stream
- Real-time log feed with WebSocket connection
- Color-coded severity levels (INFO, WARNING, ERROR, CRITICAL)
- Anomaly highlighting with visual indicators
- Filterable by service/source and severity level
- Auto-scroll to latest logs

### 🧠 Agent Thinking Display
- Real-time agent reasoning and decision-making process
- LLM thought process visualization
- Confidence scores with progress bars
- Similar incidents found display
- Diagnosis and remediation plan details
- Execution time tracking

### ⚡ Remediation Action Log
- Timeline view of all remediation actions
- Execution status (success/failure/pending)
- Execution time for each action
- Detailed result information
- Visual timeline with status indicators

### 📊 Incident History Timeline
- Chronological view of all incidents
- Resolution times and success rates
- Statistics dashboard (total, resolved, avg resolution time, success rate)
- Severity-based color coding
- Incident details and timestamps

### 💚 System Health Score
- Overall system health metric (0-100)
- Trend visualization (improving/stable/degrading)
- Real-time metrics: CPU, Memory, Error Rate, Response Time
- Predictive indicators for next hour
- Historical health trend chart
- Confidence scores for predictions

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **Recharts** - Data visualization
- **Lucide React** - Icons
- **date-fns** - Date formatting
- **WebSocket** - Real-time communication

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend server running on `http://localhost:8000`

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

The dashboard will be available at `http://localhost:3000`

### Build for Production

```bash
npm run build
npm run preview
```

## WebSocket Connections

The dashboard connects to two WebSocket endpoints (note the trailing slashes):

- **Logs Stream**: `ws://localhost:8000/api/v1/logs/`
- **Agent State**: `ws://localhost:8000/api/v1/agents/`

**Important**: The trailing slash is required for proper connection.

Connection features:
- Automatic reconnection with exponential backoff
- Maximum 10 reconnection attempts
- Connection status displayed in header
- Detailed error logging in browser console

### Troubleshooting WebSocket Issues

See `WEBSOCKET_FIX.md` in the root directory for detailed troubleshooting guide.

**Quick checks:**
1. Ensure backend is running: `uvicorn main:app --reload`
2. Check browser console for connection logs
3. Verify URLs have trailing slashes
4. Check Network tab for "101 Switching Protocols" status

## API Integration

### Trigger Incident

```bash
POST http://localhost:8000/api/v1/incidents/trigger
Content-Type: application/json

{
  "incident_type": "ddos" | "cpu_surge" | "db_bottleneck"
}
```

### Restore Normal State

```bash
POST http://localhost:8000/api/v1/incidents/remediate
```

## Dashboard Layout

### Desktop View (All Panels)
```
┌─────────────────────────────────────────────────────────┐
│                        Header                           │
│  (☰ Menu, Connection Status, Incident Triggers)        │
├──────┬──────────────────┬──────────────┬───────────────┤
│      │                  │              │               │
│ Side │  Live Log Stream │   System     │ Remediation   │
│ bar  │                  │   Health     │ Log           │
│      │                  │   Score      │               │
│      ├──────────────────┤              ├───────────────┤
│      │                  │              │               │
│      │  Agent Thinking  │              │ Incident      │
│      │                  │              │ Timeline      │
│      │                  │              │               │
└──────┴──────────────────┴──────────────┴───────────────┘
```

### Mobile View (Single Panel)
```
┌─────────────────────────┐
│   Header (☰ Menu)       │
├─────────────────────────┤
│                         │
│   Selected Panel        │
│   (Full Screen)         │
│                         │
│                         │
└─────────────────────────┘
```

### Sidebar Navigation
- Click hamburger menu (☰) to open sidebar
- Select individual panel to view full-screen
- Select "All Panels" to view dashboard layout
- Sidebar auto-closes on mobile after selection

## Color Coding

### Log Severity
- **INFO**: Blue
- **WARNING**: Yellow
- **ERROR**: Orange
- **CRITICAL**: Red
- **ANOMALY**: Red with pulse animation

### Agent Status
- **Idle**: Gray
- **Running**: Blue with spinner
- **Success**: Green
- **Error**: Red

### Incident Severity
- **Low**: Blue
- **Medium**: Yellow
- **High**: Orange
- **Critical**: Red

### Health Score
- **80-100**: Green (Healthy)
- **60-79**: Yellow (Warning)
- **40-59**: Orange (Degraded)
- **0-39**: Red (Critical)

## Development

### Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Header.tsx
│   │   ├── LiveLogStream.tsx
│   │   ├── AgentThinking.tsx
│   │   ├── RemediationLog.tsx
│   │   ├── IncidentTimeline.tsx
│   │   └── SystemHealthScore.tsx
│   ├── hooks/
│   │   └── useWebSocket.ts
│   ├── types/
│   │   └── index.ts
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

### Adding New Features

1. Define types in `src/types/index.ts`
2. Create component in `src/components/`
3. Add to `App.tsx` layout
4. Update WebSocket handlers if needed

## Troubleshooting

### WebSocket Connection Issues

- Ensure backend is running on port 8000
- Check browser console for connection errors
- Verify CORS settings in backend

### Build Errors

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Type Errors

```bash
# Regenerate TypeScript types
npm run build
```

## License

MIT

---

Built for AMD Developer Hackathon 2025
