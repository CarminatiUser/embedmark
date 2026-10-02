> Registro histórico anterior à revisão de 28/09/2026. Para instalação, funcionalidades e limitações atuais, consulte [README](README.md) e [correções do núcleo](docs/CORRECOES_2026-09-28.md). As estimativas e declarações de conclusão abaixo não são resultados de validação.

# TCC UI Translator - Estrutura do Projeto

## 📂 Arquitetura de Arquivos

```
tcc-ui-translator/
├── README.md                    # Documentação principal
├── translator/
│   ├── main.py                 # Orquestrador principal do pipeline
│   ├── cli.py                  # Interface de linha de comando
│   │
│   ├── html_parser.py          # Parser HTML com hierarquia
│   ├── css_parser.py           # Parser CSS robusto
│   ├── layout_engine.py        # Engine de layout com scaling
│   ├── lvgl_generator.py       # Gerador de código LVGL
│   │
│   ├── color_utils.py          # Conversão de cores
│   ├── containers.py           # Gerenciamento de containers
│   ├── config.py               # Configuração e presets
│   ├── debug.py                # Logging e debug
│   ├── utils.py                # Utilitários diversos
│   │
│   ├── sample_ui.html          # Exemplo simples
│   ├── advanced_example.html   # Exemplo avançado
│   │
│   └── requirements.txt        # Dependências (a criar)
│
└── output/
    └── ui_generated.c          # Código C gerado
```

## 🔄 Pipeline de Processamento

```
HTML Input (sample_ui.html)
    │
    ├─ extract <style> tag
    │
    ├─→ HTMLParser.parse()
    │   - Converte em AST
    │   - Mantém hierarquia
    │   - Extrai IDs e texto
    │   └─→ {width, height, elements[]}
    │
    ├─→ CSSParser.parse_stylesheet()
    │   - Parse CSS com tinycss2
    │   - Normaliza valores
    │   - Expande shorthands
    │   └─→ {elem_id: {prop: value}}
    │
    ├─→ ViewportConfig (scaling)
    │   - Design: 240×430 px
    │   - Display: 172×320 px (ou outro)
    │   - Calcula scale_x = 0.7167, scale_y = 0.7442
    │   └─→ Scale factors
    │
    ├─→ LayoutEngine.compute_layout()
    │   - Aplica scaling a posições/tamanhos
    │   - Mapeia fontes LVGL
    │   - Normaliza cores
    │   - Preserva hierarquia
    │   └─→ computed_elements with final coords
    │
    ├─→ LVGLCodeGenerator
    │   ├─ _collect_styles()  → StyleCache
    │   ├─ generate_style_definitions()
    │   ├─ generate_element_creation()
    │   ├─ generate_main_function()
    │   └─→ generate_complete_code()
    │
    └─→ C Output (ui_generated.c)
        - #include "lvgl.h"
        - init_styles() function
        - screen_main_create() function
        - Compilável com ESP-IDF
```

## 📊 Classes Principais

### `HTMLParser`
- `parse(html_text)` → AST dict com hierarquia
- Suporta: screen, label, button, div
- Valida estrutura

### `CSSParser`
- `parse_stylesheet(css_text)` → estilos por ID
- Suporta: posição, cor, tipografia, borders, espaçamento
- Normaliza valores numéricos

### `ViewportConfig`
- Configura design vs display resolution
- `scale_position(x, y)` → (scaled_x, scaled_y)
- `scale_size(w, h)` → (scaled_w, scaled_h)

### `FontMapper`
- Mapeia tamanho para font LVGL
- Fallback automático para próxima disponível

### `LayoutEngine`
- `compute_layout(element, styles)` → elemento com coordenadas finais
- Aplica scaling
- Calcula fontes
- Normaliza cores

### `StyleCache`
- Cache de estilos para evitar duplicatas
- Hash-based deduplication
- Retorna nome único por estilo

### `LVGLCodeGenerator`
- Geração de C code
- Criação de objetos LVGL
- Definição de estilos
- Hierarquia de objetos

### `DisplayPresets`
- Presets para displays comuns
- ST7789, ST7735, ILI9341, SSD1306
- Suporte a orientação portrait/landscape

## 🎯 Fluxo de Uso Principal

```python
# 1. Criar tradutor
from config import TranslationConfig
from main import UITranslator

config = TranslationConfig(
    design_width=240,
    design_height=430,
    display_preset="st7789",
)

translator = UITranslator(config)

# 2. Traduzir
success = translator.translate_file(
    "sample_ui.html",
    "../output/ui_generated.c"
)
```

## 📝 Uso CLI

```bash
# Tradução básica
python cli.py sample_ui.html

# Com display específico
python cli.py sample_ui.html -d st7735

# Com análise
python cli.py sample_ui.html --analyze --check-perf

# Modo silencioso
python cli.py sample_ui.html -q

# Exportar JSON intermediário
python cli.py sample_ui.html --export-json ast.json

# Listar displays
python cli.py --list-displays
```

## 🔧 Extensibilidade

### Adicionar novo display preset
```python
# Em config.py
DisplayPresets.DISPLAYS["novo_display"] = (width, height, "Nome")
```

### Adicionar nova cor nomeada
```python
# Em color_utils.py
ColorConverter.NAMED_COLORS["minha_cor"] = "#RRGGBB"
```

### Adicionar nova propriedade CSS
```python
# Em css_parser.py
CSSParser.SUPPORTED_PROPERTIES.add("nova_propriedade")

# Em layout_engine.py
# Adicionar processamento em compute_layout()
```

### Adicionar novo tipo de elemento
```python
# Em html_parser.py
HTMLParser.SUPPORTED_ELEMENTS.add("novo_elemento")

# Em lvgl_generator.py
# Adicionar caso em generate_element_creation()
```

## 📈 Melhorias Implementadas

✅ **Arquitetura Modular** - Separação clara de responsabilidades  
✅ **Viewport Real** - Scaling automático design → display  
✅ **Font Mapping** - Mapeamento LVGL automático  
✅ **Color System** - Suporte a hex, rgb, nomes CSS  
✅ **Style Cache** - Reuso de estilos  
✅ **Debug Logging** - Output detalhado do pipeline  
✅ **CLI Completa** - Interface de linha de comando  
✅ **Containers** - Suporte a hierarquia  
✅ **Performance** - Estimativas de RAM/ROM  
✅ **Presets** - Múltiplos displays  

## 📚 Documentação

- `README.md` - Guia completo
- Comentários em cada módulo
- Exemplos em `sample_ui.html` e `advanced_example.html`
- CLI help: `python cli.py -h`

## 🧪 Testes e Validação

```python
from utils import (
    HTMLValidator,
    CSSValidator,
    CodeAnalyzer,
    PerformanceMetrics,
)

# Validar
HTMLValidator.validate_structure(elements)
CSSValidator.validate_styles(styles)

# Analisar código
CodeAnalyzer.print_analysis(code)
PerformanceMetrics.check_performance(code)
```

## 🚀 Próximos Passos (Futuros)

- [ ] Flexbox mais completo
- [ ] Media queries
- [ ] Suporte a imagens
- [ ] Animações CSS
- [ ] Temas (light/dark)
- [ ] Preview em browser
- [ ] Otimização de código gerado
- [ ] Suporte a Web Components simplificado
