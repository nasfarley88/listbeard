from telepot import glance
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from skybeard.beards import BeardChatHandler, Filters
import logging


logger = logging.getLogger(__name__)


class ShoppingListBeard(BeardChatHandler):

    _timeout = 1200

    __userhelp__ = "Shopping list beard WIP"

    __commands__ = [
        (Filters.text, 'pprint_list', 'Echos everything said by anyone.')
    ]

    item_prefix = " ☐ "
    item_done_prefix = " ☑ "

    def make_keyboard(self, items):
        """Make keyboard for shopping list"""

        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="{}. {}".format(
                    i, x), callback_data=self.serialize(str(i)))]
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
        keyboard = self.make_keyboard(text)  # At this point text is a list
        text = ['Shopping list:'] + text
        text = "\n{}".format(ShoppingListBeard.item_prefix).join(text)
        await self.sender.sendMessage(text, reply_markup=keyboard)

    async def on_callback_query(self, msg):
        query_id, from_id, query_data = glance(msg, flavor='callback_query')

        try:
            data = self.deserialize(query_data)
        except ThatsNotMineException:
            return

        await self.edit_shopping_list(msg, data)

    async def edit_shopping_list(self, origin_msg, data):
        await self.sender.sendMessage("Origin message:\n"+str(origin_msg))
        await self.sender.sendMessage("Data: "+str(data))
