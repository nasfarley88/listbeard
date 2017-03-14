from telepot import glance, origin_identifier
from skybeard.beards import BeardChatHandler, ThatsNotMineException
from skybeard.predicates import Filters
from skybeard import utils
import logging

import spacy

from . import keyboards, message_parser, decorators

logger = logging.getLogger(__name__)

logger.info("Loading spacy english model")
english = spacy.load('en')
logger.info("Done!")


class ListBeard(BeardChatHandler):

    _timeout = 1200

    __userhelp__ = "Shopping list beard WIP"

    __commands__ = [
        ("checklist", 'pprint_list', 'Creates check list.'),
        (Filters.text_no_cmd, 'offer_list',
         "Offers to create a list if enough nouns are said."),
        ("currentlist", 'send_current_list',
         "Sends the list currently being created")
    ]

    check_list_prefix = "Check list:"
    item_sep = "\n"
    item_prefix = "☐ "
    item_done_prefix = "☑ "

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.current_noun_cache = []
        self.making_a_list = False

    async def send_current_list(self, msg):
        await self.sender.sendMessage(
            "Current list: {}".format(self.current_noun_cache))

    async def offer_list(self, msg):
        text = english(msg['text'])
        self.logger.debug("Nouns in the previous message: {}".format(
            [i for i in text.noun_chunks]))

        noun_list = [i for i in text.noun_chunks]
        word_list = [i for i in text]
        if len(noun_list) == 1 and len(word_list) < 4:
            for noun in noun_list:
                self.current_noun_cache.append(noun)
        else:
            self.current_noun_cache = []
            self.making_a_list = False

        if len(self.current_noun_cache) >= 3 and not self.making_a_list:
            self.making_a_list = True
            await self.sender.sendMessage(
                ("It looks like you're making a list!"
                 "\n\nWould you like me to make a checklist for you?"),
                reply_markup=await keyboards.make_list_confirmation_kbd(self))
        elif self.making_a_list:
            await self.sender.sendMessage(
                "{} added to the list.".format(noun_list[0]))

    async def list_to_checklist_msg_args(self, text, title=None):
        text = [ListBeard.item_prefix + x for x in text]
        keyboard = await keyboards.make_checklist_kbd(self, text)  # At this point text is a list

        if title is None:
            title = ListBeard.check_list_prefix

        text = await self.format_check_list(title, text)

        return {"text": text, "reply_markup": keyboard}

    async def pprint_list(self, msg):
        title = utils.get_args(msg, return_string=True)
        await self.sender.sendMessage('Send me your list (comma separated).')

        resp = await self.listener.wait()

        try:
            text = resp['text']
        except KeyError as e:
            if '_idle' in resp:
                await self.sender.sendMessage(
                    "I'm tired of waiting around."
                    " Type /checklist again if you still want to make a list.")
            else:
                await self.sender.sendMessage(
                    "Sorry, I don't think that message"
                    " included a text component.")

            return

        text = [x.strip() for x in text.split(",")]

        if title:
            kwargs = await self.list_to_checklist_msg_args(text, title)
        else:
            kwargs = await self.list_to_checklist_msg_args(text)

        await self.sender.sendMessage(**kwargs)

    @decorators.deserialize_or_ignore
    async def on_callback_query(self, msg, deserialized_data):
        query_id, from_id, query_data = glance(msg, flavor='callback_query')

        if len(deserialized_data) == 1:
            await self.edit_check_list(msg, deserialized_data)
        elif deserialized_data == 'cy':
            kwargs = await self.list_to_checklist_msg_args(
                [str(x) for x in self.current_noun_cache])
            await self.sender.sendMessage(**kwargs)
        else:
            await self.bot.answerCallbackQuery(
                query_id, "Sorry, that button is still being worked on.")

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

        list_title, check_list = self.parse_check_list(
            origin_msg['message']['text'])
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

        keyboard = await keyboards.make_checklist_kbd(check_list)
        text = await self.format_check_list(list_title, check_list)

        await self.bot.editMessageText(
            origin_identifier(origin_msg),
            text=text,
            reply_markup=keyboard,
        )

        query_id, from_id, query_data = glance(origin_msg, flavor='callback_query')
        await self.bot.answerCallbackQuery(query_id, check_list[data])

    @classmethod
    def parse_check_list(cls, text):
        list_title = message_parser.get_list_title(
            text, ListBeard.item_prefix, ListBeard.item_done_prefix)

        check_list = text.replace(list_title, '').strip()
        check_list = check_list.split(ListBeard.item_sep)

        return list_title, check_list

    @classmethod
    async def format_check_list(cls, list_title, check_list):
        text = ListBeard.item_sep.join(check_list)
        text = list_title + "\n" + text

        return text
