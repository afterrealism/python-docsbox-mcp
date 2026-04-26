<script lang="ts">
  import 'virtual:uno.css';
  import '../app.css';

  let { children } = $props();
</script>

<div class="min-h-screen flex flex-col">
  <header class="sticky top-0 z-10 backdrop-blur" style="background: var(--header-bg); border-bottom: 1px solid var(--border)">
    <div class="max-w-7xl mx-auto flex items-center gap-4 px-6 py-3">
      <a href="/" class="flex items-center gap-2 font-semibold tracking-tight" style="color: var(--fg)">
        <span class="inline-block w-6 h-6 rounded-md" style="background: var(--accent)"></span>
        <span>Python DocsBox</span>
      </a>
      <span class="text-xs px-2 py-0.5 rounded-full" style="background: var(--accent-soft); color: var(--accent); border: 1px solid var(--accent)">MCP</span>
      <nav class="ml-auto flex items-center gap-5 text-sm" style="color: var(--muted)">
        <a href="#tools">Tools</a>
        <a href="#quickstart">Quick start</a>
        <a href="https://github.com/afterrealism/python-docsbox-mcp">GitHub</a>
      </nav>
    </div>
  </header>

  <main class="flex-1">
    {@render children()}
  </main>

  <footer class="px-6 py-8 text-sm" style="color: var(--muted); border-top: 1px solid var(--border)">
    <div class="max-w-7xl mx-auto flex flex-wrap gap-4 justify-between">
      <span>python-docsbox-mcp &middot; MIT</span>
      <span>part of <a href="https://afterrealism.com" style="color: var(--accent)">afterrealism</a></span>
    </div>
  </footer>
</div>
