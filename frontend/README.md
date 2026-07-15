# Adversarial Sandbox — Frontend

React + TypeScript + Vite + Tailwind SPA for the Adversarial Sandbox.

## Prereqs
The backend must be running (see `../backend/README.md`):
```bash
cd ../backend && source .venv/bin/activate && uvicorn adversarial_sandbox.api:app --port 8000
```

## Setup & run
```bash
npm install
npm run dev        # http://localhost:5173
```
The API base URL defaults to `http://localhost:8000`; override with `VITE_API_BASE`.

## Test
```bash
npm test
```

## How it stays generic
`ControlPanel`/`KnobControl` render whatever knobs the backend's `describe()` returns,
so a new backend attack appears here with no frontend changes.
