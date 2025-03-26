from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


class Keyboard:
    """
    class keyboard have builders for kb's
    """

    @staticmethod
    def create_reply_kb(buttons_text_list: list[str], width: int = 4) -> ReplyKeyboardMarkup:
        """
        creating reply kb from a list of buttons
        :param width: how many buttons in one row
        :param buttons_text_list: button names list
        :rtype: kb object
        """
        builder = ReplyKeyboardBuilder()
        buttons: list[KeyboardButton] = [KeyboardButton(text=button) for button in buttons_text_list]
        builder.row(*buttons, width=width)
        return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

    @staticmethod
    def create_inline_kb(buttons_text_list: list[str], width: int = 4) -> InlineKeyboardMarkup:
        """
        function creating inline keyboard using text in a list
        :param width: how many buttons in one row
        :param buttons_text_list:
        :return: keyboard
        """
        buttons: list[InlineKeyboardButton] = []
        kb_builder = InlineKeyboardBuilder()
        for i in range(len(buttons_text_list)):
            buttons.append(
                InlineKeyboardButton(text=buttons_text_list[i], callback_data=str(buttons_text_list[i]))
            )
        kb_builder.row(*buttons, width=width)
        return kb_builder.as_markup()


if __name__ == '__main__':
    pass
