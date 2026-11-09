const fs = require('node:fs');
const path = require('node:path');
const { createHash } = require('node:crypto');
const { spawnSync } = require('node:child_process');
const extension = path.resolve(__dirname, '..');
const root = path.dirname(extension);
const localPython = path.join(root, '.venv', process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python');
const python = process.env.EMBEDMARK_BUILD_PYTHON || (fs.existsSync(localPython) ? localPython : process.platform === 'win32' ? 'python' : 'python3');
const manifest = JSON.parse(fs.readFileSync(path.join(extension, 'package.json'), 'utf8'));
if (!/^[a-zA-Z0-9][a-zA-Z0-9-]*$/.test(manifest.publisher || '')) { throw new Error('Defina um publisher válido antes de empacotar.'); }
const args = [path.join(root, 'tools/bundle_backend.py'), ...(process.env.EMBEDMARK_BUNDLE_OFFLINE === '1' ? ['--offline'] : [])];
const result = spawnSync(python, args, { cwd: root, stdio: 'inherit', shell: false, timeout: 300000 });
if (result.error) { throw result.error; }
if (result.status !== 0) { process.exit(result.status || 1); }
const bundled = path.join(extension, 'bundled/python');
const bundle = JSON.parse(fs.readFileSync(path.join(bundled, 'BACKEND_MANIFEST.json'), 'utf8'));
if (bundle.translator !== manifest.version || bundle.protocol !== 1) { throw new Error('Versão da extensão diferente do backend.'); }
for (const [name, expected] of Object.entries(bundle.files)) {
  const resolved = path.resolve(bundled, name);
  if (!resolved.startsWith(bundled + path.sep) || !fs.lstatSync(resolved).isFile()) { throw new Error('Arquivo inseguro no bundle: ' + name); }
  const actual = createHash('sha256').update(fs.readFileSync(resolved)).digest('hex');
  if (actual !== expected) { throw new Error('Checksum do backend inválido: ' + name); }
}
for (const resource of ['bundled/launcher.py', 'resources/icon.png', 'resources/LANGUAGE_GUIDE.md', 'resources/FONTES.md', 'resources/API_FIRMWARE.md', 'resources/fonts/fontes.json', 'resources/fonts/OFL.txt', 'LICENSE.txt']) {
  if (!fs.statSync(path.join(extension, resource)).isFile()) { throw new Error('Recurso ausente: ' + resource); }
}
fs.mkdirSync(path.join(root, 'release'), { recursive: true });
console.log('Backend verificado. Publisher do pacote: ' + manifest.publisher);
