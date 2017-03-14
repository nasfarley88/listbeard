import re
import logging

logger = logging.getLogger(__name__)


async def get_list_title(text, item_not_done_prefix, item_done_prefix):
    matches = re.findall(
        r"^(.*?)(?=({}|{}))".format(
            item_not_done_prefix,
            item_done_prefix,
        ), text, flags=re.DOTALL)
    logger.debug("Matches found for list title: "+str(matches))

    return matches[0][0].strip()
