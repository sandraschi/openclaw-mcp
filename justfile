# openclaw-mcp justfile

default:
    just check

check:
    ruff check src tests
    ruff format --check src tests
    mypy src
    pytest tests -v

lint:
    ruff check src tests --fix
    ruff format src tests

test:
    pytest tests -v

test-cov:
    pytest tests -v --cov=openclaw_mcp --cov-report=term-missing

typecheck:
    mypy src

# MCPB package: copy src into mcpb then pack (current standard). Output: dist/openclaw-mcp-<version>.mcpb
mcpb:
    pwsh -NoProfile -File scripts/mcpb-build.ps1
