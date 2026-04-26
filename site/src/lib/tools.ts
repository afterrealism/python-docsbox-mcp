export type Tool = { name: string; summary: string; detail?: string };

export const tools: Tool[] = [
  {
    name: 'list_sections',
    summary: 'Browse indexed Python stdlib and packaging documentation.',
    detail: 'Returns paths into the bundled corpus snapshot. Filterable by prefix.'
  },
  {
    name: 'get_documentation',
    summary: 'Markdown for a single section path returned by list_sections.',
    detail: 'Read-only SQLite + zstd blobs, served from the wheel.'
  },
  {
    name: 'ruff_check',
    summary: 'Lint a Python snippet and return JSON diagnostics from ruff.'
  },
  {
    name: 'ruff_fix',
    summary: 'Auto-apply ruff suggestions to a snippet.'
  },
  {
    name: 'ruff_format',
    summary: 'Canonical formatting via `ruff format`.'
  },
  {
    name: 'pyright_check',
    summary: 'Type-check a snippet with pyright in basic mode.'
  },
  {
    name: 'pep_lookup',
    summary: 'Look up a PEP by number and return its abstract + status.'
  },
  {
    name: 'pip_info',
    summary: 'PyPI metadata, version history, dependencies for a package.'
  },
  {
    name: 'ast_dump',
    summary: 'Pretty-print the AST of a Python snippet.'
  },
  {
    name: 'run_locally',
    summary: 'Emit a plan of shell commands the calling agent should run.',
    detail: 'The server itself never executes user code; the trust boundary stays at the agent host.'
  }
];
