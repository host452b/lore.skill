#!/usr/bin/env node
'use strict';

// Lore CLI — install and run lore tools in a consuming project.
//
// Usage:
//   npx github:host452b/lore.skill init         Install lore into this project
//   npx github:host452b/lore.skill validate <p>  Validate a record
//   npx github:host452b/lore.skill harvest       Stage git history candidates
//   npx github:host452b/lore.skill new-id        Generate a record ID

const fs = require('fs');
const path = require('path');
const { execSync, spawnSync } = require('child_process');

const PACKAGE_DIR = path.resolve(__dirname, '..');
const CWD = process.cwd();
const CLAUDE_DIR = path.join(CWD, '.claude');

const args = process.argv.slice(2);
const command = args[0] || 'help';

// ── helpers ──────────────────────────────────────────────────────────────────

function mkdirp(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

const SKIP = new Set(['__pycache__', '.DS_Store']);

function copyDir(src, dest) {
  mkdirp(dest);
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    if (SKIP.has(entry.name) || entry.name.endsWith('.pyc')) continue;
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);
    if (entry.isDirectory()) {
      copyDir(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

function appendGitignore(lines) {
  const p = path.join(CWD, '.gitignore');
  const existing = fs.existsSync(p) ? fs.readFileSync(p, 'utf8') : '';
  const toAdd = lines.filter(l => !existing.includes(l));
  if (toAdd.length) {
    fs.appendFileSync(p, '\n' + toAdd.join('\n') + '\n');
  }
}

function requireInstalled() {
  const scripts = path.join(CLAUDE_DIR, 'scripts');
  if (!fs.existsSync(scripts)) {
    console.error('Lore is not installed. Run: npx github:host452b/lore.skill init');
    process.exit(1);
  }
}

// ── commands ─────────────────────────────────────────────────────────────────

function cmdInit() {
  console.log('Installing lore v0.1 into', CWD, '…\n');

  // 1. .lore/ record store
  for (const dir of ['live', 'archive', 'canon', '.harvest']) {
    const full = path.join(CWD, '.lore', dir);
    mkdirp(full);
    const keep = path.join(full, '.gitkeep');
    if (!fs.existsSync(keep)) fs.writeFileSync(keep, '');
  }
  console.log('  ✓  .lore/ (live / archive / canon / .harvest)');

  // 2. .claude/scripts/
  const destScripts = path.join(CLAUDE_DIR, 'scripts');
  copyDir(path.join(PACKAGE_DIR, 'scripts'), destScripts);
  for (const f of fs.readdirSync(destScripts)) {
    if (f.endsWith('.sh')) fs.chmodSync(path.join(destScripts, f), 0o755);
  }
  console.log('  ✓  .claude/scripts/');

  // 3. .claude/skills/
  copyDir(path.join(PACKAGE_DIR, 'skills'), path.join(CLAUDE_DIR, 'skills'));
  console.log('  ✓  .claude/skills/');

  // 4. .claude/hooks/  — skip if hook already exists (preserve customisations)
  const destHooks = path.join(CLAUDE_DIR, 'hooks');
  mkdirp(destHooks);
  const hookSrc = path.join(PACKAGE_DIR, 'hooks', 'session-start');
  const hookDst = path.join(destHooks, 'session-start');
  if (fs.existsSync(hookDst)) {
    console.log('  –  .claude/hooks/session-start (already exists, kept)');
  } else {
    fs.copyFileSync(hookSrc, hookDst);
    fs.chmodSync(hookDst, 0o755);
    console.log('  ✓  .claude/hooks/session-start');
  }

  // 5. .gitignore
  appendGitignore([
    '',
    '# Lore harvest staging area (ephemeral drafts)',
    '.lore/.harvest/*.md',
  ]);
  console.log('  ✓  .gitignore updated');

  console.log(`
Done.

Start a new Claude Code session — the agent will introduce lore.
Then run:
  lore:detect    (first-run project scan)
  lore:harvest   (mine git history for candidate records)

Scripts (run directly):
  python3 .claude/scripts/validate.py <path>
  python3 .claude/scripts/from-git-log.py --since "2 weeks ago"
  bash    .claude/scripts/new-id.sh --slug <slug> --dir .lore/canon/codex
`);
}

function cmdValidate() {
  requireInstalled();
  const filePath = args[1];
  if (!filePath) {
    console.error('Usage: lore validate <path-to-record.md>');
    process.exit(1);
  }
  const script = path.join(CLAUDE_DIR, 'scripts', 'validate.py');
  const r = spawnSync('python3', [script, filePath], { stdio: 'inherit' });
  process.exit(r.status ?? 1);
}

function cmdHarvest() {
  requireInstalled();
  const script = path.join(CLAUDE_DIR, 'scripts', 'from-git-log.py');
  // pass through all remaining args
  const r = spawnSync('python3', [script, ...args.slice(1)], {
    stdio: 'inherit',
    cwd: CWD,
  });
  process.exit(r.status ?? 1);
}

function cmdNewId() {
  requireInstalled();
  const script = path.join(CLAUDE_DIR, 'scripts', 'new-id.sh');
  const r = spawnSync('bash', [script, ...args.slice(1)], {
    stdio: 'inherit',
    cwd: CWD,
  });
  process.exit(r.status ?? 1);
}

function cmdHelp() {
  console.log(`
lore <command> [options]

Commands:
  init                  Install lore into the current project
  validate <path>       Validate a lore record's frontmatter
  harvest [options]     Stage git history as candidate draft records
  new-id [options]      Generate a lore record ID

Examples:
  npx github:host452b/lore.skill init
  npx github:host452b/lore.skill harvest --since "2 weeks ago"
  npx github:host452b/lore.skill validate .lore/canon/codex/2026-04-17-my-decision.md

After init, scripts are at .claude/scripts/ and can be called directly:
  python3 .claude/scripts/validate.py <path>
  python3 .claude/scripts/from-git-log.py --last 10
  bash    .claude/scripts/new-id.sh --slug my-decision --dir .lore/canon/codex
`);
}

// ── dispatch ─────────────────────────────────────────────────────────────────

switch (command) {
  case 'init':        cmdInit();     break;
  case 'validate':    cmdValidate(); break;
  case 'harvest':     cmdHarvest();  break;
  case 'new-id':      cmdNewId();    break;
  case 'help':
  case '--help':
  case '-h':          cmdHelp();     break;
  default:
    console.error(`Unknown command: ${command}\n`);
    cmdHelp();
    process.exit(1);
}
