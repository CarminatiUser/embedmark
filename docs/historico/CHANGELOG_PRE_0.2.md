# CHANGELOG

## v2.0.0 - Architecture Evolution (2026-05-25)

### 🎨 Arquitetura Redesenhada

- ✅ Modularização completa (1 arquivo → 10 módulos)
- ✅ Separação clara de responsabilidades
- ✅ Pipeline estruturado e escalável

### 🔄 Sistema de Viewport e Scaling

- ✅ Cálculo automático de scale factors
- ✅ Aplicação em posições e tamanhos
- ✅ Suporte a múltiplas resoluções de display
- ✅ Preservação de proporções

### 🔤 Tipografia

- ✅ Mapeamento automático para fontes LVGL
- ✅ Fallback para fontes próximas
- ✅ 14 tamanhos de fonte suportados
- ✅ Escalamento aplicado

### 🎨 Sistema de Cores

- ✅ Suporte a cores nomeadas CSS (25+)
- ✅ Conversão RGB → Hex
- ✅ Conversão Hex → LVGL
- ✅ Validação e normalização

### ♻️ Otimização de Estilos

- ✅ Cache com deduplicação
- ✅ Hash-based style matching
- ✅ Redução de código gerado
- ✅ Reutilização automática

### 📊 Parser CSS

- ✅ Suporte a shorthands (padding, margin)
- ✅ Normalização de valores
- ✅ Remoção de unidades
- ✅ Validação de propriedades

### 🌳 Parser HTML

- ✅ Suporte a hierarquia
- ✅ Preservação de estrutura
- ✅ Validação de elementos
- ✅ Extração de attributes

### 🧠 Layout Engine

- ✅ Cálculo centralizado
- ✅ Aplicação de scaling
- ✅ Normalização de cores
- ✅ Mapeamento de fontes

### 🛠️ Gerador LVGL

- ✅ Geração otimizada
- ✅ Função `init_styles()` centralizada
- ✅ Reutilização de estilos
- ✅ Código legível e bem estruturado

### 💾 Sistema de Configuração

- ✅ Presets de display (ST7789, ST7735, ILI9341, SSD1306)
- ✅ Suporte a orientação (portrait, landscape)
- ✅ Configuração centralizada
- ✅ Extensível para novos displays

### 🔍 Debug e Logging

- ✅ Logging estruturado
- ✅ Visualização de pipeline
- ✅ Debug detalhado
- ✅ Relatórios de coordenadas

### 🖥️ CLI Completa

- ✅ Interface de linha de comando
- ✅ Múltiplas opções
- ✅ Help detalhado
- ✅ Análise e validação integrada

### 🧪 Utilitários

- ✅ Validação HTML/CSS
- ✅ Análise de código
- ✅ Estimativa de performance
- ✅ Estimativa de RAM/ROM

### 📚 Documentação

- ✅ README.md completo
- ✅ ARCHITECTURE.md detalhado
- ✅ ESP_IDF_INTEGRATION.md prático
- ✅ IMPROVEMENTS.md de mudanças
- ✅ Comentários nos módulos
- ✅ Exemplos HTML

---

## v1.0.0 - Initial MVP (Baseline)

### Funcionalidades Básicas

- Parse HTML/CSS simplificado
- Geração LVGL básica
- Sem scaling
- Sem otimizações

---

## Roadmap Futuro

### v2.1.0 - Planned

- [ ] Flexbox mais completo
- [ ] Media queries simplificadas
- [ ] Suporte a `display:none`
- [ ] Variables CSS (`--var-name`)

### v2.2.0 - Future

- [ ] Suporte a imagens/SVG
- [ ] Animações CSS básicas
- [ ] Temas dinâmicos (light/dark)
- [ ] Web Components simplificados

### v3.0.0 - Long Term

- [ ] Compilação direta via ESP-IDF
- [ ] Live preview em browser
- [ ] Designer visual UI
- [ ] Hot reload durante desenvolvimento

---

## Estatísticas de Melhoria

|      Métrica     |  Antes |  Depois  |       Ganho      |
|------------------|--------|----------|------------------|
|     Arquivos     |   1    |    10    | 10x modularidade |
| Linhas de código |  ~200  |   ~2000  |   Mais features  |
| Propriedades CSS |   3    |    15+   |   5x cobertura   |
|  Cores nomeadas  |   5    |    25+   |     5x cores     |
|   Escalamento    |   ❌   |    ✅    | Viewport correto |
|    Fontes LVGL   |   ❌   |    ✅    |    14 tamanhos   |
|  Display presets |   1    |    4     |   Flexibilidade  |
|   Cache estilos  |   ❌   |    ✅    |     Otimizado    |
|        CLI       |   ❌   |    ✅    |  Produção ready  |
|   Documentação   | Mínima | Completa |    10x melhor    |

---

## Compatibilidade

### Requisitos Python
- Python 3.8+
- beautifulsoup4 >= 4.11.0
- tinycss2 >= 1.2.0

### Hardware Suportado
- ESP32 (ST7789) ✅ Tested
- ESP32 (ST7735) ✅ Preset
- Arduino (ST7735) ✅ Preset
- Generic (ILI9341) ✅ Preset
- Generic (SSD1306) ✅ Preset

### Compiladores
- ESP-IDF (primary)
- Arduino IDE (compatible)
- PlatformIO (compatible)

---

## Quebras de Compatibilidade

**Nenhuma!** O projeto é totalmente retrocompatível.

Código antigo:
```bash
python main.py  # Ainda funciona!
```

Novo código:
```bash
python cli.py sample_ui.html --analyze
```

---

## Créditos

Projeto acadêmico - TCC  
**Tema:** Metodologia para Prototipagem de Interfaces Gráficas Embarcadas a partir de Linguagens Web Simplificadas

---

## Licença

MIT License - Livre para uso acadêmico e comercial

---

**Última atualização:** 2026-05-25
