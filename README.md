# IncidentBridge

IncidentBridge is a reusable Python toolkit for converting heterogeneous incident signals into a canonical, provenance-aware event model with validation and safety metadata.

## Status

Phase 0 repository baseline. The implementation will be created during the Amazon App Dev Challenge 2026 window and tagged only after clean-install and test verification.

## Design goals

- deterministic normalization
- explicit source and simulation provenance
- strict schema validation
- privacy-aware redaction hooks
- adapter isolation
- useful independently of Aenea

No capability is considered released until it is present in source, covered by tests, and documented with working install/run commands.

IncidentBridge remains deliberately small. Aenea may consume it at runtime, but the package will not depend on Aenea, AWS or a specific device vendor. Open Source mini submission work proceeds only while it does not delay the Alexa+ primary project.

## Project records

- [Project timeline](docs/project-timeline.md)
- [Build evidence](docs/build-evidence.md)
- [Contributing](CONTRIBUTING.md)
- [Security policy](SECURITY.md)

## License

Apache License 2.0. See `LICENSE`.
