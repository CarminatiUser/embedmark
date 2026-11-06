import { spawn } from 'node:child_process';
import * as path from 'node:path';

export interface Issue {
  severity: 'error' | 'warning' | 'info';
  code: string;
  message: string;
  line?: number;
  column?: number;
}
export interface Font { symbol: string; source?: string | null; size: number; }
export interface BackendResult {
  protocol: 1;
  ok: boolean;
  version: string;
  diagnostics: Issue[];
  code?: string;
  header?: string;
  fonts?: Font[];
  result?: unknown;
}
export interface Cancellation {
  readonly isCancellationRequested: boolean;
  onCancellationRequested(callback: () => void): { dispose(): void };
}
export interface BackendOptions {
  python: string;
  launcher: string;
  request: unknown;
  timeoutMs: number;
  cancellation?: Cancellation;
}
export class CancelledError extends Error {
  constructor() { super('Operação cancelada.'); this.name = 'CancelledError'; }
}
const INPUT_LIMIT = 8 * 1024 * 1024;
const OUTPUT_LIMIT = 32 * 1024 * 1024;

export function parseResponse(text: string): BackendResult {
  let data: unknown;
  try { data = JSON.parse(text); } catch { throw new Error('O tradutor retornou uma resposta inválida. Reinstale a extensão.'); }
  if (!data || typeof data !== 'object') { throw new Error('Resposta vazia do tradutor.'); }
  const r = data as Partial<BackendResult>;
  if (r.protocol !== 1 || r.version !== '0.4.0' || typeof r.ok !== 'boolean' || !Array.isArray(r.diagnostics)) {
    throw new Error('Versão ou formato incompatível do tradutor incluído na extensão.');
  }
  for (const issue of r.diagnostics) {
    if (!issue || !['error', 'warning', 'info'].includes(issue.severity) || typeof issue.code !== 'string' || typeof issue.message !== 'string') {
      throw new Error('Diagnóstico inválido do tradutor.');
    }
    for (const n of [issue.line, issue.column]) {
      if (n !== undefined && n !== null && (!Number.isInteger(n) || n < 1)) { throw new Error('Posição de diagnóstico inválida.'); }
    }
  }
  if (r.fonts !== undefined && (!Array.isArray(r.fonts) || r.fonts.some(f => !f || typeof f.symbol !== 'string' || !Number.isInteger(f.size) || (f.source !== undefined && f.source !== null && typeof f.source !== 'string')))) {
    throw new Error('Lista de fontes inválida.');
  }
  if ((r.code !== undefined && typeof r.code !== 'string') || (r.header !== undefined && typeof r.header !== 'string')) {
    throw new Error('Código gerado inválido.');
  }
  return r as BackendResult;
}

export function runBackend(options: BackendOptions): Promise<BackendResult> {
  if (options.cancellation?.isCancellationRequested) { return Promise.reject(new CancelledError()); }
  const input = JSON.stringify(options.request);
  if (Buffer.byteLength(input) > INPUT_LIMIT) { return Promise.reject(new Error('O pedido ultrapassa o limite de 8 MiB. Reduza o HTML.')); }
  return new Promise((resolve, reject) => {
    // A directory owned by the extension prevents loading executable files from the HTML project.
    const child = spawn(options.python, ['-I', '-S', '-B', options.launcher], {
      cwd: path.dirname(options.launcher), shell: false, windowsHide: true,
      stdio: ['pipe', 'pipe', 'pipe'],
    });
    let settled = false;
    let bytes = 0;
    const stdout: Buffer[] = [];
    let stderr = '';
    let subscription: { dispose(): void } | undefined;
    let killTimer: NodeJS.Timeout | undefined;
    const finish = (error?: Error, result?: BackendResult) => {
      if (settled) { return; }
      settled = true;
      clearTimeout(timer);
      subscription?.dispose();
      if (error) { reject(error); } else { resolve(result!); }
    };
    const abort = (error: Error) => {
      if (settled) { return; }
      child.kill();
      killTimer = setTimeout(() => child.kill('SIGKILL'), 500);
      killTimer.unref();
      finish(error);
    };
    const timer = setTimeout(() => abort(new Error('O tradutor excedeu o tempo limite. Simplifique a tela ou ajuste timeoutSeconds.')), options.timeoutMs);
    subscription = options.cancellation?.onCancellationRequested(() => abort(new CancelledError()));
    if (options.cancellation?.isCancellationRequested) { abort(new CancelledError()); }
    child.stdout.on('data', (chunk: Buffer) => {
      if (settled) { return; }
      bytes += chunk.length;
      if (bytes > OUTPUT_LIMIT) { abort(new Error('A saída do tradutor ultrapassou 32 MiB.')); return; }
      stdout.push(chunk);
    });
    child.stderr.on('data', (chunk: Buffer) => { if (stderr.length < 4096) { stderr += chunk.toString('utf8').slice(0, 4096 - stderr.length); } });
    child.on('error', (error: NodeJS.ErrnoException) => finish(new Error(
      error.code === 'ENOENT' ? 'Python não encontrado. Instale Python 3.10+ ou ajuste EmbedMark: Python Path.' : `Não foi possível iniciar Python: ${error.message}`,
    )));
    child.stdin.on('error', (error: NodeJS.ErrnoException) => { if (error.code !== 'EPIPE') { abort(error); } });
    child.on('close', (code, signal) => {
      if (killTimer) { clearTimeout(killTimer); }
      if (settled) { return; }
      try {
        const response = parseResponse(Buffer.concat(stdout).toString('utf8'));
        if (response.ok && code !== 0) { throw new Error(`O tradutor foi interrompido (${signal ?? code}).`); }
        finish(undefined, response);
      } catch (error) {
        const detail = stderr.trim().slice(0, 1000);
        finish(new Error(`${(error as Error).message}${detail ? `\n${detail}` : ''}`));
      }
    });
    child.stdin.end(input);
  });
}
