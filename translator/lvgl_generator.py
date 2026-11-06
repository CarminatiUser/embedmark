"""Geração determinística de C para LVGL 8.3; nomes internos independem dos IDs."""

import math

from translator.color_utils import ColorConverter
from translator.config import LVGL_COORD_MAX
from translator.fonts import FontCatalog


class StyleCache:
    def __init__(self):
        self.styles = {}
        self.style_defs = {}

    def get_or_create_style(self, config):
        if not config:
            return ""
        key = tuple(sorted(config.items()))
        if key not in self.styles:
            name = f"ui_style_{len(self.styles)}"
            self.styles[key] = name
            self.style_defs[name] = dict(config)
        return self.styles[key]

    def get_all_styles(self):
        return self.style_defs


class LVGLCodeGenerator:
    def __init__(self, viewport_width, viewport_height, font_catalog=None):
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.style_cache = StyleCache()
        self.generated_count = 0
        self.font_catalog = font_catalog or FontCatalog.builtin()
        self.bindings = []
        self.used_fonts = set()

    @staticmethod
    def _escape_c_string(text):
        # Octal de três dígitos impede que o próximo caractere estenda o escape.
        result = []
        for byte in str(text).encode("utf-8"):
            if byte == 0:
                raise ValueError("Texto não pode conter NUL.")
            # Escapar '?' também impede trigraphs C99 (por exemplo, ??/).
            if byte in (34, 63, 92):
                result.append("\\" + chr(byte))
            elif 32 <= byte <= 126:
                result.append(chr(byte))
            else:
                result.append(f"\\{byte:03o}")
        return "".join(result)

    @staticmethod
    def _int_value(value, default=0):
        if value is None:
            return default
        value = float(value)
        if not math.isfinite(value) or abs(value) > LVGL_COORD_MAX:
            raise ValueError("Valor fora do intervalo LVGL suportado.")
        return int(round(value))

    @staticmethod
    def _count_elements(elements):
        return sum(1 + LVGLCodeGenerator._count_elements(e.get("children", [])) for e in elements)

    @staticmethod
    def generate_color_declaration(color):
        return f"lv_color_hex({ColorConverter.to_lvgl(color)})"

    def extract_style_config(self, element):
        props = element.get("computed", {})
        config = {
            key: props[key]
            for key in (
                "bg_color",
                "color",
                "opacity",
                "border_radius",
                "border_color",
                "border_width",
                "padding_left",
                "padding_right",
                "padding_top",
                "padding_bottom",
            )
            if props.get(key) is not None
        }
        # Canonicalização evita estilos distintos para cores equivalentes.
        for key in ("bg_color", "color", "border_color"):
            if key in config:
                config[key] = ColorConverter.normalize(config[key])
        return config, props

    def _collect_styles(self, elements):
        for element in elements:
            config, _ = self.extract_style_config(element)
            self.style_cache.get_or_create_style(config)
            self._collect_styles(element.get("children", []))

    def generate_style_definitions(self):
        styles = self.style_cache.get_all_styles()
        lines = [f"static lv_style_t {name};" for name in styles]
        lines += [
            "",
            "static void ui_init_styles(void)",
            "{",
            "    static bool initialized = false;",
            "    if (initialized) return;",
            "    initialized = true;",
        ]
        for name, style in styles.items():
            lines.append(f"    lv_style_init(&{name});")
            for key, setter in (("bg_color", "bg_color"), ("color", "text_color"), ("border_color", "border_color")):
                if key in style:
                    lines.append(f"    lv_style_set_{setter}(&{name}, {self.generate_color_declaration(style[key])});")
            opa = "LV_OPA_COVER" if "bg_color" in style else "LV_OPA_TRANSP"
            lines.append(f"    lv_style_set_bg_opa(&{name}, {opa});")
            opacity = float(style.get("opacity", 1))
            if not 0 <= opacity <= 1:
                raise ValueError("Opacidade deve estar entre 0 e 1.")
            lines.append(f"    lv_style_set_opa(&{name}, {round(opacity * 255)});")
            for key, setter in (
                ("border_width", "border_width"),
                ("border_radius", "radius"),
                *((f"padding_{s}", f"pad_{s}") for s in ("left", "right", "top", "bottom")),
            ):
                value = self._int_value(style.get(key, 0))
                lines.append(f"    lv_style_set_{setter}(&{name}, {value});")
        return "\n".join([*lines, "}"])

    def _add_common_object_config(self, lines, var, props, indent, style_name="", is_container_like=False):
        # Remover o tema torna defaults e espaçamentos independentes do tema da aplicação.
        lines.append(f"{indent}lv_obj_remove_style_all({var});")
        if style_name:
            lines.append(f"{indent}lv_obj_add_style({var}, &{style_name}, 0);")
        if is_container_like:
            lines.append(f"{indent}lv_obj_set_size({var}, LV_PCT(100), LV_PCT(100));")
            lines.append(f"{indent}lv_obj_clear_flag({var}, LV_OBJ_FLAG_SCROLLABLE);")
            lines.append(f"{indent}lv_obj_set_scrollbar_mode({var}, LV_SCROLLBAR_MODE_OFF);")
        for axis in ("width", "height"):
            if props.get(axis) is not None:
                lines.append(f"{indent}lv_obj_set_{axis}({var}, {self._int_value(props[axis])});")
        lines.append(
            f"{indent}lv_obj_set_pos({var}, {self._int_value(props.get('left', 0))}, {self._int_value(props.get('top', 0))});"
        )
        if props.get("hidden"):
            lines.append(f"{indent}lv_obj_add_flag({var}, LV_OBJ_FLAG_HIDDEN);")

    def _add_label_config(self, lines, var, props, indent):
        font = props.get("font", "lv_font_montserrat_14")
        self.font_catalog.describe(font)
        self.used_fonts.add(font)
        lines.append(f"{indent}lv_obj_set_style_text_font({var}, &{font}, 0);")
        if props.get("width") is not None:
            lines.append(f"{indent}lv_label_set_long_mode({var}, LV_LABEL_LONG_WRAP);")
        align = props.get("text_align", "left")
        if align not in {"left", "center", "right"}:
            raise ValueError("Alinhamento de texto inválido.")
        lines.append(f"{indent}lv_obj_set_style_text_align({var}, LV_TEXT_ALIGN_{align.upper()}, 0);")

    def generate_element_creation(self, element, parent_var="scr", indent="    "):
        self.generated_count += 1
        var = f"ui_node_{self.generated_count}"
        kind = element["type"]
        creators = {
            "label": "lv_label_create",
            "button": "lv_btn_create",
            "div": "lv_obj_create",
            "container": "lv_obj_create",
            "screen": "lv_obj_create",
        }
        if kind not in creators:
            raise ValueError(f"Elemento não suportado: {kind}.")
        config, props = self.extract_style_config(element)
        style = self.style_cache.get_or_create_style(config)
        lines = [f"{indent}lv_obj_t *{var} = {creators[kind]}({parent_var});"]
        if element.get("id") is not None:
            index = len(self.bindings)
            self.bindings.append((element["id"], var))
            lines.extend(
                [
                    f"{indent}ui_objects[{index}].object = {var};",
                    f"{indent}lv_obj_add_event_cb({var}, ui_forget_object, LV_EVENT_DELETE, &ui_objects[{index}]);",
                ]
            )
        self._add_common_object_config(lines, var, props, indent, style, kind != "label")
        if kind == "label":
            lines.append(f'{indent}lv_label_set_text({var}, "{self._escape_c_string(element.get("text", ""))}");')
            self._add_label_config(lines, var, props, indent)
        children = element.get("children", [])
        # Compatibilidade com árvores antigas que guardavam apenas texto no botão.
        if kind == "button" and not children and element.get("text"):
            children = [
                {
                    "type": "label",
                    "text": element["text"],
                    "computed": {k: props[k] for k in ("font", "text_align") if k in props},
                    "children": [],
                }
            ]
        for child in children:
            child_var = f"ui_node_{self.generated_count + 1}"
            lines.append(self.generate_element_creation(child, var, indent))
            if kind == "button" and child["type"] == "label" and not child.get("computed", {}).get("position_explicit"):
                lines.append(f"{indent}lv_obj_center({child_var});")
        return "\n".join(lines)

    def generate_registry(self):
        # Uma sentinela mantém a tabela válida inclusive em interfaces sem IDs.
        lines = [
            "static lv_obj_t *ui_root = NULL;",
            "typedef struct { const char *id; lv_obj_t *object; } ui_binding_t;",
            "static ui_binding_t ui_objects[] = {",
            *[f'    {{"{self._escape_c_string(name)}", NULL}},' for name, _ in self.bindings],
            "    {NULL, NULL}",
            "};",
        ]
        if any(var != "scr" for _, var in self.bindings):
            lines.append("""
static void ui_forget_object(lv_event_t *event)
{
    ui_binding_t *binding = lv_event_get_user_data(event);
    if (binding->object == lv_event_get_target(event)) binding->object = NULL;
}
""")
        lines.append("""
static void ui_forget_screen(lv_event_t *event)
{
    if (ui_root != lv_event_get_target(event)) return;
    ui_root = NULL;
    for (size_t i = 0; ui_objects[i].id != NULL; ++i) ui_objects[i].object = NULL;
}

lv_obj_t *screen_main_get(void)
{
    return ui_root;
}

lv_obj_t *screen_main_get_object(const char *id)
{
    if (ui_root == NULL || id == NULL) return NULL;
    for (size_t i = 0; ui_objects[i].id != NULL; ++i) {
        if (strcmp(ui_objects[i].id, id) == 0) return ui_objects[i].object;
    }
    return NULL;
}

bool screen_main_destroy(void)
{
    if (ui_root == NULL) return true;
    lv_disp_t *display = lv_obj_get_disp(ui_root);
    /* LVGL precisa de uma tela ativa; transições devem terminar primeiro. */
    if (lv_disp_get_scr_act(display) == ui_root ||
        lv_disp_get_scr_prev(display) == ui_root || lv_anim_get(ui_root, NULL) != NULL) return false;
    lv_obj_del(ui_root);
    return true;
}
""")
        return "\n".join(lines)

    def generate_complete_code(self, elements, design_info):
        if design_info["width"] <= 0 or design_info["height"] <= 0:
            raise ValueError("Dimensões do projeto devem ser positivas.")
        self.style_cache = StyleCache()
        self.generated_count = 0
        self.bindings = [(design_info["id"], "scr")] if design_info.get("id") is not None else []
        self.used_fonts = set()
        self._collect_styles(elements)
        # Gerar elementos antes das definições também cobre labels sintéticos.
        body = [self.generate_element_creation(e) for e in elements]
        fonts = sorted(
            (self.font_catalog.describe(symbol) for symbol in self.used_fonts), key=lambda item: item["size"]
        )
        lines = [
            "/* Gerado por EmbedMark. API alvo: LVGL 8.3. */",
            '#include "lvgl.h"',
            "#include <stdbool.h>",
            "#include <stddef.h>",
            "#include <string.h>",
            "",
            "#if LVGL_VERSION_MAJOR != 8 || LVGL_VERSION_MINOR != 3",
            '#error "Esta saída requer LVGL 8.3.x"',
            "#endif",
        ]
        for font in fonts:
            if self.font_catalog.is_builtin:
                size = font["size"]
                lines += [
                    f"#if !LV_FONT_MONTSERRAT_{size}",
                    f'#error "Habilite LV_FONT_MONTSERRAT_{size} na configuração LVGL"',
                    "#endif",
                ]
            else:
                lines += [f"LV_FONT_DECLARE({font['symbol']});"]
        lines += [
            "",
            self.generate_registry(),
            self.generate_style_definitions(),
            "",
            "lv_obj_t *screen_main_create(void)",
            "{",
            "    if (ui_root != NULL) {",
            "        lv_disp_t *display = lv_obj_get_disp(ui_root);",
            "        if (lv_disp_get_scr_act(display) == ui_root) return ui_root;",
            "        if (lv_disp_get_scr_prev(display) == ui_root || lv_anim_get(ui_root, NULL) != NULL) return NULL;",
            "        lv_scr_load(ui_root);",
            "        return ui_root;",
            "    }",
            "    if (lv_disp_get_default() == NULL) return NULL;",
            "    ui_init_styles();",
            "    lv_obj_t *scr = lv_obj_create(NULL);",
            "    ui_root = scr;",
            "    lv_obj_add_event_cb(scr, ui_forget_screen, LV_EVENT_DELETE, NULL);",
            *(["    ui_objects[0].object = scr;"] if design_info.get("id") is not None else []),
            "    lv_obj_remove_style_all(scr);",
            f"    lv_obj_set_size(scr, {self.viewport_width}, {self.viewport_height});",
            "    lv_obj_set_style_bg_color(scr, lv_color_hex(0x000000), 0);",
            "    lv_obj_set_style_bg_opa(scr, LV_OPA_COVER, 0);",
            "    lv_obj_clear_flag(scr, LV_OBJ_FLAG_SCROLLABLE);",
            *body,
            "    lv_scr_load(scr);",
            "    return ui_root;",
            "}",
            "",
            f"/* Design: {design_info['width']}x{design_info['height']}; display: {self.viewport_width}x{self.viewport_height}. */",
            f"/* Objetos gerados (sem a raiz): {self.generated_count}. */",
            "",
        ]
        return "\n".join(lines)

    @staticmethod
    def generate_header():
        return """#ifndef EMBEDMARK_UI_GENERATED_H
#define EMBEDMARK_UI_GENERATED_H
#include "lvgl.h"
#include <stdbool.h>
#ifdef __cplusplus
extern "C" {
#endif
/* Todas as chamadas exigem o contexto/proteção de acesso do LVGL. */
/* Cria e carrega uma vez; repetições reutilizam a tela. NULL sem display ou em transição. */
lv_obj_t *screen_main_create(void);
lv_obj_t *screen_main_get(void);
/* NULL para ID desconhecido, objeto removido ou tela ainda não criada. */
lv_obj_t *screen_main_get_object(const char *id);
/* Carregue outra tela antes. false enquanto ativa, em transição ou animada. */
bool screen_main_destroy(void);
#ifdef __cplusplus
}
#endif
#endif
"""
