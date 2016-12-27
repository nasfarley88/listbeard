from telepot import glance, origin_identifier
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from skybeard.beards import BeardChatHandler, Filters, ThatsNotMineException
import logging
import re


logger = logging.getLogger(__name__)


class ShoppingListBeard(BeardChatHandler):

    _timeout = 1200

    __userhelp__ = "Shopping list beard WIP"

    __commands__ = [
        ("shoppinglist", 'pprint_list', 'Echos everything said by anyone.')
    ]

    shopping_list_prefix = "Shopping list:\n"
    item_sep = "\n"
    item_prefix = "☐ "
    item_done_prefix = "☑ "

    def make_keyboard(self, items):
        """Make keyboard for shopping list"""

        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text=x,
                    callback_data=self.serialize(str(i)))]
                for i, x in enumerate(items)
            ])

    async def pprint_list(self, msg):
        await self.sender.sendMessage('Send me your list (comma separated).')
        resp = await self.listener.wait()
        try:
            text = resp['text']
        except KeyError:
            if '_idle' in resp:
                await self.sender.sendMessage(
                    "TODO put something witty about timing out here.")
            await self.sender.sendMessage(
                "Sorry, I don't think that message included a text component.")
            if logger.getEffectiveLevel() == logging.DEBUG:
                await self.sender.sendMessage(
                    "Response: \n"+str(resp))

        text = [x.strip() for x in text.split(",")]
        text = [ShoppingListBeard.item_prefix + x for x in text]
        keyboard = self.make_keyboard(text)  # At this point text is a list
        text = ShoppingListBeard.item_sep.join(text)
        text = ShoppingListBeard.shopping_list_prefix + text

        await self.sender.sendMessage(text, reply_markup=keyboard)

    async def on_callback_query(self, msg):
        query_id, from_id, query_data = glance(msg, flavor='callback_query')

        try:
            data = self.deserialize(query_data)
        except ThatsNotMineException:
            return

        await self.edit_shopping_list(msg, data)

    async def edit_shopping_list(self, origin_msg, data):
        if logger.getEffectiveLevel() == logging.DEBUG:
            await self.sender.sendMessage("Origin message:\n"+str(origin_msg))
            await self.sender.sendMessage("Shopping list as list:\n"+str(
                self.parse_shopping_list(origin_msg['message']['text'])))
            await self.sender.sendMessage("Data: "+str(data))

        try:
            data = int(data)
        except Exception as e:
            self.sender.sendMessage("Sorry, something went wrong.")
            raise e

        shopping_list = self.parse_shopping_list(origin_msg['message']['text'])
        if ShoppingListBeard.item_prefix in shopping_list[data]:
            shopping_list[data] = shopping_list[data].replace(
                ShoppingListBeard.item_prefix,
                ShoppingListBeard.item_done_prefix,
            )
        elif ShoppingListBeard.item_done_prefix in shopping_list[data]:
            shopping_list[data] = shopping_list[data].replace(
                ShoppingListBeard.item_done_prefix,
                ShoppingListBeard.item_prefix,
            )
        else:
            assert False, "Hmm, shouldn't get here..."

        keyboard = self.make_keyboard(shopping_list)
        text = self.format_shopping_list(shopping_list)

        await self.bot.editMessageText(
            origin_identifier(origin_msg),
            text=text,
            reply_markup=keyboard,
        )

    @classmethod
    def parse_shopping_list(cls, text):
        shopping_list = text.replace(
            ShoppingListBeard.shopping_list_prefix, '')
        shopping_list = shopping_list.split(
            ShoppingListBeard.item_sep)

        return shopping_list

    @classmethod
    def format_shopping_list(cls, shopping_list):
        text = ShoppingListBeard.item_sep.join(shopping_list)
        text = ShoppingListBeard.shopping_list_prefix + text

        return text
