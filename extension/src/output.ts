import { createHash, randomUUID } from 'node:crypto';
import * as fs from 'node:fs/promises';
import * as path from 'node:path';
import { BackendResult } from './backend';

const MANIFEST = '.embedmark-output.json';
const LEGACY_MANIFEST = '.tcc-ui-output.json';
const OWNER = 'embedmark';
const LEGACY_OWNER = 'tcc-ui-translator';
interface Manifest { schema: 1; owner: string; source: string; files: Record<string, string>; }
function hash(data: Uint8Array | string): string { return createHash('sha256').update(data).digest('hex'); }
function existsError(e: unknown, code: string): boolean { return (e as NodeJS.ErrnoException).code === code; }
export function within(parent: string, child: string): boolean {
  const relative = path.relative(parent, child);
  return relative !== '' && relative !== '..' && !relative.startsWith(`..${path.sep}`) && !path.isAbsolute(relative);
}
export function resolveOutput(base: string, sourcePath: string, setting: string): string {
  const stem = path.basename(sourcePath, path.extname(sourcePath));
  if (!setting.trim() || setting.includes('\0')) { throw new Error('Defina uma pasta exclusiva para a saída.'); }
  const expanded = setting.replaceAll('${fileBasenameNoExtension}', stem);
  if (expanded.includes('${')) { throw new Error('outputDirectory aceita apenas a variável ${fileBasenameNoExtension}.'); }
  const target = path.resolve(base, expanded);
  if (!within(base, target)) { throw new Error('A pasta de saída deve ficar dentro da pasta do projeto e não pode ser sua raiz.'); }
  if (target === sourcePath || within(target, sourcePath)) { throw new Error('A pasta de saída não pode conter o HTML de entrada.'); }
  return target;
}
async function regularFile(filename: string): Promise<Buffer> {
  const stat = await fs.lstat(filename);
  if (!stat.isFile() || stat.isSymbolicLink()) { throw new Error(`O arquivo não pode ser um link ou diretório: ${path.basename(filename)}.`); }
  if (stat.size > 16 * 1024 * 1024) { throw new Error(`Arquivo maior que 16 MiB: ${path.basename(filename)}.`); }
  return fs.readFile(filename);
}
export async function prepareFiles(response: BackendResult, fontManifest?: string): Promise<Map<string, Buffer>> {
  if (!response.ok || !response.code || !response.header) { throw new Error('A geração não produziu código válido.'); }
  const files = new Map<string, Buffer>([
    ['ui_generated.c', Buffer.from(response.code)], ['ui_generated.h', Buffer.from(response.header)],
    ['translation.json', Buffer.from(JSON.stringify(response.result ?? {}, null, 2) + '\n')],
  ]);
  const reserved = new Set([...files.keys(), MANIFEST, LEGACY_MANIFEST, 'sources.cmake', 'fontes.json'].map(name => name.toLowerCase()));
  const copied = new Map<string, string>();
  for (const font of response.fonts ?? []) {
    if (!font.source) { continue; }
    if (!fontManifest) { throw new Error('Fonte externa sem catálogo de origem.'); }
    const folded = font.source.toLowerCase();
    if (!/^[A-Za-z0-9_][A-Za-z0-9_.-]*\.c$/.test(font.source) || reserved.has(folded) || (copied.has(folded) && copied.get(folded) !== font.source)) {
      throw new Error(`Nome de arquivo de fonte inseguro ou repetido: ${font.source}.`);
    }
    if (copied.has(folded)) { continue; }
    files.set(font.source, await regularFile(path.join(path.dirname(fontManifest), font.source)));
    copied.set(folded, font.source);
  }
  if (fontManifest && copied.size > 0) {
    const original = JSON.parse((await regularFile(fontManifest)).toString('utf8')) as { name?: string };
    files.set('fontes.json', Buffer.from(JSON.stringify({
      schema_version: 1, name: original.name ?? 'Fontes da interface',
      fonts: (response.fonts ?? []).filter(font => font.source),
    }, null, 2) + '\n'));
    // Preserve notices next to the catalog; never follow links or traverse directories.
    for (const entry of await fs.readdir(path.dirname(fontManifest), { withFileTypes: true })) {
      if (entry.isFile() && /^(?:OFL|LICENSE|LICENCE|COPYING|NOTICE)(?:[._-].*)?$/i.test(entry.name)) {
        if ([...files.keys(), MANIFEST, LEGACY_MANIFEST, 'sources.cmake'].some(name => name.toLowerCase() === entry.name.toLowerCase())) { throw new Error('Nome de licença em conflito com a saída.'); }
        files.set(entry.name, await regularFile(path.join(path.dirname(fontManifest), entry.name)));
      }
    }
  }
  const sources = [...files.keys()].filter(name => name.endsWith('.c'));
  files.set('sources.cmake', Buffer.from('set(EMBEDMARK_UI_SOURCES\n' + sources.map(name => `  "\${CMAKE_CURRENT_LIST_DIR}/${name}"`).join('\n') + '\n)\n'
    + '# Compatibility alias for firmware projects created before EmbedMark.\nset(TCC_UI_SOURCES ${EMBEDMARK_UI_SOURCES})\n'));
  return files;
}
async function ensureSafeParents(base: string, target: string): Promise<void> {
  if (!within(base, target)) { throw new Error('Pasta de saída fora do projeto.'); }
  // Resolve the user-selected workspace root once, but refuse links below it.
  const segments = path.relative(base, target).split(path.sep);
  let current = base;
  for (const segment of segments) {
    current = path.join(current, segment);
    try {
      const stat = await fs.lstat(current);
      if (!stat.isDirectory() || stat.isSymbolicLink()) { throw new Error('A saída não pode atravessar links simbólicos ou arquivos.'); }
    } catch (error) { if (!existsError(error, 'ENOENT')) { throw error; } }
  }
}
async function verifyExisting(target: string, source: string): Promise<boolean> {
  let entries: string[];
  try { entries = await fs.readdir(target); } catch (e) { if (existsError(e, 'ENOENT')) { return false; } throw e; }
  if (entries.length === 0) { return true; }
  if (entries.includes(MANIFEST) && entries.includes(LEGACY_MANIFEST)) {
    throw new Error('A pasta de saída contém registros de versões diferentes. Preserve os arquivos e escolha outra pasta.');
  }
  const manifestName = entries.includes(MANIFEST) ? MANIFEST : LEGACY_MANIFEST;
  const owner = manifestName === MANIFEST ? OWNER : LEGACY_OWNER;
  let manifest: Manifest;
  try { manifest = JSON.parse((await regularFile(path.join(target, manifestName))).toString('utf8')) as Manifest; }
  catch { throw new Error('A pasta de saída contém arquivos que não pertencem a esta extensão. Escolha outra pasta.'); }
  if (manifest.schema !== 1 || manifest.owner !== owner || manifest.source !== source || !manifest.files || typeof manifest.files !== 'object' || Array.isArray(manifest.files)) {
    throw new Error('A pasta de saída pertence a outra interface ou tem um registro inválido. Escolha outra pasta.');
  }
  const expected = Object.keys(manifest.files);
  if (entries.length !== expected.length + 1 || entries.some(name => name !== manifestName && !Object.hasOwn(manifest.files, name))) {
    throw new Error('Há arquivos adicionados manualmente na pasta de saída. Mova-os antes de gerar novamente.');
  }
  for (const name of expected) {
    if (path.basename(name) !== name || [MANIFEST, LEGACY_MANIFEST].includes(name.toLowerCase()) || hash(await regularFile(path.join(target, name))) !== manifest.files[name]) {
      throw new Error(`Arquivo gerado foi alterado: ${name}. Preserve sua alteração ou escolha outra pasta de saída.`);
    }
  }
  return true;
}
export async function writeOutput(base: string, target: string, source: string, files: Map<string, Buffer>, beforeCommit: () => void = () => {}): Promise<void> {
  const foldedNames = new Set<string>();
  for (const name of files.keys()) {
    const folded = name.toLowerCase();
    if (path.basename(name) !== name || name === '.' || name === '..' || [MANIFEST, LEGACY_MANIFEST].includes(folded) || name.includes('\0') || foldedNames.has(folded)) { throw new Error('Nome inseguro na saída.'); }
    foldedNames.add(folded);
  }
  await ensureSafeParents(base, target);
  const parent = path.dirname(target);
  await fs.mkdir(parent, { recursive: true });
  await ensureSafeParents(base, target);
  // Acquire the legacy lock first so an older installation cannot write concurrently.
  const lockPaths = ['tcc-ui-lock', 'embedmark-lock'].map(suffix => path.join(parent, `.${path.basename(target)}.${suffix}`));
  const locks: { filename: string; handle: fs.FileHandle }[] = [];
  let stage: string | undefined;
  let backup: string | undefined;
  try {
    for (const filename of lockPaths) {
      try { locks.push({ filename, handle: await fs.open(filename, 'wx') }); } catch (e) {
        if (existsError(e, 'EEXIST')) { throw new Error(`Esta saída está em uso ou uma geração anterior foi interrompida. Verifique o arquivo ${path.basename(filename)} na pasta superior.`); }
        throw e;
      }
    }
    const hadOutput = await verifyExisting(target, source);
    stage = await fs.mkdtemp(path.join(parent, '.embedmark-stage-'));
    const manifest: Manifest = { schema: 1, owner: OWNER, source, files: {} };
    for (const [name, data] of files) { await fs.writeFile(path.join(stage, name), data, { flag: 'wx' }); manifest.files[name] = hash(data); }
    await fs.writeFile(path.join(stage, MANIFEST), JSON.stringify(manifest, null, 2) + '\n', { flag: 'wx' });
    // Recheck immediately before the atomic swap, including manual edits made during translation.
    await ensureSafeParents(base, target);
    if (!hadOutput && await verifyExisting(target, source)) { throw new Error('A pasta de saída foi criada durante a geração. Execute novamente.'); }
    if (hadOutput) {
      await verifyExisting(target, source);
      beforeCommit();
      backup = path.join(parent, `.embedmark-backup-${randomUUID()}`);
      await fs.rename(target, backup);
    }
    try { beforeCommit(); await fs.rename(stage, target); stage = undefined; }
    catch (e) { if (backup) { await fs.rename(backup, target); backup = undefined; } throw e; }
    if (backup) { await fs.rm(backup, { recursive: true }); backup = undefined; }
  } finally {
    if (stage) { await fs.rm(stage, { recursive: true, force: true }); }
    // A failed rollback intentionally preserves the backup for recovery.
    for (const lock of locks.reverse()) {
      await lock.handle.close();
      await fs.unlink(lock.filename);
    }
  }
}
