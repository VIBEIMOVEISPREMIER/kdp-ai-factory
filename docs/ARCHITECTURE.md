# Architecture

## Layers

### 1. Dashboard
Human-friendly visual interface for creating and monitoring projects.

### 2. Application API
Coordinates projects, jobs, agents, models, documents, validation, and exports.

### 3. Core engine
Contains business logic independent of any specific UI or AI provider.

### 4. AI adapters
Adapters for local/open models. The first targets are Ollama-compatible text models and ComfyUI image workflows.

### 5. Editorial engines
Writing, editing, document assembly, layout, cover, metadata, validation, and export.

### 6. Connectors
External integrations are isolated here. KDP publication must remain replaceable because Amazon's public API availability and policies can change.

## Non-negotiable design goals

- A failed task must be retryable.
- A project must be resumable after interruption.
- Generated assets must be traceable to a project/task.
- UI and CLI must call the same core services.
- No provider-specific code should leak into the core.
- Local execution must remain the default path.
