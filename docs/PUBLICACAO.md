# Pacote da extensão e publicação

O [repositório GitHub do EmbedMark](https://github.com/CarminatiUser/embedmark) disponibiliza código-fonte, documentação e exemplos **para consulta**, conforme a licença proprietária em [LICENSE](../LICENSE). Esta publicação não inclui pacotes instaláveis nem concede permissão de uso, modificação ou redistribuição do código original. As licenças dos componentes de terceiros permanecem preservadas.

Após a adoção do nome EmbedMark em 14/10/2026, a versão 0.4.0 é entregue como `release/embedmark-0.4.0.vsix`, acompanhada do pacote Python, hashes e registros de verificação. O envio ao Marketplace é uma etapa posterior; não foi feito automaticamente. Os registros de validação de 02/10/2026 conservam os nomes anteriores e não devem ser confundidos com verificações de um pacote reconstruído.

A pasta `release/` e seus artefatos são locais, ignorados pelo Git e ausentes deste repositório público. As instruções a seguir registram o procedimento técnico da entrega local; elas não alteram as permissões da licença.

## Instalar o pacote local

No VS Code, abra Extensions, use o menu de três pontos e escolha **Install from VSIX**. Selecione o arquivo da pasta `release`. Tenha Python 3.10 ou superior instalado; a extensão inclui as bibliotecas Python necessárias. Node.js, pip e ESP-IDF não são requisitos para usar a extensão já empacotada.

Abra uma pasta confiável e use **EmbedMark: Criar exemplo de contador**. Salve o HTML e execute **Validar interface** e **Gerar interface LVGL**. Se o Python não for encontrado, configure **EmbedMark: Python Path** com o caminho do executável, sem argumentos adicionais.

O ESP-IDF é necessário apenas para compilar/gravar um firmware. O laboratório da tela, `embedmark-validation`, é um projeto local separado, não incluído neste repositório e sem endereço público confirmado; seu próprio README documenta esse procedimento.

## Identidade do publicador

O manifesto utiliza `arthur-carminati` como **identificador proposto**, sem afirmar que a conta existe ou que está disponível. Antes do envio, entre na sua conta do Marketplace e confirme/crie o publicador. O campo `publisher` do pacote deve corresponder exatamente a essa conta.

Se o identificador escolhido for diferente, altere somente esse metadado e gere outro pacote:

```sh
cd extension
npm pkg set publisher=IDENTIFICADOR_REAL
npm run package
```

O código original mantém direitos reservados em `LICENSE`/`LICENSE.txt`; as licenças das dependências e das fontes estão incluídas. Nenhuma licença aberta foi aplicada ao código original. Os metadados Python e da extensão apontam para o repositório GitHub de consulta. A conta GitHub `CarminatiUser` e o identificador proposto do Marketplace `arthur-carminati` são identidades de serviços diferentes; uma não confirma a outra.

## Enviar ao Marketplace

Acesse o painel de gerenciamento de extensões da sua conta, selecione o publicador correto, crie uma extensão do VS Code e envie o `.vsix`. A documentação oficial descreve o [envio manual de um pacote VSIX e o cadastro do publicador](https://code.visualstudio.com/api/working-with-extensions/publishing-extension). A conta, a identidade do publicador e a aprovação do serviço não são verificadas pela compilação local.

## Reproduzir a distribuição

Para desenvolver/empacotar, use Python 3.10+ e Node.js 24 LTS. Na pasta raiz:

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
python tools/verify_release.py release/embedmark-0.4.0.vsix --python python3 --report release/embedmark-package-verification.json
```

Os testes do VS Code usam perfis e pastas temporários, sem instalar a extensão na configuração pessoal. O comando de verificação da instalação real do `.vsix` está em `tools/verify_installed_extension.cjs`.

## Limites dos resultados

A versão foi preparada e testada originalmente no macOS do autor. A matriz automatizada para Linux, Windows e macOS é executada no [GitHub Actions](https://github.com/CarminatiUser/embedmark/actions/workflows/tests.yml), com resultados vinculados ao commit verificado e ao ambiente de execução. Consulte [VALIDACAO_0.4.0.md](VALIDACAO_0.4.0.md) para os registros históricos das verificações locais. A validação física do display permanece no roteiro do laboratório.
