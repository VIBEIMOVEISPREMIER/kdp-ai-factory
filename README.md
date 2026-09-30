# KDP AI Factory

A local-first, open-source AI publishing platform designed to help users create, edit, illustrate, format, validate, and prepare books for Amazon KDP.

## Vision

KDP AI Factory is not just a coloring-book generator. It is an extensible editorial automation system for fiction, children's books, educational books, study guides, workbooks, journals, notebooks, activity books, cookbooks, poetry, and custom publishing projects.

## Core principles

- Local-first processing whenever possible
- No mandatory paid AI APIs
- No artificial image-credit limits
- Multiple local AI models
- Multi-language architecture
- Beginner-friendly visual dashboard
- PowerShell/CLI for advanced users
- Resumable projects and task queues
- KDP-oriented validation and export
- Clear documentation from installation to publication
- Modular architecture so AI providers and models can be replaced

## Project status

🚧 Early development — architecture and foundation.

## Planned stack

- Web dashboard: React + TypeScript
- Backend/core: Python
- Local text inference: Ollama-compatible models
- Local image workflows: ComfyUI-compatible workflows
- Documents: PDF/EPUB generation and validation
- Project storage: SQLite initially, with an upgrade path
- CLI: cross-platform command interface
- CI/CD: GitHub Actions

## Important

KDP AI Factory does not assume a public Amazon KDP publishing API exists. Publication automation will be isolated behind a connector so the rest of the system remains independent of Amazon's interface.

## License

License will be defined before the first public release.
