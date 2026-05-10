# ML/AI Components - Phase 2

This module implements the core ML/AI pipeline for the Autonomous SRE Guardian.

## Architecture

### 1. Monitor Agent (`agent_manager.py`)
- Ingests logs continuously
- Stores logs in ChromaDB with embeddings
- Detects anomalies based on thresholds (ERROR/CRITICAL levels)
- Triggers diagnosis pipeline

### 2. Diagnosis Agent (`llm_engine.py`)
- Queries ChromaDB for similar historical incidents
- Cross-references SRE runbooks
- Uses LLM reasoning (currently rule-based fallback)
- Outputs structured diagnosis JSON

### 3. Remediation Agent (`remediation.py`)
- Executes appropriate remediation scripts
- Generates PDF post-mortem reports
- Tracks remediation success

## Components

### `vector_store.py`
- ChromaDB integration for log and incident storage
- Semantic similarity search
- Pre-seeded with 5 sample incidents

### `llm_engine.py`
- LLM integration (placeholder for Llama 3.1 8B)
- Rule-based diagnosis fallback
- Incident classification and action recommendation

### `remediation.py`
- Remediation script execution
- PDF post-mortem generation using ReportLab
- Action tracking and logging

## Setup

1. Install dependencies:
```bash
pip install -r ../requirements.txt
```

2. Initialize ML components:
```bash
python ml/setup.py
```

## Usage

The agent pipeline runs automatically when logs are ingested:

```
Log Entry → Monitor Agent → Diagnosis Agent → Remediation Agent → Post-Mortem
```

## Incident Types Supported

1. **DDoS Attack** - Rate limit breaches, high traffic
2. **CPU Surge** - Resource exhaustion, high CPU usage
3. **DB Bottleneck** - Query timeouts, connection pool issues

## Future Enhancements (Phase 3)

- [ ] Load actual Llama 3.1 8B model with ROCm
- [ ] Fine-tune on SRE runbooks and historical logs
- [ ] Implement advanced anomaly detection (sliding window)
- [ ] Add more remediation scripts
- [ ] Integrate with real infrastructure APIs
