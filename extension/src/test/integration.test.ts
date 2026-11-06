import { strict as assert } from 'node:assert';
import * as fs from 'node:fs/promises';
import * as path from 'node:path';
import * as vscode from 'vscode';
import { ExtensionApi } from '../extension';
export async function run(): Promise<void> {
  const manifest = JSON.parse(await fs.readFile(path.resolve(__dirname, '../../package.json'), 'utf8')) as { publisher: string; name: string };
  const extension = vscode.extensions.getExtension<ExtensionApi>(process.env.EMBEDMARK_TEST_EXTENSION_ID ?? `${manifest.publisher}.${manifest.name}`);
  assert.ok(extension, 'Development extension is discoverable');
  if (process.env.EMBEDMARK_EXPECT_INSTALLED_ROOT) {
    assert.equal(await fs.realpath(extension.extensionPath), await fs.realpath(process.env.EMBEDMARK_EXPECT_INSTALLED_ROOT), 'Tests activate the installed VSIX');
  }
  const api = await extension.activate(); const commands = await vscode.commands.getCommands(true);
  if (process.env.EMBEDMARK_EXPECT_INSTALLED_ROOT) { assert.equal(api.extensionMode, vscode.ExtensionMode.Production, 'Installed extension runs in production mode'); }
  for (const command of ['generate', 'validate', 'createExample', 'openLanguageGuide']) { assert.ok(commands.includes(`embedmark.${command}`)); }
  const example = await vscode.commands.executeCommand<vscode.TextDocument>('embedmark.createExample');
  assert.ok(example?.isUntitled); assert.match(example.getText(), /Contador de ações/);
  const guide = await vscode.commands.executeCommand<vscode.Uri>('embedmark.openLanguageGuide');
  assert.ok(guide); assert.match(await fs.readFile(guide.fsPath, 'utf8'), /screen/);
  if (process.env.EMBEDMARK_TEST_MODE === 'untrusted') {
    assert.equal(vscode.workspace.isTrusted, false, 'Untrusted profile remains restricted');
    await assert.rejects(api.run('validate', example.uri, true), /Confie nesta pasta/);
    console.log('PASS: restricted workspace blocks execution; example and guide work.'); return;
  }
  assert.equal(vscode.workspace.isTrusted, true);
  const roots = vscode.workspace.workspaceFolders!; assert.equal(roots.length, 2);
  const python = process.env.EMBEDMARK_TEST_PYTHON ?? (process.platform === 'win32' ? 'python' : 'python3');
  for (const folder of roots) { await vscode.workspace.getConfiguration('embedmark', folder.uri).update('pythonPath', python, vscode.ConfigurationTarget.WorkspaceFolder); }
  assert.equal((await api.run('validate', example.uri, true))?.ok, true, 'Untitled example validates with bundled fonts');
  const file = vscode.Uri.file(path.join(roots[0]!.uri.fsPath, 'tela ação.html')); await fs.writeFile(file.fsPath, example.getText());
  const document = await vscode.workspace.openTextDocument(file); await vscode.window.showTextDocument(document);
  assert.equal((await api.run('generate', file, true))?.ok, true);
  const output = path.join(roots[0]!.uri.fsPath, 'generated', 'tela ação');
  assert.match(await fs.readFile(path.join(output, 'ui_generated.c'), 'utf8'), /embedmark_sans_pt/);
  assert.equal(JSON.parse(await fs.readFile(path.join(output, '.embedmark-output.json'), 'utf8')).owner, 'embedmark');
  assert.ok((await fs.stat(path.join(output, 'OFL.txt'))).isFile());
  const firstCode = await fs.readFile(path.join(output, 'ui_generated.c'), 'utf8');
  const edit = new vscode.WorkspaceEdit();
  edit.replace(file, new vscode.Range(document.positionAt(0), document.positionAt(document.getText().length)), '<screen width="172" height="320"><label id="titulo">Texto atualizado</label></screen>');
  assert.equal(await vscode.workspace.applyEdit(edit), true); assert.equal(document.isDirty, true);
  assert.equal((await api.run('generate', file, true))?.ok, true, 'Generation uses current unsaved buffer');
  assert.notEqual(await fs.readFile(path.join(output, 'ui_generated.c'), 'utf8'), firstCode);
  const generatedUri = vscode.Uri.file(path.join(output, 'ui_generated.c'));
  const generatedDocument = await vscode.workspace.openTextDocument(generatedUri);
  const generatedEdit = new vscode.WorkspaceEdit(); generatedEdit.insert(generatedUri, new vscode.Position(0, 0), '// unsaved manual change\n');
  assert.equal(await vscode.workspace.applyEdit(generatedEdit), true);
  await assert.rejects(api.run('generate', file, true), /não salvas/);
  assert.equal(generatedDocument.isDirty, true);
  await vscode.window.showTextDocument(generatedDocument);
  await vscode.commands.executeCommand('workbench.action.files.revert');
  await fs.writeFile(path.join(output, 'ui_generated.c'), 'MANUAL');
  await assert.rejects(api.run('generate', file, true), /alterado/);
  assert.equal(await fs.readFile(path.join(output, 'ui_generated.c'), 'utf8'), 'MANUAL');
  const invalid = vscode.Uri.file(path.join(roots[0]!.uri.fsPath, 'invalid.html'));
  await fs.writeFile(invalid.fsPath, '<screen width="172" height="320">\n<div id="bad" style="display:flex">Texto</div>\n</screen>');
  assert.equal((await api.run('validate', invalid, true))?.ok, false);
  assert.ok((api.diagnostics.get(invalid)?.length ?? 0) > 0, 'Problems collection receives diagnostics');
  assert.ok(api.diagnostics.get(invalid)?.every(diagnostic => diagnostic.source === 'EmbedMark'), 'Problems identify the product as EmbedMark');
  assert.ok(api.diagnostics.get(invalid)?.some(diagnostic => diagnostic.range.start.line === 1), 'Diagnostic targets source line');
  const secondFile = vscode.Uri.file(path.join(roots[1]!.uri.fsPath, 'outra tela.html'));
  await fs.writeFile(secondFile.fsPath, '<screen width="172" height="320"><label id="texto">Olá</label></screen>');
  await vscode.workspace.getConfiguration('embedmark', secondFile).update('outputDirectory', 'saida/${fileBasenameNoExtension}', vscode.ConfigurationTarget.WorkspaceFolder);
  assert.equal((await api.run('generate', secondFile, true))?.ok, true);
  assert.ok((await fs.stat(path.join(roots[1]!.uri.fsPath, 'saida', 'outra tela', 'ui_generated.c'))).isFile());
  console.log('PASS: commands, guide, example, validation, generation, fonts, unsaved buffer, output protection, Problems and multi-root settings.');
}
