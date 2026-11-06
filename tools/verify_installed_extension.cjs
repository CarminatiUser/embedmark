#!/usr/bin/env node
'use strict';

// Verify the installed artifact with independent, disposable VS Code profiles.
// The sole development extension is a tiny verifier, never the product source.
const { spawn } = require('node:child_process');
const { createHash } = require('node:crypto');
const fs = require('node:fs/promises');
const os = require('node:os');
const path = require('node:path');

const ROOT = path.resolve(__dirname, '..');
const EXTENSION = path.join(ROOT, 'extension');
const TIMEOUT_MS = 180_000;

function usage() {
  console.log('Uso: node tools/verify_installed_extension.cjs ARQUIVO.vsix [--report resultado.json]');
  console.log('VSCODE_EXECUTABLE_PATH: executável do VS Code; obrigatório fora do macOS.');
  console.log('EMBEDMARK_TEST_PYTHON: executável Python do teste; padrão python3/python.');
  console.log('EMBEDMARK_KEEP_TEST_PROFILE=1: preserva os perfis temporários para diagnóstico.');
}

function argumentsFor(argv) {
  if (argv.length === 1 && ['--help', '-h'].includes(argv[0])) { return { help: true }; }
  if (!argv[0] || argv[0].startsWith('-') || ![1, 3].includes(argv.length)
      || (argv.length === 3 && (argv[1] !== '--report' || !argv[2]))) {
    throw new Error('Informe um VSIX e, opcionalmente, --report arquivo.json. Use --help.');
  }
  return { vsix: path.resolve(argv[0]), report: argv[2] ? path.resolve(argv[2]) : undefined };
}

function isolatedEnvironment(extra = {}) {
  const env = { ...process.env };
  // Do not attach CLI requests to an existing personal VS Code process.
  for (const key of ['VSCODE_IPC_HOOK_CLI', 'VSCODE_PID', 'VSCODE_NLS_CONFIG', 'VSCODE_CWD', 'VSCODE_DEV', 'ELECTRON_RUN_AS_NODE']) {
    delete env[key];
  }
  return { ...env, ...extra };
}

function runProcess(executable, args, { env, label, timeoutMs = TIMEOUT_MS } = {}) {
  return new Promise((resolve, reject) => {
    console.log(`\n${label ?? 'Executando verificação'}…`);
    const child = spawn(executable, args, {
      env: env ?? isolatedEnvironment(), cwd: ROOT, shell: false,
      detached: process.platform !== 'win32', windowsHide: true,
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    let stdout = '';
    let stderr = '';
    let timedOut = false;
    let forceTimer;
    const terminate = (force) => {
      if (!child.pid) { return; }
      try {
        if (process.platform === 'win32') {
          // The PID belongs solely to this isolated verifier process.
          const killer = spawn('taskkill', ['/PID', String(child.pid), '/T', ...(force ? ['/F'] : [])], {
            shell: false, windowsHide: true, stdio: 'ignore',
          });
          killer.on('error', () => child.kill());
        } else { process.kill(-child.pid, force ? 'SIGKILL' : 'SIGTERM'); }
      } catch (error) { if (error.code !== 'ESRCH') { child.kill(force ? 'SIGKILL' : 'SIGTERM'); } }
    };
    const timer = setTimeout(() => {
      timedOut = true;
      terminate(false);
      forceTimer = setTimeout(() => terminate(true), 1000);
      forceTimer.unref();
    }, timeoutMs);
    child.stdout.on('data', chunk => {
      const text = chunk.toString('utf8');
      stdout = (stdout + text).slice(-512 * 1024);
      process.stdout.write(text);
    });
    child.stderr.on('data', chunk => {
      const text = chunk.toString('utf8');
      stderr = (stderr + text).slice(-128 * 1024);
      process.stderr.write(text);
    });
    child.on('error', error => {
      clearTimeout(timer);
      if (forceTimer) { clearTimeout(forceTimer); }
      reject(new Error(`${label}: ${error.message}`));
    });
    child.on('close', (code, signal) => {
      clearTimeout(timer);
      if (forceTimer) { clearTimeout(forceTimer); }
      if (timedOut || code !== 0) {
        reject(new Error(`${label}: ${timedOut ? 'tempo limite de 180 segundos' : `saída ${signal ?? code}`}\n${stderr.slice(-4000)}`));
      } else { resolve({ stdout, stderr, code }); }
    });
  });
}

async function cliInvocation(executable, profileArgs, commandArgs, label) {
  const { resolveCliArgsFromVSCodeExecutablePath } = require(path.join(EXTENSION, 'node_modules/@vscode/test-electron'));
  // Avoid the library's shared .vscode-test profile. Both directories are always
  // supplied explicitly below; no machine profile or user settings are reused.
  const [cli, ...prefix] = resolveCliArgsFromVSCodeExecutablePath(executable, { reuseMachineInstall: true });
  if (process.platform === 'win32' && cli.toLowerCase().endsWith('.cmd')) {
    // Same entry point as code.cmd, without a shell interpreting VSIX paths.
    const cliScript = path.resolve(path.dirname(cli), '../resources/app/out/cli.js');
    await fs.access(cliScript);
    return runProcess(executable, [cliScript, ...prefix, ...profileArgs, ...commandArgs], {
      label, env: isolatedEnvironment({ ELECTRON_RUN_AS_NODE: '1' }),
    });
  }
  return runProcess(cli, [...prefix, ...profileArgs, ...commandArgs], { label });
}

async function findInstalled(extensionsDir, expected) {
  const matches = [];
  for (const entry of await fs.readdir(extensionsDir, { withFileTypes: true })) {
    if (!entry.isDirectory()) { continue; }
    const directory = path.join(extensionsDir, entry.name);
    let manifest;
    try { manifest = JSON.parse(await fs.readFile(path.join(directory, 'package.json'), 'utf8')); }
    catch { continue; }
    if (`${manifest.publisher}.${manifest.name}` === expected.id && manifest.version === expected.version) {
      matches.push(directory);
    }
  }
  if (matches.length !== 1) { throw new Error(`Esperada uma instalação de ${expected.id}@${expected.version}; encontradas ${matches.length}.`); }
  return fs.realpath(matches[0]);
}

async function runMode(mode, temporary, executable, vsix, expected, integrationTests) {
  // Short ASCII profile paths avoid macOS's ~103-byte IPC socket path limit.
  const testRoot = path.join(temporary, mode === 'trusted' ? 't' : 'u');
  const userData = path.join(testRoot, 'p');
  const extensionsDir = path.join(testRoot, 'e');
  const verifier = path.join(testRoot, 'v');
  const first = path.join(testRoot, 'projeto ação');
  const second = path.join(testRoot, 'outro projeto');
  for (const directory of [path.join(userData, 'User'), extensionsDir, verifier, first, second]) {
    await fs.mkdir(directory, { recursive: true });
  }
  await fs.writeFile(path.join(userData, 'User', 'settings.json'), JSON.stringify({
    'security.workspace.trust.startupPrompt': 'never',
    'security.workspace.trust.enabled': mode !== 'trusted',
    'update.mode': 'none', 'extensions.autoCheckUpdates': false, 'extensions.autoUpdate': false,
    'telemetry.telemetryLevel': 'off', 'workbench.startupEditor': 'none', 'window.restoreWindows': 'none',
  }, null, 2));
  await fs.writeFile(path.join(verifier, 'package.json'), JSON.stringify({
    name: 'embedmark-installed-artifact-verifier', publisher: 'embedmark-local-verifier', version: '0.0.0',
    engines: { vscode: '^1.95.0' }, main: './index.js', activationEvents: ['*'],
    capabilities: { untrustedWorkspaces: { supported: true } },
  }, null, 2));
  await fs.writeFile(path.join(verifier, 'index.js'), 'exports.activate = () => ({});\n');
  const workspaceFile = path.join(testRoot, 'teste.code-workspace');
  await fs.writeFile(workspaceFile, JSON.stringify({ folders: [{ path: first }, { path: second }] }, null, 2));
  const profileArgs = ['--user-data-dir', userData, '--extensions-dir', extensionsDir];
  await cliInvocation(executable, profileArgs, ['--install-extension', vsix, '--disable-telemetry'], `Instalando VSIX no perfil ${mode}`);
  const installedRoot = await findInstalled(extensionsDir, expected);
  const listing = await cliInvocation(executable, profileArgs, ['--list-extensions', '--show-versions', '--disable-telemetry'], `Conferindo instalação ${mode}`);
  if (!listing.stdout.split(/\r?\n/).some(line => line.trim().toLowerCase() === `${expected.id}@${expected.version}`.toLowerCase())) {
    throw new Error(`O CLI não confirmou ${expected.id}@${expected.version}.`);
  }

  // test-electron.runTests() injects --disable-workspace-trust unconditionally.
  // Direct spawning is necessary to test the actual restricted-workspace case.
  // Do not add --disable-extensions: the product must load from the VSIX install.
  const result = await runProcess(executable, [
    workspaceFile, ...profileArgs, '--skip-welcome', '--skip-release-notes', '--disable-updates',
    '--disable-telemetry', '--no-cached-data', '--disable-gpu-sandbox',
    `--extensionDevelopmentPath=${verifier}`, `--extensionTestsPath=${integrationTests}`,
    ...(process.platform === 'linux' ? ['--no-sandbox'] : []),
    ...(mode === 'trusted' ? ['--disable-workspace-trust'] : []),
  ], {
    label: `Testando o artefato instalado: ${mode}`,
    env: isolatedEnvironment({
      EMBEDMARK_TEST_MODE: mode, EMBEDMARK_TEST_ROOT: testRoot, EMBEDMARK_TEST_EXTENSION_ID: expected.id,
      EMBEDMARK_EXPECT_INSTALLED_ROOT: installedRoot,
    }),
  });
  const marker = mode === 'trusted' ? 'PASS: commands' : 'PASS: restricted workspace';
  if (!result.stdout.includes(marker)) { throw new Error(`O processo ${mode} encerrou sem confirmar a execução da suíte (${marker}).`); }
  return { mode, status: 'passed', extension_id: expected.id, version: expected.version, installed_path: installedRoot };
}

async function main() {
  const options = argumentsFor(process.argv.slice(2));
  if (options.help) { usage(); return; }
  const executable = process.env.VSCODE_EXECUTABLE_PATH
    || (process.platform === 'darwin' ? '/Applications/Visual Studio Code.app/Contents/MacOS/Code' : undefined);
  if (!executable) { throw new Error('Defina VSCODE_EXECUTABLE_PATH com o executável local do VS Code.'); }
  await fs.access(executable);
  const vsixStat = await fs.stat(options.vsix);
  if (!vsixStat.isFile() || path.extname(options.vsix).toLowerCase() !== '.vsix') { throw new Error('O argumento deve apontar para um arquivo .vsix existente.'); }
  if (options.report) {
    let reportPath = options.report;
    try { reportPath = await fs.realpath(reportPath); } catch (error) { if (error.code !== 'ENOENT') { throw error; } }
    if (reportPath === await fs.realpath(options.vsix)) { throw new Error('O relatório não pode substituir o VSIX.'); }
  }
  const integrationTests = path.join(EXTENSION, 'dist/test/integration.test.js');
  const compiled = await fs.readFile(integrationTests, 'utf8');
  if (!compiled.includes('EMBEDMARK_EXPECT_INSTALLED_ROOT')) {
    throw new Error('Recompile a extensão: o teste deve confirmar que a instância ativada pertence ao VSIX instalado.');
  }
  const manifest = JSON.parse(await fs.readFile(path.join(EXTENSION, 'package.json'), 'utf8'));
  const expected = { id: `${manifest.publisher}.${manifest.name}`, version: manifest.version };
  const temporary = await fs.mkdtemp(path.join(process.platform === 'darwin' ? '/tmp' : os.tmpdir(), 'em-i-'));
  const artifact = await fs.readFile(options.vsix);
  const candidate = path.join(temporary, 'candidate.vsix');
  await fs.writeFile(candidate, artifact, { flag: 'wx' });
  const summary = {
    schema: 1, status: 'running', artifact: options.vsix,
    sha256: createHash('sha256').update(artifact).digest('hex'),
    vscode_executable: executable, profiles: [], started_at: new Date().toISOString(),
  };
  let failure;
  try {
    for (const mode of ['trusted', 'untrusted']) {
      summary.profiles.push(await runMode(mode, temporary, executable, candidate, expected, integrationTests));
    }
    const currentHash = createHash('sha256').update(await fs.readFile(options.vsix)).digest('hex');
    if (currentHash !== summary.sha256) { throw new Error('O VSIX original mudou durante os testes; execute a verificação novamente.'); }
    summary.status = 'passed';
  } catch (error) {
    summary.status = 'failed'; summary.error = error.message; failure = error;
  } finally {
    summary.completed_at = new Date().toISOString();
    if (failure || process.env.EMBEDMARK_KEEP_TEST_PROFILE) {
      summary.retained_profile = temporary;
      console.log(`Perfis isolados preservados: ${temporary}`);
    } else { await fs.rm(temporary, { recursive: true, force: true, maxRetries: 10, retryDelay: 200 }); }
    if (options.report) {
      await fs.mkdir(path.dirname(options.report), { recursive: true });
      await fs.writeFile(options.report, JSON.stringify(summary, null, 2) + '\n');
    }
    console.log('\n' + JSON.stringify(summary, null, 2));
  }
  if (failure) { throw failure; }
}

if (require.main === module) {
  main().catch(error => { console.error(`Verificação do VSIX instalado falhou: ${error.message}`); process.exitCode = 1; });
}
