import asyncio
import customtkinter as cst
import winrt.windows.applicationmodel.datatransfer as w_am_dt
from pathlib import Path


cst.set_appearance_mode("dark")

class App(cst.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("240x440")
        self.title("Разметка")

        self.buttons = []

        self.button = cst.CTkButton(self, text="Вопрос:\nОтвет:", font=("Arial", 18), width=200, height=60, command=self.button_click)
        self.button.grid(row=0, column=0, padx=20, pady=10)
        self.buttons.append(self.button)

        parts = Path("copy.txt").read_text(encoding="utf-8").split("#@#\n")
        texts = {
            1: "Хорошо\nХорошо",
            2: "Хорошо\nПлохо",
            3: "Плохо\nПлохо",
            4: "Качество эксперта",
            5: "На скриншотах",
        }
        for i, part in enumerate(parts):
            row = i + 1
            btn = cst.CTkButton(
                self,
                text=texts.get(i + 1, f"Часть {i + 1}"),
                font=("Arial", 18),
                width=200,
                height=60,
                command=lambda p=part: self.copy_part_click(p),
            )
            btn.grid(row=row, column=0, padx=20, pady=5)
            self.buttons.append(btn)

    def button_click(self):
        try:
            history = asyncio.run(self._get_clip_history())
            last_one, last_two = [i.replace("\n", "") for i in history[:2]]
            text = f"Вопрос: {last_two}\n\nОтвет: {last_one}"

            self.clipboard_clear()
            self.clipboard_append(text)
        except Exception as e:
            print(f"Ошибка: {e}")

    def copy_button_click(self):
        try:
            text = Path("copy.txt").read_text(encoding="utf-8")
            self.clipboard_clear()
            self.clipboard_append(text)
        except Exception as e:
            print(f"Ошибка: {e}")

    def copy_part_click(self, part):
        try:
            self.clipboard_clear()
            self.clipboard_append(part)
        except Exception as e:
            print(f"Ошибка: {e}")

    @staticmethod
    async def _get_clip_history():
        result = await w_am_dt.Clipboard.get_history_items_async()
        return [
            await item.content.get_text_async()
            for item in (result.items or [])
            if item.content and item.content.contains("Text")
        ]


app = App()
app.mainloop()
