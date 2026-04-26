<script lang="ts">
  import { tools } from '$lib/tools';

  const SITE = {
    name: 'Python DocsBox MCP',
    short: 'Python DocsBox',
    url: 'https://python-mcp.afterrealism.com',
    title: 'Python DocsBox MCP, LLM coding tools for Python',
    description:
      'A Model Context Protocol server giving LLM coding agents typed access to Python documentation, ruff, pyright, PEP lookup, PyPI metadata and AST inspection over a single streamable-HTTP endpoint.',
    descriptionShort:
      'MCP streamable-HTTP server with Python docs, ruff, pyright, PEP lookup, PyPI metadata and AST tools for LLM coding agents.',
    locale: 'en_US',
    repo: 'https://github.com/afterrealism/python-docsbox-mcp',
    license: 'MIT',
    org: 'afterrealism',
    keywords:
      'MCP, Model Context Protocol, Python, ruff, pyright, PEP, PyPI, AST, LLM, coding agent, OpenCode, Claude Code, Cursor, Continue, AI tools, developer tools'
  };

  const sections = [
    { id: 'overview', label: 'Overview' },
    { id: 'endpoint', label: 'Endpoint' },
    { id: 'quickstart', label: 'Quick start' },
    { id: 'tools', label: 'Tools' },
    { id: 'documentation', label: 'Documentation' },
    { id: 'trust', label: 'Trust model' },
    { id: 'faq', label: 'FAQ' },
    { id: 'source', label: 'Source' }
  ];

  const opencodeConfig = `{
  "mcp": {
    "python-docsbox": {
      "type": "remote",
      "url": "https://python-mcp.afterrealism.com/mcp",
      "enabled": true
    }
  }
}`;

  const claudeConfig = `{
  "mcpServers": {
    "python-docsbox": {
      "transport": {
        "type": "http",
        "url": "https://python-mcp.afterrealism.com/mcp"
      }
    }
  }
}`;

  const faqs = [
    {
      q: 'What is Python DocsBox MCP?',
      a: 'A Model Context Protocol (MCP) server that gives LLM coding agents typed access to Python documentation, ruff lint and format, pyright type-check, PEP lookup, PyPI metadata and AST inspection over a single streamable-HTTP endpoint at https://python-mcp.afterrealism.com/mcp.'
    },
    {
      q: 'How do I connect my agent to it?',
      a: 'Add the URL https://python-mcp.afterrealism.com/mcp to your MCP-aware client (OpenCode, Claude Code, Cursor, Continue) under its mcpServers / mcp config block. The transport is MCP streamable HTTP, specification 2025-06-18.'
    },
    {
      q: 'Does the server execute my code?',
      a: 'No. Ruff, pyright, and ast_dump run in tempdirs under bounded timeouts and bounded output limits, but never execute the snippet. The run_locally tool returns a plan of shell commands for the calling agent to dispatch on the user\u2019s host, the server itself never runs user Python.'
    },
    {
      q: 'Is it free?',
      a: 'Yes. The hosted instance at https://python-mcp.afterrealism.com/ is free to use, and the source code is MIT-licensed at https://github.com/afterrealism/python-docsbox-mcp.'
    },
    {
      q: 'Can I self-host it?',
      a: 'Yes. The repository ships a Dockerfile, a hatch-built wheel and a Cloudflare Containers deploy config. Run it on any container host, or pip install the wheel and run python -m python_docsbox_mcp.'
    },
    {
      q: 'What tools does the server expose?',
      a: 'list_sections, get_documentation, ruff_check, ruff_fix, ruff_format, pyright_check, pep_lookup, pip_info, ast_dump, run_locally. The full descriptions are at https://python-mcp.afterrealism.com/#tools.'
    },
    {
      q: 'Are AI crawlers allowed to index this site?',
      a: 'Yes. The robots.txt at https://python-mcp.afterrealism.com/robots.txt explicitly allows GPTBot, ChatGPT-User, OAI-SearchBot, ClaudeBot, anthropic-ai, Claude-Web, Claude-User, Claude-SearchBot, PerplexityBot, Perplexity-User, Google-Extended, GoogleOther, Applebot-Extended, CCBot, Meta-ExternalAgent, Meta-ExternalFetcher, Bytespider, DuckAssistBot, MistralAI-User, Cohere-AI, AI2Bot, Diffbot, YouBot, and others. Only the JSON-RPC transport at /mcp is disallowed for crawlers.'
    }
  ];

  const jsonLd = {
    '@context': 'https://schema.org',
    '@graph': [
      {
        '@type': 'WebSite',
        '@id': SITE.url + '/#website',
        name: SITE.name,
        alternateName: SITE.short,
        url: SITE.url + '/',
        description: SITE.descriptionShort,
        inLanguage: 'en',
        publisher: { '@id': 'https://afterrealism.com/#org' }
      },
      {
        '@type': 'SoftwareApplication',
        '@id': SITE.url + '/#app',
        name: SITE.name,
        alternateName: SITE.short,
        operatingSystem: 'Any (HTTP client)',
        applicationCategory: 'DeveloperApplication',
        applicationSubCategory: 'Model Context Protocol Server',
        url: SITE.url + '/',
        downloadUrl: SITE.repo,
        installUrl: SITE.url + '/#quickstart',
        license: 'https://opensource.org/licenses/MIT',
        codeRepository: SITE.repo,
        programmingLanguage: 'Python',
        offers: { '@type': 'Offer', price: '0', priceCurrency: 'USD' },
        featureList: tools.map((t) => t.name + ': ' + t.summary),
        publisher: { '@id': 'https://afterrealism.com/#org' }
      },
      {
        '@type': 'Organization',
        '@id': 'https://afterrealism.com/#org',
        name: SITE.org,
        url: 'https://afterrealism.com',
        sameAs: ['https://github.com/afterrealism']
      },
      {
        '@type': 'FAQPage',
        '@id': SITE.url + '/#faq',
        mainEntity: faqs.map((f) => ({
          '@type': 'Question',
          name: f.q,
          acceptedAnswer: { '@type': 'Answer', text: f.a }
        }))
      },
      {
        '@type': 'BreadcrumbList',
        '@id': SITE.url + '/#breadcrumb',
        itemListElement: [
          { '@type': 'ListItem', position: 1, name: 'afterrealism', item: 'https://afterrealism.com/' },
          { '@type': 'ListItem', position: 2, name: SITE.short, item: SITE.url + '/' }
        ]
      }
    ]
  };

  const jsonLdStr = JSON.stringify(jsonLd)
    .replace(/</g, '\\u003c')
    .replace(/>/g, '\\u003e')
    .replace(/&/g, '\\u0026');

  const ldOpen = '<' + 'script type="application/ld+json">';
  const ldClose = '</' + 'script>';
</script>

<svelte:head>
  <title>{SITE.title}</title>
  <meta name="description" content={SITE.descriptionShort} />
  <meta name="keywords" content={SITE.keywords} />
  <meta name="author" content={SITE.org} />
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1" />
  <meta name="googlebot" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1" />
  <meta name="theme-color" content="#2563eb" media="(prefers-color-scheme: light)" />
  <meta name="theme-color" content="#0b1020" media="(prefers-color-scheme: dark)" />
  <meta name="application-name" content={SITE.name} />
  <meta name="apple-mobile-web-app-title" content={SITE.short} />
  <meta name="generator" content="SvelteKit + UnoCSS (prerendered, no JS)" />
  <link rel="canonical" href={SITE.url + '/'} />
  <link rel="alternate" type="text/markdown" href={SITE.url + '/llms.txt'} title="LLM index (llms.txt)" />
  <link rel="alternate" type="text/markdown" href={SITE.url + '/llms-full.txt'} title="LLM full reference (llms-full.txt)" />
  <link rel="sitemap" type="application/xml" href={SITE.url + '/sitemap.xml'} />

  <meta property="og:type" content="website" />
  <meta property="og:site_name" content={SITE.name} />
  <meta property="og:locale" content={SITE.locale} />
  <meta property="og:url" content={SITE.url + '/'} />
  <meta property="og:title" content={SITE.title} />
  <meta property="og:description" content={SITE.descriptionShort} />

  <meta name="twitter:card" content="summary" />
  <meta name="twitter:title" content={SITE.title} />
  <meta name="twitter:description" content={SITE.descriptionShort} />

  {@html ldOpen + jsonLdStr + ldClose}
</svelte:head>

<div class="max-w-7xl mx-auto px-6 py-10 grid gap-10" style="grid-template-columns: minmax(0, 1fr); --rail: 220px;">
  <div class="grid gap-10 lg:grid-cols-[var(--rail)_minmax(0,1fr)]">
    <aside class="hidden lg:block">
      <nav class="sticky top-20 flex flex-col gap-0.5 pr-4" style="border-right: 1px solid var(--border)" aria-label="On this page">
        <p class="text-xs uppercase tracking-wider px-3 mb-2" style="color: var(--muted)">On this page</p>
        {#each sections as s}
          <a class="toc-link" href="#{s.id}">{s.label}</a>
        {/each}
      </nav>
    </aside>

    <article class="prose max-w-3xl">
      <header class="mb-10 pb-6" style="border-bottom: 1px solid var(--border)">
        <p class="text-sm font-medium mb-2" style="color: var(--accent)">Server</p>
        <h1 class="text-4xl font-semibold tracking-tight mb-3" style="letter-spacing: -0.02em">Python DocsBox</h1>
        <p class="text-lg" style="color: var(--muted)">A Model Context Protocol server giving LLM coding agents typed access to Python documentation, ruff, pyright, PEP lookup, PyPI metadata and AST inspection, over a single streamable-HTTP endpoint.</p>
      </header>

      <section id="overview" aria-labelledby="overview-h">
        <h2 id="overview-h">Overview</h2>
        <p>Python DocsBox is a self-contained MCP server. It bundles a snapshot of the Python standard library and packaging-ecosystem documentation, and exposes a small set of tools that let a coding agent look things up, lint and format code with <a href="https://docs.astral.sh/ruff/">ruff</a>, type-check with <a href="https://microsoft.github.io/pyright/">pyright</a>, look up PEPs and PyPI metadata, and inspect ASTs, all without bouncing through arbitrary internet calls.</p>
        <p>It speaks <a href="https://modelcontextprotocol.io/specification/2025-06-18/basic/transports">MCP streamable HTTP</a> (spec 2025-06-18), so any MCP-aware client, OpenCode, Claude Code, Cursor, Continue, can connect with a one-line config.</p>
      </section>

      <section id="endpoint" aria-labelledby="endpoint-h">
        <h2 id="endpoint-h">Endpoint</h2>
        <pre><code>POST https://python-mcp.afterrealism.com/mcp</code></pre>
        <p class="muted">Health probe at <code>/health</code>. Crawler policy at <code>/robots.txt</code>. LLM index at <code>/llms.txt</code> and <code>/llms-full.txt</code>. This page is served at <code>/</code>.</p>
      </section>

      <section id="quickstart" aria-labelledby="quickstart-h">
        <h2 id="quickstart-h">Quick start</h2>
        <h3>OpenCode</h3>
        <p>Add the server to your <code>opencode.json</code> under <code>mcp</code>:</p>
        <pre><code>{opencodeConfig}</code></pre>

        <h3>Claude Code / Cursor / Continue</h3>
        <p>The same endpoint works for any MCP client that supports the streamable-HTTP transport:</p>
        <pre><code>{claudeConfig}</code></pre>
      </section>

      <section id="tools" aria-labelledby="tools-h">
        <h2 id="tools-h">Tools</h2>
        <p>The server exposes the following tools to connected agents. Names match what the agent sees in its tool list:</p>
        <div class="tool-grid mt-4">
          {#each tools as t}
            <div class="tool-card">
              <code>{t.name}</code>
              <p>{t.summary}</p>
              {#if t.detail}<p style="font-style: italic; opacity: 0.85">{t.detail}</p>{/if}
            </div>
          {/each}
        </div>
      </section>

      <section id="documentation" aria-labelledby="documentation-h">
        <h2 id="documentation-h">Documentation</h2>
        <p>The bundled corpus is a read-only SQLite index plus zstd-compressed markdown blobs, packaged into the wheel. The index covers stdlib modules, common third-party libraries, and a curated set of PEPs. Sections are addressable by path and discoverable via <code>list_sections</code>.</p>
        <p>To add the server's documentation to an agent's context, you typically wire it through the agent's MCP integration:</p>
        <pre><code># OpenCode
opencode mcp add python-docsbox \
  --transport http \
  --url https://python-mcp.afterrealism.com/mcp</code></pre>
        <p class="muted">After adding, the agent can call <code>list_sections</code> to discover paths and <code>get_documentation</code> to fetch markdown for any section it needs.</p>
      </section>

      <section id="trust" aria-labelledby="trust-h">
        <h2 id="trust-h">Trust model</h2>
        <ul class="list-disc pl-6 space-y-1.5" style="color: var(--fg)">
          <li>All linting, formatting, and type-checking runs in tempdirs with bounded timeouts and bounded captured output.</li>
          <li>Tempdirs are cleaned up on exit; no persistent disk state per request.</li>
          <li><code>run_locally</code> never executes code on the server. It returns a plan; the calling agent dispatches the steps through its own host bash tool.</li>
          <li>HTTP fetches (docs, PEPs, PyPI) follow redirects with a 15&nbsp;s timeout.</li>
        </ul>
      </section>

      <section id="faq" aria-labelledby="faq-h">
        <h2 id="faq-h">FAQ</h2>
        <dl class="grid gap-5">
          {#each faqs as f}
            <div>
              <dt class="font-semibold" style="color: var(--fg)">{f.q}</dt>
              <dd class="mt-1" style="color: var(--muted)">{f.a}</dd>
            </div>
          {/each}
        </dl>
      </section>

      <section id="source" aria-labelledby="source-h">
        <h2 id="source-h">Source</h2>
        <p><a href="https://github.com/afterrealism/python-docsbox-mcp">github.com/afterrealism/python-docsbox-mcp</a>, MIT licensed.</p>
      </section>
    </article>
  </div>
</div>
