import * as fs from 'node:fs/promises';
import * as path from 'node:path';
import * as vscode from 'vscode';
import { BackendResult, CancelledError, Issue, runBackend } from './backend';
import { prepareFiles, resolveOutput, within, writeOutput } from './output';

export interface ExtensionApi {
  run(action: 'validate' | 'generate', uri?: vscode.Uri, quiet?: boolean): Promise<BackendResult | undefined>;
  diagnostics: vscode.DiagnosticCollection;
  readonly extensionMode: vscode.ExtensionMode;
}
interface Settings { python: string; timeoutMs: number; fontManifest?: string; config: Record<string, unknown>; outputDirectory: string; }
const busy = new Set<string>();

function readSettings(context: vscode.ExtensionContext, document: vscode.TextDocument): Settings {
  const config = vscode.workspace.getConfiguration('tccUiTranslator', document.uri);
  const preset = config.get<string>('displayPreset', 'st7789');
  const base = vscode.workspace.getWorkspaceFolder(document.uri)?.uri.fsPath ?? (document.uri.scheme === 'file' ? path.dirname(document.uri.fsPath) : undefined);
  const fontSetting = config.get<string>('fontManifest', '');
  let fontManifest: string | undefined;
  if (fontSetting !== 'builtin') {
    if (fontSetting && !path.isAbsolute(fontSetting) && !base) { throw new Error('Salve o HTML para resolver o caminho relativo do catálogo de fontes.'); }
    fontManifest = fontSetting ? path.resolve(base ?? '', fontSetting) : context.asAbsolutePath('resources/fonts/fontes.json');
  }
  const python = config.get<string>('pythonPath', '').trim() || (process.platform === 'win32' ? 'python' : 'python3');
  if (python.includes('\0') || python.includes('\n')) { throw new Error('Python Path deve conter apenas o executável, sem argumentos.'); }
  // Relative paths with directory separators have an unambiguous workspace origin.
  let executable = python;
  if (!path.isAbsolute(python) && (python.includes('/') || python.includes('\\'))) {
    if (!base) { throw new Error('Salve o HTML para resolver o caminho relativo do Python.'); }
    executable = path.resolve(base, python);
  }
  const seconds = config.get<number>('timeoutSeconds', 30);
  if (!Number.isInteger(seconds) || seconds < 5 || seconds > 120) { throw new Error('timeoutSeconds deve ficar entre 5 e 120.'); }
  const translation: Record<string, unknown> = {
    display_preset: preset, orientation: config.get('orientation', 'portrait'), strict: config.get('strict', true),
  };
  for (const [setting, key] of [['designWidth', 'design_width'], ['designHeight', 'design_height']] as const) {
    const value = config.get<number | null>(setting, null);
    if (value !== null) { translation[key] = value; }
  }
  if (preset === 'custom') { translation.display_width = config.get('displayWidth', 172); translation.display_height = config.get('displayHeight', 320); }
  if (fontManifest) { translation.font_manifest = fontManifest; }
  return { python: executable, timeoutMs: seconds * 1000, fontManifest, config: translation, outputDirectory: config.get('outputDirectory', 'generated/${fileBasenameNoExtension}') };
}
function toDiagnostic(issue: Issue, document: vscode.TextDocument): vscode.Diagnostic {
  const line = Math.max(0, Math.min(document.lineCount - 1, (issue.line ?? 1) - 1));
  const text = document.lineAt(line).text;
  // Python reports Unicode code points; VS Code positions use UTF-16 code units.
  const character = Array.from(text).slice(0, Math.max(0, (issue.column ?? 1) - 1)).join('').length;
  const end = Math.min(text.length, character + (text.codePointAt(character)! > 0xffff ? 2 : 1));
  const diagnostic = new vscode.Diagnostic(new vscode.Range(line, character, line, end), issue.message,
    issue.severity === 'error' ? vscode.DiagnosticSeverity.Error : issue.severity === 'warning' ? vscode.DiagnosticSeverity.Warning : vscode.DiagnosticSeverity.Information);
  diagnostic.code = issue.code;
  diagnostic.source = 'TCC UI';
  return diagnostic;
}
export function activate(context: vscode.ExtensionContext): ExtensionApi {
  const diagnostics = vscode.languages.createDiagnosticCollection('tcc-ui-translator');
  const output = vscode.window.createOutputChannel('TCC UI Translator');
  context.subscriptions.push(diagnostics, output);
  context.subscriptions.push(vscode.workspace.onDidCloseTextDocument(document => diagnostics.delete(document.uri)));
  context.subscriptions.push(vscode.workspace.onDidChangeTextDocument(event => {
    if (event.contentChanges.length > 0) { diagnostics.delete(event.document.uri); }
  }));
  async function run(action: 'validate' | 'generate', uri?: vscode.Uri, quiet = false): Promise<BackendResult | undefined> {
    if (!vscode.workspace.isTrusted) { throw new Error('Confie nesta pasta no VS Code para executar o tradutor Python. O guia permanece disponível em modo restrito.'); }
    let document = uri ? await vscode.workspace.openTextDocument(uri) : vscode.window.activeTextEditor?.document;
    if (!document) { throw new Error('Abra um arquivo HTML ou use TCC UI: Criar exemplo de contador.'); }
    if (document.languageId !== 'html' && !/\.html?$/i.test(document.fileName)) { throw new Error('Selecione um documento HTML para traduzir.'); }
    if (action === 'generate' && document.isUntitled) {
      await vscode.window.showTextDocument(document, { preview: false });
      const savedUri = await vscode.workspace.save(document.uri);
      if (!savedUri) { return undefined; }
      document = await vscode.workspace.openTextDocument(savedUri);
    }
    if (action === 'generate' && document.uri.scheme !== 'file') { throw new Error('Salve o HTML em uma pasta local antes de gerar o firmware.'); }
    const sourceUri = document.uri;
    const key = sourceUri.toString();
    if (busy.has(key)) { throw new Error('Este documento já está sendo traduzido. Aguarde ou cancele a operação atual.'); }
    const snapshot = document.getText();
    const version = document.version;
    const settings = readSettings(context, document);
    const base = vscode.workspace.getWorkspaceFolder(sourceUri)?.uri.fsPath ?? path.dirname(sourceUri.fsPath);
    const target = action === 'generate' ? resolveOutput(base, sourceUri.fsPath, settings.outputDirectory) : undefined;
    const checkDirtyOutput = () => {
      if (!target) { return; }
      const dirty = vscode.workspace.textDocuments.find(open => open.uri.scheme === 'file' && open.isDirty && within(target, open.uri.fsPath));
      if (dirty) { throw new Error(`Há alterações não salvas em ${path.basename(dirty.fileName)} na pasta de saída. Preserve-as antes de gerar.`); }
    };
    checkDirtyOutput();
    busy.add(key);
    try {
      return await vscode.window.withProgress({ location: vscode.ProgressLocation.Notification, title: action === 'generate' ? 'TCC UI: gerando interface' : 'TCC UI: validando interface', cancellable: true }, async (progress, token) => {
        progress.report({ message: 'Analisando HTML/CSS…' });
        const result = await runBackend({ python: settings.python, launcher: context.asAbsolutePath('bundled/launcher.py'),
          request: { protocol: 1, action, source: snapshot, config: settings.config }, timeoutMs: settings.timeoutMs, cancellation: token });
        if (token.isCancellationRequested) { throw new CancelledError(); }
        if (document!.isClosed || document!.version !== version) { throw new Error('O HTML mudou durante a tradução. Execute o comando novamente para usar o conteúdo atual.'); }
        diagnostics.set(sourceUri, result.diagnostics.map(issue => toDiagnostic(issue, document!)));
        output.appendLine(`${new Date().toISOString()} | ${action} | ${path.basename(document!.fileName)} | ${result.ok ? 'OK' : 'FALHOU'} | ${result.diagnostics.length} diagnóstico(s)`);
        for (const issue of result.diagnostics) { output.appendLine(`${issue.severity.toUpperCase()} ${issue.code}: ${issue.message}`); }
        if (!result.ok) {
          if (!quiet) { void vscode.window.showWarningMessage('A interface tem problemas. Consulte o painel Problemas (TCC UI).'); await vscode.commands.executeCommand('workbench.actions.view.problems'); }
          return result;
        }
        if (target) {
          progress.report({ message: 'Preparando os arquivos de firmware…' });
          const files = await prepareFiles(result, settings.fontManifest);
          if (token.isCancellationRequested) { throw new CancelledError(); }
          if (document!.isClosed || document!.version !== version) { throw new Error('O HTML mudou durante a preparação. Execute a geração novamente.'); }
          await writeOutput(base, target, key, files, () => {
            if (token.isCancellationRequested) { throw new CancelledError(); }
            if (document!.isClosed || document!.version !== version) { throw new Error('O HTML mudou durante a preparação. Execute a geração novamente.'); }
            checkDirtyOutput();
          });
          output.appendLine(`Saída: ${target}`);
          if (!quiet) {
            void vscode.window.showInformationMessage(`Interface LVGL gerada em ${path.relative(base, target)}.`);
            await vscode.window.showTextDocument(vscode.Uri.file(path.join(target, 'ui_generated.c')), { preview: true, viewColumn: vscode.ViewColumn.Beside });
          }
        } else if (!quiet) {
          void vscode.window.showInformationMessage(result.diagnostics.length ? `Validação concluída com ${result.diagnostics.length} aviso(s). Consulte Problemas.` : 'Interface válida para a configuração selecionada.');
        }
        return result;
      });
    } finally { busy.delete(key); }
  }
  const guarded = (action: 'validate' | 'generate') => async (uri?: vscode.Uri) => {
    try { return await run(action, uri); } catch (error) {
      if (!(error instanceof CancelledError)) { output.appendLine(`ERRO: ${(error as Error).message}`); void vscode.window.showErrorMessage(`TCC UI: ${(error as Error).message}`); }
      return undefined;
    }
  };
  context.subscriptions.push(
    vscode.commands.registerCommand('tccUiTranslator.generate', guarded('generate')),
    vscode.commands.registerCommand('tccUiTranslator.validate', guarded('validate')),
    vscode.commands.registerCommand('tccUiTranslator.createExample', async () => {
      try {
        const content = await fs.readFile(context.asAbsolutePath('resources/contador.html'), 'utf8');
        const document = await vscode.workspace.openTextDocument({ language: 'html', content });
        await vscode.window.showTextDocument(document);
        return document;
      } catch (error) { void vscode.window.showErrorMessage(`Não foi possível abrir o exemplo: ${(error as Error).message}`); return undefined; }
    }),
    vscode.commands.registerCommand('tccUiTranslator.openLanguageGuide', async () => {
      const uri = vscode.Uri.file(context.asAbsolutePath('resources/LANGUAGE_GUIDE.md'));
      await vscode.commands.executeCommand('markdown.showPreview', uri);
      return uri;
    }),
  );
  return { run, diagnostics, extensionMode: context.extensionMode };
}
export function deactivate(): void { busy.clear(); }
