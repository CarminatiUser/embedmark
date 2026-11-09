import { strict as assert } from 'node:assert';
import { createHash } from 'node:crypto';
import * as fs from 'node:fs/promises';
import * as os from 'node:os';
import * as path from 'node:path';
import { test } from 'node:test';
import { BackendResult, CancelledError, parseResponse, runBackend } from '../backend';
import { prepareFiles, resolveOutput, writeOutput } from '../output';
const response: BackendResult = { protocol: 1, ok: true, version: '0.4.1', diagnostics: [], code: '#include "ui_generated.h"\n', header: '#pragma once\n', fonts: [], result: { valid: true } };
async function temporary<T>(body: (dir: string) => Promise<T>): Promise<T> {
  const dir = await fs.mkdtemp(path.join(os.tmpdir(), 'embedmark ação-'));
  try { return await body(dir); } finally { await fs.rm(dir, { recursive: true, force: true }); }
}
function data(value: string): Map<string, Buffer> { return new Map([['ui_generated.c', Buffer.from(value)]]); }
async function legacyOutput(target: string): Promise<void> {
  await fs.mkdir(target);
  await fs.writeFile(path.join(target, 'ui_generated.c'), 'legacy code');
  await fs.writeFile(path.join(target, '.tcc-ui-output.json'), JSON.stringify({
    schema: 1, owner: 'tcc-ui-translator', source: 'legacy.html',
    files: { 'ui_generated.c': createHash('sha256').update('legacy code').digest('hex') },
  }));
}
const python = process.env.EMBEDMARK_TEST_PYTHON ?? (process.platform === 'win32' ? 'python' : 'python3');
test('managed output updates paths with spaces and Unicode', async () => temporary(async base => {
  const target = resolveOutput(base, path.join(base, 'minha ação.html'), 'generated/${fileBasenameNoExtension}');
  assert.equal(target, path.join(base, 'generated', 'minha ação'));
  await writeOutput(base, target, 'source1', data('first')); await writeOutput(base, target, 'source1', data('second'));
  assert.equal(await fs.readFile(path.join(target, 'ui_generated.c'), 'utf8'), 'second');
}));
test('legacy output migrates to EmbedMark only after a successful generation', async () => temporary(async base => {
  const target = path.join(base, 'out'); await legacyOutput(target);
  await writeOutput(base, target, 'legacy.html', data('new code'));
  assert.equal(await fs.readFile(path.join(target, 'ui_generated.c'), 'utf8'), 'new code');
  const manifest = JSON.parse(await fs.readFile(path.join(target, '.embedmark-output.json'), 'utf8'));
  assert.equal(manifest.owner, 'embedmark'); assert.equal(manifest.source, 'legacy.html');
  assert.deepEqual((await fs.readdir(target)).sort(), ['.embedmark-output.json', 'ui_generated.c']);
  assert.deepEqual(await fs.readdir(base), ['out']);
}));
test('legacy migration protects manual edits, extra files, source identity and conflicting records', async () => temporary(async base => {
  const target = path.join(base, 'out'); await legacyOutput(target);
  const original = await fs.readFile(path.join(target, '.tcc-ui-output.json'), 'utf8');
  await assert.rejects(writeOutput(base, target, 'different.html', data('new code')), /outra interface/);
  await fs.writeFile(path.join(target, 'ui_generated.c'), 'manual edit');
  await assert.rejects(writeOutput(base, target, 'legacy.html', data('new code')), /alterado/);
  assert.equal(await fs.readFile(path.join(target, 'ui_generated.c'), 'utf8'), 'manual edit');
  await fs.writeFile(path.join(target, 'ui_generated.c'), 'legacy code');
  await fs.writeFile(path.join(target, 'controller.c'), 'user code');
  await assert.rejects(writeOutput(base, target, 'legacy.html', data('new code')), /adicionados/);
  assert.equal(await fs.readFile(path.join(target, 'controller.c'), 'utf8'), 'user code');
  await fs.unlink(path.join(target, 'controller.c'));
  await fs.writeFile(path.join(target, '.embedmark-output.json'), original);
  await assert.rejects(writeOutput(base, target, 'legacy.html', data('new code')), /registros de versões diferentes/);
  assert.equal(await fs.readFile(path.join(target, '.tcc-ui-output.json'), 'utf8'), original);
  assert.equal(await fs.readFile(path.join(target, '.embedmark-output.json'), 'utf8'), original);
  assert.deepEqual(await fs.readdir(base), ['out']);
}));
test('cancelled legacy migration restores the original manifest and files', async () => temporary(async base => {
  const target = path.join(base, 'out'); await legacyOutput(target);
  const original = await fs.readFile(path.join(target, '.tcc-ui-output.json'), 'utf8');
  let guards = 0;
  await assert.rejects(writeOutput(base, target, 'legacy.html', data('new code'), () => {
    if (++guards === 2) { throw new CancelledError(); }
  }), CancelledError);
  assert.equal(await fs.readFile(path.join(target, '.tcc-ui-output.json'), 'utf8'), original);
  assert.equal(await fs.readFile(path.join(target, 'ui_generated.c'), 'utf8'), 'legacy code');
  assert.deepEqual((await fs.readdir(target)).sort(), ['.tcc-ui-output.json', 'ui_generated.c']);
  assert.deepEqual(await fs.readdir(base), ['out']);
}));
test('root, traversal, input ancestor and unknown variable are refused', () => {
  for (const setting of ['.', '../outside', '${workspaceFolder}/anything', '']) { assert.throws(() => resolveOutput('/workspace', '/workspace/tela.html', setting)); }
  assert.throws(() => resolveOutput('/workspace', '/workspace/generated/tela.html', 'generated'));
});
test('manual edits and unknown files remain intact', async () => temporary(async base => {
  const target = path.join(base, 'output'); await writeOutput(base, target, 'source', data('first'));
  await fs.writeFile(path.join(target, 'ui_generated.c'), 'manual');
  await assert.rejects(writeOutput(base, target, 'source', data('second')), /alterado/);
  assert.equal(await fs.readFile(path.join(target, 'ui_generated.c'), 'utf8'), 'manual');
  await fs.writeFile(path.join(target, 'ui_generated.c'), 'first'); await fs.writeFile(path.join(target, 'controller.c'), 'mine');
  await assert.rejects(writeOutput(base, target, 'source', data('second')), /adicionados/);
  assert.equal(await fs.readFile(path.join(target, 'controller.c'), 'utf8'), 'mine');
}));
test('another HTML cannot take over the output', async () => temporary(async base => {
  const target = path.join(base, 'output'); await writeOutput(base, target, 'first.html', data('first'));
  await assert.rejects(writeOutput(base, target, 'second.html', data('second')), /outra interface/);
  assert.equal(await fs.readFile(path.join(target, 'ui_generated.c'), 'utf8'), 'first');
}));
test('symlink traversal and linked generated files are refused', { skip: process.platform === 'win32' }, async () => temporary(async base => {
  const original = path.join(base, 'original'); await fs.mkdir(original); await fs.symlink(original, path.join(base, 'link'));
  await assert.rejects(writeOutput(base, path.join(base, 'link', 'out'), 'source', data('code')), /links/);
  assert.deepEqual(await fs.readdir(original), []);
  const target = path.join(base, 'out'); await writeOutput(base, target, 'source', data('first'));
  await fs.unlink(path.join(target, 'ui_generated.c')); await fs.writeFile(path.join(original, 'code.c'), 'first');
  await fs.symlink(path.join(original, 'code.c'), path.join(target, 'ui_generated.c'));
  await assert.rejects(writeOutput(base, target, 'source', data('second')), /link/);
  assert.equal(await fs.readFile(path.join(original, 'code.c'), 'utf8'), 'first');
}));
test('unmanaged content and outstanding locks are preserved', async () => temporary(async base => {
  const target = path.join(base, 'out'); await fs.mkdir(target); await fs.writeFile(path.join(target, 'precious.c'), 'user code');
  await assert.rejects(writeOutput(base, target, 'source', data('second')), /não pertencem/);
  assert.equal(await fs.readFile(path.join(target, 'precious.c'), 'utf8'), 'user code');
  for (const lock of ['.out.tcc-ui-lock', '.out.embedmark-lock']) {
    await fs.writeFile(path.join(base, lock), 'in use');
    await assert.rejects(writeOutput(base, target, 'source', data('second')), /em uso/);
    assert.equal(await fs.readFile(path.join(base, lock), 'utf8'), 'in use');
    assert.deepEqual((await fs.readdir(base)).sort(), [lock, 'out']);
    await fs.unlink(path.join(base, lock));
  }
}));
test('obsolete fonts removed only inside managed output', async () => temporary(async base => {
  const target = path.join(base, 'out'); const before = data('old'); before.set('old_font.c', Buffer.from('font'));
  await writeOutput(base, target, 'source', before); await fs.writeFile(path.join(base, 'controller.c'), 'controller');
  await writeOutput(base, target, 'source', data('new'));
  await assert.rejects(fs.stat(path.join(target, 'old_font.c')), { code: 'ENOENT' });
  assert.equal(await fs.readFile(path.join(base, 'controller.c'), 'utf8'), 'controller');
}));
test('font preparation copies used C sources and license notices', async () => temporary(async base => {
  const manifest = path.join(base, 'fontes.json'); await fs.writeFile(manifest, '{}'); await fs.writeFile(path.join(base, 'font.c'), 'font data'); await fs.writeFile(path.join(base, 'OFL.txt'), 'license');
  const files = await prepareFiles({ ...response, fonts: [{ symbol: 'embedmark_font_a', size: 14, source: 'font.c' }] }, manifest);
  assert.equal(files.get('font.c')?.toString(), 'font data'); assert.equal(files.get('OFL.txt')?.toString(), 'license');
  assert.match(files.get('sources.cmake')!.toString(), /\$\{CMAKE_CURRENT_LIST_DIR\}\/font\.c/);
  assert.match(files.get('sources.cmake')!.toString(), /set\(EMBEDMARK_UI_SOURCES/);
  assert.match(files.get('sources.cmake')!.toString(), /set\(TCC_UI_SOURCES \$\{EMBEDMARK_UI_SOURCES\}\)/);
}));
test('missing fonts, traversal and generated-name collisions fail before writes', async () => temporary(async base => {
  const manifest = path.join(base, 'fontes.json'); await fs.writeFile(manifest, '{}');
  for (const source of ['missing.c', '../outside.c', 'ui_generated.c', 'UI_GENERATED.c']) { await assert.rejects(prepareFiles({ ...response, fonts: [{ symbol: 'embedmark_font_a', size: 14, source }] }, manifest)); }
}));
test('response validates protocol, version, diagnostics and field types', () => {
  assert.deepEqual(parseResponse(JSON.stringify(response)), response);
  for (const invalid of [null, {}, { ...response, version: '0.1' }, { ...response, protocol: 9 }, { ...response, diagnostics: [{ severity: 'error', code: 'X', message: 'x', line: -1 }] }, { ...response, code: 123 }]) { assert.throws(() => parseResponse(JSON.stringify(invalid))); }
});
test('isolated subprocess preserves structured failure and Unicode input', async () => temporary(async base => {
  const launcher = path.join(base, 'ponte ação.py');
  // Match the real bridge's UTF-8 byte protocol, even with a Windows legacy text encoding.
  await fs.writeFile(launcher, 'import json,sys\nsys.stdin.reconfigure(encoding="cp1252")\nr=json.loads(sys.stdin.buffer.read().decode("utf-8"))\nprint(json.dumps({"protocol":1,"ok":False,"version":"0.4.1","diagnostics":[{"severity":"error","code":"EXPECTED","message":r["source"]}]}))\nsys.exit(1)\n');
  const result = await runBackend({ python, launcher, request: { source: 'ação 😃' }, timeoutMs: 5000 });
  assert.equal(result.ok, false); assert.equal(result.diagnostics[0]?.message, 'ação 😃');
}));
test('missing executable and malformed subprocess output give useful errors', async () => temporary(async base => {
  await assert.rejects(runBackend({ python: path.join(base, 'missing'), launcher: 'unused', request: {}, timeoutMs: 5000 }), /Python não encontrado/);
  const launcher = path.join(base, 'bad.py'); await fs.writeFile(launcher, 'print("not json")\n');
  await assert.rejects(runBackend({ python, launcher, request: {}, timeoutMs: 5000 }), /inválida/);
}));
test('timeout and cancellation stop translation', async () => temporary(async base => {
  const launcher = path.join(base, 'slow.py'); await fs.writeFile(launcher, 'import time\ntime.sleep(30)\n');
  await assert.rejects(runBackend({ python, launcher, request: {}, timeoutMs: 100 }), /tempo limite/);
  let callback = () => {};
  const result = runBackend({ python, launcher, request: {}, timeoutMs: 5000, cancellation: { isCancellationRequested: false, onCancellationRequested(fn) { callback = fn; return { dispose() {} }; } } });
  callback(); await assert.rejects(result, CancelledError);
}));
test('oversized request is refused before any subprocess starts', async () => {
  await assert.rejects(runBackend({ python: 'nonexistent', launcher: 'none', request: { source: 'a'.repeat(8 * 1024 * 1024) }, timeoutMs: 5000 }), /8 MiB/);
});
test('cancellation immediately before commit preserves the previous output', async () => temporary(async base => {
  const target = path.join(base, 'out');
  await writeOutput(base, target, 'source', data('old'));
  let stages = 0;
  await assert.rejects(writeOutput(base, target, 'source', data('new'), () => {
    stages += 1;
    // Second guard runs after the previous output has moved, exercising rollback.
    if (stages === 2) { throw new CancelledError(); }
  }), CancelledError);
  assert.equal(await fs.readFile(path.join(target, 'ui_generated.c'), 'utf8'), 'old');
  assert.deepEqual(await fs.readdir(base), ['out']);
}));
test('case-insensitive output collisions are rejected on all platforms', async () => temporary(async base => {
  const files = data('first'); files.set('UI_GENERATED.c', Buffer.from('second'));
  await assert.rejects(writeOutput(base, path.join(base, 'out'), 'source', files), /Nome inseguro/);
  assert.deepEqual(await fs.readdir(base), []);
}));
test('current and legacy manifest names are reserved before writing any output', async () => temporary(async base => {
  for (const name of ['.embedmark-output.json', '.EMBEDMARK-output.json', '.tcc-ui-output.json', '.TCC-UI-output.json']) {
    const files = data('first'); files.set(name, Buffer.from('{}'));
    await assert.rejects(writeOutput(base, path.join(base, 'out'), 'source', files), /Nome inseguro/);
    assert.deepEqual(await fs.readdir(base), []);
  }
}));
