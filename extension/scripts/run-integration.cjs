const { downloadAndUnzipVSCode } = require('@vscode/test-electron');
const { spawn } = require('node:child_process');
const fs = require('node:fs/promises');
const os = require('node:os');
const path = require('node:path');
async function main() {
  const root = path.resolve(__dirname, '..');
  let executable = process.env.VSCODE_EXECUTABLE_PATH;
  if (!executable && process.platform === 'darwin') {
    const installed = '/Applications/Visual Studio Code.app/Contents/MacOS/Code';
    try { await fs.access(installed); executable = installed; } catch { /* Download below on a clean runner. */ }
  }
  executable ||= await downloadAndUnzipVSCode('stable');
  // macOS Unix-domain sockets are capped near 104 bytes, including profile paths.
  const temp = await fs.mkdtemp(path.join(process.platform === 'darwin' ? '/tmp' : os.tmpdir(), 'tcc-vsc-'));
  try {
    for (const mode of ['trusted', 'untrusted']) {
      const testRoot = path.join(temp, mode === 'trusted' ? 't' : 'u');
      const first = path.join(testRoot, 'projeto ação'); const second = path.join(testRoot, 'outro projeto');
      const userData = path.join(testRoot, 'user');
      await fs.mkdir(first, { recursive: true }); await fs.mkdir(second, { recursive: true }); await fs.mkdir(path.join(userData, 'User'), { recursive: true });
      await fs.writeFile(path.join(userData, 'User', 'settings.json'), JSON.stringify({
        'security.workspace.trust.startupPrompt': 'never', 'security.workspace.trust.enabled': mode !== 'trusted',
        'update.mode': 'none', 'extensions.autoCheckUpdates': false, 'extensions.autoUpdate': false,
        'telemetry.telemetryLevel': 'off', 'workbench.startupEditor': 'none', 'window.restoreWindows': 'none'
      }));
      const workspaceFile = path.join(testRoot, 'teste.code-workspace');
      await fs.writeFile(workspaceFile, JSON.stringify({ folders: [{ path: first }, { path: second }] }));
      // test-electron runTests forcibly disables Workspace Trust; launch directly
      // so the restricted pass exercises the real trust boundary.
      const args = [workspaceFile, '--user-data-dir', userData, '--extensions-dir', path.join(testRoot, 'extensions'),
          '--extensionDevelopmentPath=' + root,
          '--extensionTestsPath=' + path.join(root, 'dist/test/integration.test.js'),
          '--skip-welcome', '--skip-release-notes', '--disable-updates', '--disable-telemetry', '--disable-extensions',
          ...(process.platform === 'linux' && process.env.CI ? ['--no-sandbox', '--disable-gpu-sandbox'] : []),
          ...(mode === 'trusted' ? ['--disable-workspace-trust'] : [])];
      await new Promise((resolve, reject) => {
        const env = { ...process.env, TCC_TEST_MODE: mode, TCC_TEST_ROOT: testRoot };
        delete env.ELECTRON_RUN_AS_NODE;
        const child = spawn(executable, args, { env, stdio: 'inherit', shell: false });
        const timer = setTimeout(() => { child.kill('SIGKILL'); reject(new Error('VS Code integration test timed out: ' + mode)); }, 180000);
        child.on('error', error => { clearTimeout(timer); reject(error); });
        child.on('close', code => { clearTimeout(timer); code === 0 ? resolve() : reject(new Error('VS Code integration test failed: ' + mode + ' (exit ' + code + ')')); });
      });
    }
  } finally {
    if (!process.env.TCC_KEEP_TEST_PROFILE) { await fs.rm(temp, { recursive: true, force: true }); }
    else { console.log('Perfil de teste preservado:', temp); }
  }
}
main().catch(error => { console.error(error); process.exitCode = 1; });
