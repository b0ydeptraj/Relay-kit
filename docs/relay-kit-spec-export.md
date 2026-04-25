# Relay-kit Spec Export and Import

`relay-kit spec export` converts Relay-kit planning and QA contracts into a machine-readable JSON artifact.

Default command:

```bash
relay-kit spec export /path/to/project
```

Custom output:

```bash
relay-kit spec export /path/to/project --output-file /path/to/relay-spec.json
```

The export includes:

- schema version
- project path
- source artifact paths and SHA-256 hashes
- requirements
- acceptance criteria
- verification steps
- verification evidence
- likely files
- risks
- missing fields
- `verification_ready`

`verification_ready` is `false` when acceptance criteria, verification steps, or verification evidence are missing.

Import preview:

```bash
relay-kit spec import /path/to/project --spec-file /path/to/relay-spec.json
```

Apply imported fields:

```bash
relay-kit spec import /path/to/project --spec-file /path/to/relay-spec.json --apply
```

The importer maps requirements, acceptance criteria, verification steps, verification evidence, files, and risks into Relay-kit contract sections. It preserves concrete existing section content by default; use `--force` only when replacing those sections is intentional.
