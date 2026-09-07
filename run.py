import asyncio
import re
import customtkinter as cst
from CTkMessagebox import CTkMessagebox
import winrt.windows.applicationmodel.datatransfer as w_am_dt
from pathlib import Path


cst.set_appearance_mode("dark")

class App(cst.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("240x580")
        self.title("Разметка")

        self.buttons = []

        self.button = cst.CTkButton(self, text="Вопрос:\nОтвет:", font=("Arial", 18), width=200, height=60, command=self.button_click)
        self.button.grid(row=0, column=0, padx=20, pady=5)
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
        
        btn_cliche = cst.CTkButton(
            self,
            text="Проверка",
            font=("Arial", 18),
            width=200,
            height=60,
            command=self.find_errors
        )
        btn_cliche.grid(row=len(parts) + 1, column=0, padx=20, pady=5)

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

    def _text_to_check(self):
        text = self.clipboard_get()
        m = re.search(r'Ответ\s*:', text)
        if m:
            return text[m.end():]
        return text

    _CLICHE_WORDS = [
        "Решим шаг за шагом",
        "Это типичная",
        "Типовой ответ на такую задачу",
        "Анализ",
        "Дано",
        "Для решения задачи нужно",
        "Для решения задачи",
        "Таким образом",
        "Нужно",
        "Теперь",
        "Тогда",
        "Теперь нам нужно",
        "Однако",
        "Конечно!",
        "Как я могу помочь?",
        "постановка задачи",
        "анализ ситуации",
        "анализ исходных данных",
        "теоретические основы",
        "анализ задачи"
    ]

    def find_errors(self):
        try:
            text = self._text_to_check()

            cliche_phrases = []
            for word in self._CLICHE_WORDS:
                if word in text:
                    pattern = rf'\b{re.escape(word)}\s+(\S+)'
                    matches = re.findall(pattern, text)
                    for match in matches:
                        if len(cliche_phrases) >= 3:
                            break
                        cliche_phrases.append(f'"{word} {match}..."')
                    if not matches:
                        cliche_phrases.append(f'"{word}..."')

            colon_errors = []
            for cm in re.finditer(r':', text):
                before = text[:cm.start()].rstrip()
                word1_m = re.search(r'([ЁёА-Яа-яA-Za-z-]+)\s*$', before)
                if not word1_m:
                    continue
                word1 = word1_m.group(1)
                if word1 in ("Вопрос", "Ответ"):
                    continue
                after = text[cm.end():]
                cap_m = re.match(r'(?:\s*(?:\d+[.)]|[-–—*•])\s*)*\s*([А-ЯЁA-Z][^\s!?.:;,]*)', after)
                if not cap_m:
                    continue
                cap_word = cap_m.group(1)
                if after[cap_m.end(1):cap_m.end(1) + 1] == ":":
                    continue
                colon_errors.append(f'"{word1}: {cap_word}..."')

            decimal_errors = []
            for m in re.finditer(r'\d+,\d+%?', text):
                if len(decimal_errors) >= 3:
                    break
                item = f'"{m.group(0)}"'
                if item not in decimal_errors:
                    decimal_errors.append(item)

            percent_errors = []
            for m in re.finditer(r'\d+(?:[.,]\d+)?%', text):
                if len(percent_errors) >= 3:
                    break
                item = f'"{m.group(0)}"'
                if item not in percent_errors:
                    percent_errors.append(item)

            unit_errors = []
            for m in re.finditer(r'\d+(?:[.,]\d+)?(?:[А-Яа-яЁё]+|[A-Za-z]+)', text):
                if len(unit_errors) >= 3:
                    break
                item = f'"{m.group(0)}"'
                if item not in unit_errors:
                    unit_errors.append(item)

            currency_errors = []
            for m in re.finditer(r'\d+(?:[.,]\d+)?[$€£¥₽¢]', text):
                if len(currency_errors) >= 3:
                    break
                item = f'"{m.group(0)}"'
                if item not in currency_errors:
                    currency_errors.append(item)

            numero_errors = []
            for m in re.finditer(r'№\d+', text):
                if len(numero_errors) >= 3:
                    break
                item = f'"{m.group(0)}"'
                if item not in numero_errors:
                    numero_errors.append(item)

            read_issues = []
            sentences = []
            start = 0
            for sm in re.finditer(r'(?:\r\n|\r|\n)|(?<=[.!?…])[ \t]+', text):
                seg = sm.group(0)
                if not (seg[0] in ".!?…" and sm.start() > 0 and text[sm.start() - 1].isdigit()):
                    sentences.append(text[start:sm.start()])
                    start = sm.end()
            sentences.append(text[start:])
            for s in sentences:
                if len(s) > 250:
                    quote = " ".join(s.split()[:3]) + "..."
                    read_issues.append(f'предложение содержит {len(s)} символов("{quote}")')
            paragraphs = text.splitlines()
            for p in paragraphs:
                p_len = len(p.strip())
                if p_len > 600:
                    quote = " ".join(p.strip().split()[:4]) + "..."
                    read_issues.append(f'абзац "{quote}" содержит {p_len} символов (превышает 600)')

            parts = []
            if cliche_phrases:
                parts.append(f'тег "Клише": имеются клишированные фразы({", ".join(cliche_phrases[:3])})')
            if colon_errors:
                parts.append(f'тег "Языковые ошибки": заглавные буквы после двоеточий({", ".join(colon_errors[:3])})')
            if decimal_errors:
                parts.append(f'тег "Языковые ошибки": запятая вместо точки в десятичных дробях({", ".join(decimal_errors[:3])})')
            if percent_errors:
                parts.append(f'тег "Языковые ошибки": отсутствие пробела между значением и знаком процента({", ".join(percent_errors[:3])})')
            if unit_errors:
                parts.append(f'тег "Языковые ошибки": отсутствие пробела между значением и единицей измерения({", ".join(unit_errors[:3])})')
            if currency_errors:
                parts.append(f'тег "Языковые ошибки": отсутствие пробела между значением и знаком валюты({", ".join(currency_errors[:3])})')
            if numero_errors:
                parts.append(f'тег "Языковые ошибки": отсутствие пробела между знаком № и числом({", ".join(numero_errors[:3])})')
            if read_issues:
                parts.append(f'тег "Трудночитаемость": {"; ".join(read_issues[:3])}')

            if not parts:
                CTkMessagebox(title="Результат", message="Ошибки не найдены в буфере обмена.", icon="info")
                return

            full_message = "\n\n".join(parts)

            msg = CTkMessagebox(
                title="Проверка",
                message=full_message,
                icon="info",
                option_1="Копировать",
                option_2="Отмена"
            )

            if msg.get() == "Копировать":
                self.clipboard_clear()
                self.clipboard_append(full_message)

        except Exception as e:
            CTkMessagebox(title="Ошибка", message=f"Ошибка: {e}", icon="cancel")


app = App()
app.mainloop()
