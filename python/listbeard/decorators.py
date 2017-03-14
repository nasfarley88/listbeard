from functools import wraps

from telepot import glance

from skybeard.beards import ThatsNotMineException


def deserialize_or_ignore(f):
    @wraps(f)
    async def g(self, msg):
        _, _, query_data = glance(msg, flavor='callback_query')

        try:
            data = self.deserialize(query_data)
            return await f(self, msg, data)
        except ThatsNotMineException:
            return

    return g
