from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from Alya import app

def generate_help_buttons(_, start: int, end: int, current_page: int):
    buttons = []
    buttons_per_row = 3
    for idx, i in enumerate(range(start, end + 1)):
        if idx % buttons_per_row == 0:
            buttons.append([])
        buttons[-1].append(InlineKeyboardButton(
            text=_[f"H_B_{i}"],
            callback_data=f"help_callback hb{i}_p{current_page}"
        ))
    return buttons

def first_page(_):
    buttons = generate_help_buttons(_, start=1, end=15, current_page=1)
    navigation_buttons = [
        InlineKeyboardButton(text="๏ ᴍᴇɴᴜ ๏", callback_data="back_to_main"),
        InlineKeyboardButton(text="๏ ɴᴇxᴛ ๏", callback_data="help_next_2")
    ]
    buttons.append(navigation_buttons)
    return InlineKeyboardMarkup(buttons)

def second_page(_):
    buttons = generate_help_buttons(_, start=16, end=30, current_page=2)
    navigation_buttons = [
        InlineKeyboardButton(text="๏ ʙᴀᴄᴋ ๏", callback_data="help_prev_1"),
        InlineKeyboardButton(text="๏ ᴍᴇɴᴜ ๏", callback_data="back_to_main")
    ]
    buttons.append(navigation_buttons)
    return InlineKeyboardMarkup(buttons)

def help_back_markup(_, current_page):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=_["BACK_BUTTON"],
                    callback_data=f"help_back_{current_page}"
                ),
                InlineKeyboardButton(
                    text=_["CLOSE_BUTTON"],
                    callback_data="close"
                ),
            ]
        ]
    )

def private_help_panel(_):
    return [
        [
            InlineKeyboardButton(
                text=_["S_B_4"],
                url=f"https://t.me/{app.username}?start=help"
            ),
        ],
    ]