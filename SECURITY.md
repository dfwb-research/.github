# Security policy

## Reporting a vulnerability

Please report vulnerabilities **privately**:

- use GitHub's **"Report a vulnerability"** button on the repository's *Security* tab; or
- email Luke Collins at luke.collins@research.deakin.edu.au.

Do not open a public issue. Include the affected package and version, a description, and steps
to reproduce. You will get an acknowledgement, and a fix or mitigation will be coordinated with you
before anything is disclosed.

## Scope

Of particular interest:

- loading model weights and checkpoints (the projects prefer safetensors and load PyTorch
  checkpoints with `weights_only=True`);
- parsing protocol packs, configs and score files (YAML is loaded with `safe_load`; configs never
  execute code);
- downloading and verifying third-party weights (sha256 checks).

`py:` detector sources run the user's own code by design; that is documented and not a
vulnerability.

## Supported versions

Security fixes are made for the latest release of each package.
