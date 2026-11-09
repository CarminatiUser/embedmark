# Pacote da extensão e publicação

O [repositório GitHub do EmbedMark](https://github.com/CarminatiUser/embedmark) disponibiliza o código-fonte da ferramenta **para consulta**, com licença proprietária. A extensão oficial distribuída pelo Marketplace pode ser instalada e usada gratuitamente. A permissão para usar o produto e as interfaces geradas está descrita em [LICENSE](../LICENSE); o núcleo e a extensão não receberam licença de código aberto. As licenças dos componentes de terceiros permanecem preservadas.

A versão atual é **0.4.1**, preparada em 09/11/2026. O publicador `arthur-carminati` foi confirmado no painel do Marketplace. O envio e a disponibilidade pública serão registrados após a validação do pacote pelo serviço.

Os pacotes e relatórios locais ficam em `release/`, ignorada pelo Git. Os registros da versão 0.4.0 e da adoção do nome EmbedMark em 14/10/2026 permanecem como histórico e não comprovam a validação de um pacote reconstruído.

## Instalar o pacote local

No VS Code, abra Extensions, use o menu de três pontos e escolha **Install from VSIX**. Selecione o arquivo da pasta `release`. Tenha Python 3.10 ou superior instalado; a extensão inclui as bibliotecas Python necessárias. Node.js, pip e ESP-IDF não são requisitos para usar a extensão já empacotada.

Abra uma pasta confiável e use **EmbedMark: Criar exemplo de contador**. Salve o HTML e execute **Validar interface** e **Gerar interface LVGL**. Se o Python não for encontrado, configure **EmbedMark: Python Path** com o caminho do executável, sem argumentos adicionais.

O ESP-IDF é necessário apenas para compilar/gravar um firmware. O laboratório da tela, `embedmark-validation`, é um projeto local separado, não incluído neste repositório e sem endereço público confirmado; seu próprio README documenta esse procedimento.

## Identidade do publicador

O publicador confirmado é **Arthur Carminati** (`arthur-carminati`), com acesso de proprietário verificado em 09/11/2026. O identificador completo é `arthur-carminati.embedmark`. A conta GitHub `CarminatiUser` e o publicador do Marketplace são identidades de serviços diferentes.

O campo `publisher` do manifesto e do VSIX deve permanecer igual ao publicador selecionado para o envio. `LICENSE` e `extension/LICENSE.txt` contêm os mesmos termos, e as licenças das dependências e fontes acompanham o pacote.

## Enviar ao Marketplace

Acesse o painel de gerenciamento de extensões da sua conta, selecione o publicador correto, crie uma extensão do VS Code e envie o `.vsix`. A documentação oficial descreve o [envio manual de um pacote VSIX e o cadastro do publicador](https://code.visualstudio.com/api/working-with-extensions/publishing-extension). A conta, a identidade do publicador e a aprovação do serviço não são verificadas pela compilação local.

## Reproduzir a distribuição

Este procedimento documenta a manutenção pelo titular, sem ampliar as permissões de consulta do código. Para desenvolver/empacotar, use Python 3.10+ e Node.js 24 LTS. Na pasta raiz:

```sh
python3 -m venv .venv
# macOS/Linux; no Windows: .venv\Scripts\activate
source .venv/bin/activate
python -m pip install -r requirements-dev.lock
python -m pip install -e .
python tools/bundle_backend.py
cd extension
npm ci
npm test
npm run test:integration
npm run package
```

O empacotamento recompila a extensão e reúne novamente o núcleo e as dependências verificadas por hash. A primeira preparação requer rede para obter essas dependências. A extensão instalada não usa a rede para traduzir interfaces.

De volta à pasta raiz do repositório, para verificar o conteúdo de um `.vsix` e executar o núcleo incluído sem pacotes Python do usuário:

```sh
python tools/verify_release.py release/embedmark-0.4.1.vsix --python python3 --report release/embedmark-package-verification.json
```

Os testes do VS Code usam perfis e pastas temporários, sem instalar a extensão na configuração pessoal. O comando de verificação da instalação real do `.vsix` está em `tools/verify_installed_extension.cjs`.

## Limites dos resultados

A versão foi preparada e testada originalmente no macOS do autor. A matriz automatizada para Linux, Windows e macOS é executada no [GitHub Actions](https://github.com/CarminatiUser/embedmark/actions/workflows/tests.yml), com resultados vinculados ao commit verificado e ao ambiente de execução. Consulte [VALIDACAO_0.4.0.md](VALIDACAO_0.4.0.md) para os registros históricos das verificações locais. A validação física do display permanece no roteiro do laboratório.
