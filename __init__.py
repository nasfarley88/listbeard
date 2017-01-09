from telepot import glance, origin_identifier
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from skybeard.beards import BeardChatHandler, Filters, ThatsNotMineException
import logging
import re


logger = logging.getLogger(__name__)


class ListBeard(BeardChatHandler):

    _timeout = 1200

    __userhelp__ = "Shopping list beard WIP"

    __commands__ = [
        ("checklist", 'pprint_list', 'Creates check list.')
    ]

    check_list_prefix = "Check list:\n"
    item_sep = "\n"
    item_prefix = "☐ "
    item_done_prefix = "☑ "

    def make_keyboard(self, items):
        """Make keyboard for check list"""

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
        text = [ListBeard.item_prefix + x for x in text]
        keyboard = self.make_keyboard(text)  # At this point text is a list
        text = ListBeard.item_sep.join(text)
        text = ListBeard.check_list_prefix + text

        await self.sender.sendMessage(text, reply_markup=keyboard)

    async def on_callback_query(self, msg):
        query_id, from_id, query_data = glance(msg, flavor='callback_query')

        try:
            data = self.deserialize(query_data)
        except ThatsNotMineException:
            return

        await self.edit_check_list(msg, data)

    async def edit_check_list(self, origin_msg, data):
        self.logger.debug("Origin message:\n"+str(origin_msg))
        self.logger.debug("Shopping list as list:\n"+str(
            self.parse_check_list(origin_msg['message']['text'])))
        self.logger.debug("Data: "+str(data))

        try:
            data = int(data)
        except Exception as e:
            self.sender.sendMessage("Sorry, something went wrong.")
            raise e

        check_list = self.parse_check_list(origin_msg['message']['text'])
        if ListBeard.item_prefix in check_list[data]:
            check_list[data] = check_list[data].replace(
                ListBeard.item_prefix,
                ListBeard.item_done_prefix,
            )
        elif ListBeard.item_done_prefix in check_list[data]:
            check_list[data] = check_list[data].replace(
                ListBeard.item_done_prefix,
                ListBeard.item_prefix,
            )
        else:
            assert False, "Hmm, shouldn't get here..."

        keyboard = self.make_keyboard(check_list)
        text = self.format_check_list(check_list)

        await self.bot.editMessageText(
            origin_identifier(origin_msg),
            text=text,
            reply_markup=keyboard,
        )

    @classmethod
    def parse_check_list(cls, text):
        check_list = text.replace(
            ListBeard.check_list_prefix, '')
        check_list = check_list.split(
            ListBeard.item_sep)

        return check_list

    @classmethod
    def format_check_list(cls, check_list):
        text = ListBeard.item_sep.join(check_list)
        text = ListBeard.check_list_prefix + text

        return text
