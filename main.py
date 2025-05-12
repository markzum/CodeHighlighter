import tkinter as tk
from highlighter import insert_highlighted_code, generate_rtf_from_code, copy_rtf_to_clipboard, paste_from_clipboard, TOKEN_TAGS


def main():
    root = tk.Tk()
    root.title("Подсветка Python-кода")
    root.geometry("1000x600")
    # Настраиваем grid для равного распределения
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)
    root.grid_rowconfigure(0, weight=1)

    # Левая панель: ввод
    frame_left = tk.Frame(root)
    frame_left.grid(row=0, column=0, sticky="nsew")
    lbl_input = tk.Label(frame_left, text="Исходный код:")
    lbl_input.pack(anchor="nw", padx=5, pady=(5,0))
    input_text = tk.Text(frame_left, wrap="none", font=("Consolas", 12))
    scrollbar_v_input = tk.Scrollbar(frame_left, orient="vertical", command=input_text.yview)
    scrollbar_h_input = tk.Scrollbar(frame_left, orient="horizontal", command=input_text.xview)
    input_text.config(yscrollcommand=scrollbar_v_input.set, xscrollcommand=scrollbar_h_input.set)
    scrollbar_v_input.pack(side="right", fill="y")
    scrollbar_h_input.pack(side="bottom", fill="x")
    input_text.pack(fill="both", expand=True)

    frame_left_buttons = tk.Frame(frame_left)
    frame_left_buttons.pack(fill="x")
    btn_paste = tk.Button(frame_left_buttons, text="Вставить из буфера обмена",
                          command=lambda: paste_from_clipboard(input_text))
    btn_paste.pack(side="left", padx=5, pady=5)
    btn_clear = tk.Button(frame_left_buttons, text="Очистить",
                          command=lambda: input_text.delete("1.0", "end"))
    btn_clear.pack(side="left", padx=5, pady=5)

    # Правая панель: вывод
    frame_right = tk.Frame(root)
    frame_right.grid(row=0, column=1, sticky="nsew")
    lbl_output = tk.Label(frame_right, text="Подсвеченный код:")
    lbl_output.pack(anchor="nw", padx=5, pady=(5,0))
    output_text = tk.Text(frame_right, wrap="none", font=("Courier New", 12))
    scrollbar_v_output = tk.Scrollbar(frame_right, orient="vertical", command=output_text.yview)
    scrollbar_h_output = tk.Scrollbar(frame_right, orient="horizontal", command=output_text.xview)
    output_text.config(yscrollcommand=scrollbar_v_output.set, xscrollcommand=scrollbar_h_output.set)
    scrollbar_v_output.pack(side="right", fill="y")
    scrollbar_h_output.pack(side="bottom", fill="x")
    output_text.pack(fill="both", expand=True)

    frame_right_buttons = tk.Frame(frame_right)
    frame_right_buttons.pack(fill="x")
    btn_copy = tk.Button(frame_right_buttons, text="Скопировать подсвеченный код",
                         command=lambda: copy_rtf_to_clipboard(
                             generate_rtf_from_code(input_text.get("1.0", "end")))
                         )
    btn_copy.pack(side="left", padx=5, pady=5)

    # Кнопка "Да будет цвет!" по центру снизу
    btn_color = tk.Button(root, text="Да будет цвет!", font=("Arial", 14),
                          width=20,
                          command=lambda: insert_highlighted_code(
                              output_text, input_text.get("1.0", "end"))
                          )
    btn_color.grid(row=1, column=0, columnspan=2, pady=10)

    # Создание тегов для подсветки
    for tag, conf in TOKEN_TAGS.items():
        output_text.tag_configure(tag, **conf)

    root.mainloop()


if __name__ == "__main__":
    main()
