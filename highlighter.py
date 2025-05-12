import io
import tokenize
import keyword
import win32clipboard
import win32con
import os
import json
import builtins

# читаем конфиг
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config_colors = json.load(f)

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

# Цвета для tk.Text
TOKEN_TAGS = {
    name: {'foreground': color}
    for name, color in config_colors.items()
}

TOKEN_TYPE_TO_NAME = {
    tokenize.COMMENT: 'COMMENT',
    tokenize.STRING: 'STRING',
    tokenize.NUMBER: 'NUMBER',
    tokenize.OP: 'OP',
    tokenize.NAME: 'NAME',
}

BUILTIN_NAMES = set(dir(builtins))

def insert_highlighted_code(text_widget, code):
    text_widget.config(state="normal")
    text_widget.delete("1.0", "end")
    tokens = list(tokenize.generate_tokens(io.StringIO(code).readline))
    prev_end_line, prev_end_col = 1, 0
    lines = code.splitlines(keepends=True)

    for tok_type, tok_string, (start_line, start_col), (end_line, end_col), _ in tokens:
        if start_line <= len(lines):
            if start_line == prev_end_line:
                gap = lines[start_line - 1][prev_end_col:start_col]
                text_widget.insert("end", gap)
            else:
                for line in range(prev_end_line, start_line):
                    if line - 1 < len(lines):
                        if line == prev_end_line:
                            text_widget.insert("end", lines[line - 1][prev_end_col:])
                        else:
                            text_widget.insert("end", lines[line - 1])
                if start_line - 1 < len(lines):
                    text_widget.insert("end", lines[start_line - 1][:start_col])
        else:
            text_widget.insert("end", "\n")

        if tok_type == tokenize.NAME and tok_string in keyword.kwlist:
            tag_name = 'KEYWORD'
        elif tok_type == tokenize.NAME and tok_string in BUILTIN_NAMES:
            tag_name = 'BUILTIN'
        else:
            tag_name = TOKEN_TYPE_TO_NAME.get(tok_type, 'DEFAULT')

        text_widget.insert("end", tok_string, tag_name)
        prev_end_line, prev_end_col = end_line, end_col

    text_widget.config(state="disabled")

def escape_rtf(text):
    return text.replace('\\', r'\\').replace('{', r'\{').replace('}', r'\}')

# Цветовая таблица для RTF
COLOR_TABLE = {
    name: fr'\red{r}\green{g}\blue{b};'
    for name, hexcol in config_colors.items()
    for (r, g, b) in [hex_to_rgb(hexcol)]
}

TOKEN_TYPE_TO_COLOR = {
    tokenize.COMMENT: 'COMMENT',
    tokenize.STRING: 'STRING',
    tokenize.NUMBER: 'NUMBER',
    tokenize.OP: 'OP',
    tokenize.NAME: 'NAME',
}

def generate_rtf_from_code(code):
    result = []
    color_indices = {name: i + 1 for i, name in enumerate(COLOR_TABLE)}
    rtf = [r"{\rtf1\ansi\ansicpg1251"]
    color_table_rtf = r"{\colortbl ;" + ''.join(COLOR_TABLE[name] for name in COLOR_TABLE) + "}"
    rtf.append(color_table_rtf)
    rtf.append('\n')
    tokens = tokenize.generate_tokens(io.StringIO(code).readline)
    prev_line, prev_col = 1, 0

    for tok_type, tok_string, (start_line, start_col), (end_line, end_col), _ in tokens:
        while prev_line < start_line:
            result.append(r"\line ")
            prev_line += 1
            prev_col = 0
        if start_col > prev_col:
            spaces = start_col - prev_col
            result.append(r'\~' * spaces)
        if tok_type == tokenize.NAME and tok_string in keyword.kwlist:
            color = color_indices['KEYWORD']
        elif tok_type == tokenize.NAME and tok_string in BUILTIN_NAMES:
            color = color_indices['BUILTIN']
        else:
            color_name = TOKEN_TYPE_TO_COLOR.get(tok_type, 'DEFAULT')
            color = color_indices.get(color_name, color_indices['DEFAULT'])
        escaped = escape_rtf(tok_string)
        result.append(rf"\cf{color} {escaped}")
        prev_line = end_line
        prev_col = end_col if end_line == start_line else 0

    rtf.append(''.join(result))
    rtf.append('}')
    return ''.join(rtf)

def copy_rtf_to_clipboard(rtf_text):
    cf_rtf = win32clipboard.RegisterClipboardFormat("Rich Text Format")
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(cf_rtf, rtf_text.encode('cp1251'))
    win32clipboard.CloseClipboard()

def paste_from_clipboard(input_widget):
    win32clipboard.OpenClipboard()
    try:
        data = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
    except:
        data = ""
    win32clipboard.CloseClipboard()
    input_widget.insert("end", data)
