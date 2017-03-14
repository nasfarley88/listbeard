from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton


async def make_checklist_kbd(bot_instance, items):
    """Make keyboard for check list"""

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=x,
                callback_data=bot_instance.serialize(str(i)))]
            for i, x in enumerate(items)
        ])


async def make_list_confirmation_kbd(bot_instance):
    """Make keyboard for check list"""

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text='Yes',
                callback_data=bot_instance.serialize(str('cy'))),
             InlineKeyboardButton(
                 text='No',
                 callback_data=bot_instance.serialize(str('cn')))],
            [InlineKeyboardButton(
                text='Yes, but I\'ve still got a few more items to add.',
                callback_data=bot_instance.serialize(str('cn')))],
        ])
