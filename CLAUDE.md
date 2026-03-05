# CLAUDE.md

## Project Overview

OpenClaw on AWS Lightsail — a CDK (Python) project that deploys an [OpenClaw](https://aws.amazon.com/blogs/aws/introducing-openclaw-on-amazon-lightsail-to-run-your-autonomous-private-ai-agents/) autonomous AI agent on Amazon Lightsail with a static IP, auto snapshots, and Amazon Bedrock as the default model provider.

## Tech Stack

- **Language**: Python 3.14+
- **IaC**: AWS CDK v2 (Python bindings via `aws-cdk-lib`)
- **Package manager**: [uv](https://docs.astral.sh/uv/) for Python deps, npm/npx for CDK CLI
- **Linting/Formatting**: Ruff (Python), markdownlint (Markdown)
- **Testing**: pytest with CDK assertion helpers (`aws_cdk.assertions`)

## Repository Structure

```text
.
├── app.py                          # CDK app entry point (synthesizes OpenClawStack)
├── cdk/
│   ├── constants.py                # Shared config (REGION)
│   ├── openclaw_stack.py           # Main stack: composes AiAgent construct, adds CfnOutputs
│   └── constructs/
│       └── ai_agent.py             # Domain construct: Lightsail instance + static IP
├── tests/
│   └── unit/
│       └── test_openclaw_stack.py  # Synthesis-time assertion tests
├── Makefile                        # All dev commands (install, test, lint, deploy, etc.)
├── pyproject.toml                  # Python project config (deps, ruff, pytest)
├── package.json                    # CDK CLI + markdownlint version pins
├── cdk.json                        # CDK app command: "uv run python app.py"
└── .markdownlint.yaml              # Markdown lint rules
```

## Common Commands

All commands are in the `Makefile`:

```bash
make install       # Install all deps (uv sync --dev && npm install)
make test          # Run pytest: uv run pytest tests/ -v
make lint          # Ruff check + format check + markdownlint
make format        # Auto-fix: ruff check --fix + ruff format
make synth         # CDK synth (npx cdk synth)
make diff          # CDK diff
make deploy        # CDK deploy (--require-approval broadening)
make destroy       # CDK destroy
make update-deps   # Upgrade all deps (uv lock --upgrade, npm update)
make pr            # Pre-PR gate: lint + test + synth
```

**Before opening a PR, always run `make pr`** (runs lint, test, and synth).

## Code Conventions

### Python Style (enforced by Ruff)

- **Line length**: 150 characters max
- **Indent**: 4 spaces
- **Quote style**: single quotes
- **Import sorting**: isort with `aws_cdk` and `constructs` as known third-party
- **Target version**: Python 3.14
- **Lint rules enabled**: pycodestyle (E/W), pyflakes (F), isort (I), flake8-comprehensions (C), flake8-bugbear (B), pylint (PL)

### CDK Patterns

- **Domain-Driven Design (DDD) constructs**: organize constructs by business domain (e.g., `AiAgent`), not by AWS resource type. See `cdk/constructs/`.
- **Props as dataclasses**: use `@dataclass` for construct props (see `AiAgentProps`).
- **Single stack**: one repo, one CDK app, one stack (`OpenClawStack`).
- **Constants**: shared config values live in `cdk/constants.py`.
- **Stack-level names**: instance and static IP names are defined at the stack level in `openclaw_stack.py`, not inside constructs.

### Testing

- Tests use CDK `Template.from_stack()` and assertion methods like `has_resource_properties` and `resource_count_is`.
- Test classes are grouped by domain: `TestAiAgent` (instance properties), `TestAiAgentNetworking` (static IP).
- Helper `_create_template()` creates a fresh stack per test.
- No mocking — tests validate the synthesized CloudFormation template directly.

### Git & PR Workflow

- Default branch: `main`
- PR labeler configured in `.github/workflows/pr-labeler.yml`
- Release changelog categories defined in `.github/release.yml` (breaking-change, enhancement, bug, documentation, chore, dependencies)
- Lock files (`uv.lock`, `package-lock.json`) are gitignored

## Key Files to Know

| File | Purpose |
|------|---------|
| `cdk/constructs/ai_agent.py` | Core construct — Lightsail instance + static IP creation |
| `cdk/openclaw_stack.py` | Stack composition and CfnOutputs |
| `cdk/constants.py` | Region config (currently `us-east-1`) |
| `tests/unit/test_openclaw_stack.py` | All unit tests |
| `pyproject.toml` | Python deps, ruff config, pytest config |

## Important Notes

- The CDK app is invoked via `uv run python app.py` (configured in `cdk.json`).
- The OpenClaw Lightsail blueprint (`openclaw_ls_1_0`) must exist in the target region before deploying.
- Firewall and networking rules are managed by the OpenClaw blueprint itself — do not override them in CDK.
- Auto snapshots are enabled by default at 04:00 UTC.
- The static IP depends on the Lightsail instance (`add_dependency`).
