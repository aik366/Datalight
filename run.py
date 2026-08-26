import asyncio
import customtkinter as cst
import winrt.windows.applicationmodel.datatransfer as w_am_dt


class App(cst.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("600x500")
        self.title("CTk example")

        self.button = cst.CTkButton(self, command=self.button_click)
        self.button.grid(row=0, column=0, padx=20, pady=10)

    def button_click(self):
        try:
            history = asyncio.run(self._get_clip_history())
            last_one, last_two = [i.replace("\n", "") for i in history[:2]]
            text = f"Вопрос: {last_two}\n\nОтвет: {last_one}"

            self.clipboard_clear()
            self.clipboard_append(text)
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
