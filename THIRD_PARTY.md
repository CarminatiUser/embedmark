# Dependências e atribuições

O código original do TCC UI Translator tem direitos reservados conforme `LICENSE`. Isso não altera as licenças dos componentes abaixo.

| Componente incluído na extensão | Versão | Licença |
|---|---|---|
| Beautiful Soup | 4.15.0 | MIT |
| Soup Sieve | 2.10 | MIT |
| tinycss2 | 1.5.1 | BSD-3-Clause |
| typing_extensions | 4.16.0 | PSF, com termos históricos no arquivo original |
| webencodings | 0.6.1 | BSD-3-Clause |
| Fontes bitmap TCC Sans PT | Derivadas de Montserrat Medium 7.200 | SIL Open Font License 1.1 |

As cinco bibliotecas Python são distribuídas com seus arquivos originais de licença em `extension/bundled/python/*.dist-info/licenses`. `THIRD_PARTY_NOTICES.md`, dentro desse diretório, lista os caminhos completos. `BACKEND_MANIFEST.json` registra versões e hashes dos arquivos incluídos. A pasta é gerada por `tools/bundle_backend.py` usando `requirements-runtime.lock`.

Os direitos de Montserrat pertencem aos autores do projeto Montserrat. A fonte original e a licença estão em `tools/fonts`; as fontes bitmap derivadas e `OFL.txt` estão em `examples/fonts` e na extensão. A geração usa `lv_font_conv` 1.5.3 (MIT), com seu lockfile em `tools/fonts`; esse conversor não é incluído na extensão.

TypeScript, os tipos da API do VS Code, `vsce` e `@vscode/test-electron` são ferramentas de desenvolvimento. Seus pacotes e dependências constam de `extension/package-lock.json`; a distribuição da extensão não inclui `node_modules`.

O laboratório de hardware tem seu próprio [registro de dependências](../tcc-ui-validation/THIRD_PARTY.md), incluindo LVGL 8.3.11 (MIT) e o driver Espressif ST7789T (Apache-2.0).
