import re

import pytest

from translator.color_utils import ColorConverter
from translator.config import TranslationConfig
from translator.css_parser import CSSParser
from translator.diagnostics import TranslationError
from translator.html_parser import HTMLParser
from translator.layout_engine import FontMapper, ViewportConfig
from translator.lvgl_generator import LVGLCodeGenerator
from translator.main import UITranslator


def translate(body='<label id="x">Texto</label>', css="", config=None):
    return UITranslator(config).translate(f'<screen width="100" height="100">{body}</screen><style>{css}</style>')


@pytest.mark.parametrize(
    "text,values", [("1", [1, 1, 1, 1]), ("1 2", [1, 2, 1, 2]), ("1 2 3", [1, 2, 3, 2]), ("1 2 3 4", [1, 2, 3, 4])]
)
@pytest.mark.parametrize("prefix", ["padding", "margin"])
def test_spacing_expansion(text, values, prefix):
    styles = CSSParser.parse_stylesheet(f"#x {{{prefix}: {text}}}")["x"]
    assert [styles[f"{prefix}-{s}"] for s in ("top", "right", "bottom", "left")] == values
    assert all(k.startswith(prefix) for k in styles)


def test_repeated_rules_and_shorthand_order():
    styles = CSSParser.parse_stylesheet("#x {color:red; padding:1 2;} #x {width:3; padding-left:4;}")["x"]
    assert styles == {
        "color": "#FF0000",
        "width": 3,
        "padding-top": 1,
        "padding-right": 2,
        "padding-bottom": 1,
        "padding-left": 4,
    }
    assert CSSParser.parse_stylesheet("#x {padding-left:4; padding:2;}")["x"]["padding-left"] == 2


def test_important_survives_later_normal_rule():
    assert CSSParser.parse_stylesheet("#x {color:red!important} #x {color:blue}")["x"]["color"] == "#FF0000"
    assert CSSParser.parse_stylesheet("#x {color:red!important} #x {color:blue!important}")["x"]["color"] == "#0000FF"


@pytest.mark.parametrize("value", ["-1px", "50%", "NaN", "inf", "1e999", "auto", "100000px"])
def test_invalid_width_has_diagnostic(value):
    with pytest.raises(TranslationError) as error:
        translate(css=f"#x {{width:{value}}}")
    assert any(d.code == "css.value" and d.element_id == "x" for d in error.value.diagnostics)


@pytest.mark.parametrize("value", [8192, -8192])
def test_lvgl_reserved_coordinate_values_rejected(value):
    with pytest.raises(TranslationError):
        translate(css=f"#x {{left:{value}}}")
    with pytest.raises(ValueError):
        TranslationConfig(display_preset="custom", display_width=abs(value), display_height=100)


def test_scaled_coordinate_outside_lvgl_range_rejected():
    with pytest.raises(TranslationError, match="8191"):
        translate(css="#x {top:3000}")


@pytest.mark.parametrize("value", ["#GGGGGG", "#12345", "rgb(999,0,0)", "rgb(-1,0,0)", "rgb(1,2,3)oops", "invalid"])
def test_invalid_colors_rejected(value):
    with pytest.raises(ValueError):
        ColorConverter.to_lvgl(value)


@pytest.mark.parametrize("value,expected", [("red", "0xFF0000"), ("#aB3", "0xAABB33"), ("rgb(1, 2, 255)", "0x0102FF")])
def test_colors(value, expected):
    assert ColorConverter.to_lvgl(value) == expected


def test_anonymous_parent_and_child_survive():
    code = translate('<div><label id="child">Preservado</label></div>').code
    assert "lv_obj_t *ui_node_1 = lv_obj_create(scr);" in code
    assert "lv_obj_t *ui_node_2 = lv_label_create(ui_node_1);" in code
    assert "Preservado" in code


def test_ids_never_become_c_identifiers():
    code = translate(
        "".join(f'<label id="{name}">x</label>' for name in ["1bad", "a-b", "a_b", "scr", "for", "ação"])
    ).code
    names = re.findall(r"lv_obj_t \*(\w+) = lv_\w+_create\(", code)
    assert len(names) == len(set(names)) == 7
    assert "lv_obj_t *1bad" not in code


def test_duplicate_ids_rejected():
    with pytest.raises(TranslationError, match="ID duplicado"):
        translate('<div id="a"><label id="a">x</label></div>')


def test_height_only_and_zero_dimensions_emitted():
    result = translate(css="#x {height:10; width:0;}")
    assert "lv_obj_set_height(ui_node_1, 32);" in result.code
    assert "lv_obj_set_width(ui_node_1, 0);" in result.code
    assert "lv_obj_set_height(ui_node_1, 32);" in translate(css="#x {height:10;}").code


def test_padding_scales_on_correct_axes_and_reaches_c():
    result = translate('<div id="x"><label>child</label></div>', "#x {padding:10px;}")
    computed = result.computed_layout[0]["computed"]
    assert computed["padding_left"] == 17
    assert computed["padding_top"] == 32
    assert "lv_style_set_pad_left(&ui_style_0, 17);" in result.code
    assert "lv_style_set_pad_top(&ui_style_0, 32);" in result.code


def test_margin_changes_position_without_changing_padding():
    result = translate(css="#x {left:10; top:10; margin-left:2; margin-top:3;}")
    computed = result.computed_layout[0]["computed"]
    assert (computed["left"], computed["top"]) == (20, 41)
    assert computed["padding_left"] == 0


def test_button_label_styles_and_text_preserved_once():
    result = translate(
        '<button id="b"><label id="t">Go</label></button>',
        "#b {color:red; font-size:10;} #t {color:blue; font-size:12; left:1;}",
    )
    assert result.code.count('"Go"') == 1
    assert len(result.computed_layout[0]["children"]) == 1
    assert result.computed_layout[0]["children"][0]["computed"]["color"] == "#0000FF"
    assert "lv_obj_center(ui_node_2)" not in result.code


def test_direct_button_text_centered_and_typography_inherited():
    result = translate('<button id="b">Go</button>', "#b {color:red; font-size:10;}")
    assert "lv_obj_center(ui_node_2);" in result.code
    assert result.computed_layout[0]["children"][0]["computed"]["font_size"] == 32


def test_border_and_display():
    result = translate(css="#x {border:2px solid red; display:none;}")
    assert result.computed_layout[0]["computed"]["border_width"] == 6
    assert "lv_style_set_border_color(&ui_style_0, lv_color_hex(0xFF0000));" in result.code
    assert "lv_obj_add_flag(ui_node_1, LV_OBJ_FLAG_HIDDEN);" in result.code


def test_multiple_style_blocks_preserve_source_locations():
    html = '<screen><label id="x">x</label></screen>\n<style>#x {color:red}</style>\n<style>\n#x {width:abc}\n</style>'
    with pytest.raises(TranslationError) as error:
        UITranslator().translate(html)
    assert error.value.diagnostics[-1].line == 4
    result = UITranslator().translate(html.replace("abc", "50"))
    assert result.styles["x"] == {"color": "#FF0000", "width": 50}


def test_config_overrides_design_and_custom_orientation_roundtrip():
    config = TranslationConfig(
        design_width=200,
        design_height=400,
        display_preset="custom",
        display_width=300,
        display_height=500,
        orientation="landscape",
    )
    result = translate(config=config)
    assert result.ast["width"] == 200
    assert result.display == {"width": 500, "height": 300}
    assert TranslationConfig.from_dict(config.to_dict()).to_dict() == config.to_dict()
    assert TranslationConfig.from_dict(TranslationConfig().to_dict()).to_dict() == TranslationConfig().to_dict()


@pytest.mark.parametrize(
    "kwargs",
    [
        {"display_preset": "typo"},
        {"display_preset": "custom"},
        {"design_width": 0},
        {"design_height": -1},
        {"orientation": "upside"},
        {"display_width": 100},
        {"design_width": float("nan")},
    ],
)
def test_invalid_configuration(kwargs):
    with pytest.raises(ValueError):
        TranslationConfig(**kwargs)


@pytest.mark.parametrize(
    "html", ["", "<screen/><screen/>", '<screen width="0"/>', '<screen height="-1"/>', '<screen width="NaN"/>']
)
def test_invalid_screen(html):
    with pytest.raises(TranslationError):
        HTMLParser.parse(html)


def test_unknown_inputs_are_reported_and_strict_rejects():
    result = translate('<span>não suportado</span><label id="x">x</label>', "#x {font-weight:bold;} .a {color:red;}")
    assert {d.code for d in result.diagnostics} >= {"html.element", "css.unsupported", "css.selector"}
    with pytest.raises(TranslationError, match="Modo estrito"):
        translate(css="#x {font-weight:bold;}", config=TranslationConfig(strict=True))


def test_direct_screen_text_is_diagnosed_but_comments_are_ignored():
    result = translate("Texto solto<label>Visivel</label>")
    assert any(d.code == "html.text" for d in result.diagnostics)
    assert not translate("<!-- comentario -->\n<label>Visivel</label>").diagnostics
    with pytest.raises(TranslationError, match="Modo estrito"):
        translate("Texto solto", config=TranslationConfig(strict=True))


def test_generator_reuse_is_deterministic():
    result = translate()
    generator = LVGLCodeGenerator(172, 320)
    first = generator.generate_complete_code(result.computed_layout, result.ast)
    assert generator.generate_complete_code(result.computed_layout, result.ast) == first


def test_analysis_counts_objects_without_counting_registry_and_api_pointers():
    from translator.utils import CodeAnalyzer

    result = translate('<div id="container"><button id="button">Go</button></div>')
    assert CodeAnalyzer.count_objects(result.code) == 4


def test_strings_preserve_utf8_and_control_bytes():
    assert LVGLCodeGenerator._escape_c_string('A\r\t"\\é') == 'A\\015\\011\\"\\\\\\303\\251'
    with pytest.raises(ValueError, match="NUL"):
        LVGLCodeGenerator._escape_c_string("a\0b")


def test_font_rounding_and_invalid_viewport():
    assert FontMapper.get_font(21) == "lv_font_montserrat_22"
    assert FontMapper.get_font(21.8) == "lv_font_montserrat_22"
    with pytest.raises(ValueError):
        ViewportConfig(0, 100)


def test_font_coverage_warning_preserves_text():
    result = translate('<label id="x">Ação</label>')
    assert any(d.code == "font.glyphs" for d in result.diagnostics)
    assert result.ast["elements"][0]["text"] == "Ação"
    assert "\\303\\247" in result.code


def test_all_valid_official_examples_have_no_diagnostics():
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    paths = [*root.glob("translator/*.html"), *sorted(root.glob("examples/0[123]*.html"))]
    assert len(paths) == 5
    for path in paths:
        result = UITranslator(TranslationConfig(strict=True)).translate(path.read_text())
        assert result.diagnostics == [], path.name


def test_bad_example_is_rejected():
    from pathlib import Path

    path = Path(__file__).resolve().parents[1] / "examples/04_erros.html"
    with pytest.raises(TranslationError):
        UITranslator().translate(path.read_text())


def test_css_syntax_error_and_unsupported_selector():
    with pytest.raises(TranslationError):
        CSSParser.parse_stylesheet("#x {width}")
    diagnostics = []
    assert CSSParser.parse_stylesheet("#x label {color:red}", diagnostics) == {}
    assert diagnostics[0].code == "css.selector"


def test_same_style_deduplicates_and_initializes_once():
    result = translate('<label id="a">a</label><label id="b">b</label>', "#a {color:red} #b {color:#f00}")
    assert result.code.count("static lv_style_t") == 1
    assert "if (initialized) return;" in result.code


def test_overflow_cannot_generate_out_of_range_coordinates():
    with pytest.raises(TranslationError):
        translate(css="#x {left:32767}")


def test_style_opening_tag_quotes_and_carriage_return_keep_css_locations():
    html = '<screen>\r<label id="x">x</label></screen>\n<style data-note="a > b">\n#x {width:no}\n</style>'
    with pytest.raises(TranslationError) as caught:
        UITranslator().translate(html)
    diagnostic = caught.value.diagnostics[-1]
    assert diagnostic.code == "css.value" and (diagnostic.line, diagnostic.column) == (3, 5)


def test_css_ignored_margin_and_unmatched_selector_have_locations():
    result = translate(css="\n#x {margin-right:3;}\n#missing {color:red}")
    margin = next(d for d in result.diagnostics if d.code == "css.margin")
    unmatched = next(d for d in result.diagnostics if d.code == "css.unmatched_id")
    assert (margin.line, margin.column) == (2, 5)
    assert (unmatched.line, unmatched.column) == (3, 1)


def test_deep_nesting_is_diagnosed_without_python_traceback():
    html = "<screen>" + "<div>" * 150 + "</div>" * 150 + "</screen>"
    with pytest.raises(TranslationError) as caught:
        UITranslator().translate(html)
    assert caught.value.diagnostics[0].code == "html.nesting"


def test_source_nul_and_non_string_are_diagnosed():
    for source, code in ((None, "html.source"), ("<screen>\n<label>a\0b</label></screen>", "html.nul")):
        with pytest.raises(TranslationError) as caught:
            UITranslator().translate(source)
        assert caught.value.diagnostics[0].code == code


def test_layout_overflow_points_to_responsible_component():
    html = '<screen width="1" height="1">\n  <label id="x">x</label></screen><style>#x {left:100}</style>'
    with pytest.raises(TranslationError) as caught:
        UITranslator().translate(html)
    diagnostic = caught.value.diagnostics[-1]
    assert (diagnostic.line, diagnostic.column, diagnostic.element_id) == (2, 3, "x")


@pytest.mark.parametrize("kwargs", [{"strict": "false"}, {"verbose": 1}, {"display_preset": []}, {"orientation": []}])
def test_configuration_rejects_incorrect_json_types(kwargs):
    with pytest.raises(ValueError):
        TranslationConfig(**kwargs)


def test_legacy_helpers_do_not_silently_invent_flexbox_or_dimensions():
    from copy import deepcopy
    from translator.containers import ContainerManager, SimplexFlexbox

    element = {"type": "div", "children": [{"type": "label", "text": "x"}]}
    original = deepcopy(element)
    with pytest.raises(ValueError, match="Flexbox não está implementado"):
        SimplexFlexbox.apply_flexbox(element, justify_content="center")
    with pytest.raises(ValueError, match="Auto-sizing não está implementado"):
        ContainerManager.calculate_container_bounds(element, {})
    assert element == original
    assert ContainerManager.validate_hierarchy(element)
    assert not ContainerManager.validate_hierarchy({"type": "unknown"})
    assert not ContainerManager.validate_hierarchy({"type": "label", "children": [element]})
    assert not ContainerManager.validate_hierarchy({"type": "div", "children": [{"type": "screen"}]})
    assert ContainerManager.validate_hierarchy({"type": "button", "children": [element]})
