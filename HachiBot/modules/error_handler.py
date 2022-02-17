import html
import io
import random
import sys
import traceback

import pretty_errors
import requests
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode,
    Update,
)
from telegram.ext import CallbackContext

from HachiBot import DEV_USERS, ERROR_LOGS, dispatcher

pretty_errors.mono()


class ErrorsDict(dict):
    """A custom dict to store errors and their count"""

    def __init__(self, *args, **kwargs):
        self.raw = []
        super().__init__(*args, **kwargs)

    def __contains__(self, error):
        self.raw.append(error)
        error.identifier = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=5))
        for e in self:
            if type(e) is type(error) and e.args == error.args:
                self[e] += 1
                return True
        self[error] = 0
        return False

    def __len__(self):
        return len(self.raw)


errors = ErrorsDict()


def error_callback(update: Update, context: CallbackContext):
    if not update:
        return
    if context.error not in errors:
        try:
            stringio = io.StringIO()
            pretty_errors.output_stderr = stringio
            output = pretty_errors.excepthook(
                type(context.error),
                context.error,
                context.error.__traceback__,
            )
            pretty_errors.output_stderr = sys.stderr
            pretty_error = stringio.getvalue()
            stringio.close()
        except:
            pretty_error = "Failed to create pretty error."
        tb_list = traceback.format_exception(
            None,
            context.error,
            context.error.__traceback__,
        )
        tb = "".join(tb_list)
        pretty_message = (
            "{}\n"
            "-------------------------------------------------------------------------------\n"
            "An exception was raised while handling an update\n"
            "User: {}\n"
            "Chat: {} {}\n"
            "Callback data: {}\n"
            "Message: {}\n\n"
            "Full Traceback: {}"
        ).format(
            pretty_error,
            update.effective_user.id,
            update.effective_chat.title if update.effective_chat else "",
            update.effective_chat.id if update.effective_chat else "",
            update.callback_query.data if update.callback_query else "None",
            update.effective_message.text if update.effective_message else "No message",
            tb,
        )
        extension = "txt"
        url = "https://spaceb.in/api/v1/documents/"
        try:
            response = requests.post(
                url, data={"content": pretty_message, "extension": extension}
            )
        except Exception as e:
            return {"error": str(e)}
        response = response.json()
        e = html.escape(f"{context.error}")
        if not response:
            with open("error.txt", "w+") as f:
                f.write(pretty_message)
            context.bot.send_document(
                ERROR_LOGS,
                open("error.txt", "rb"),
                caption=f"#{context.error.identifier}\n<b>Darling, i have an Error :"
                f"</b>\n<code>{e}</code>",
                parse_mode="html",
            )
            return

        url = f"https://spaceb.in/{response['payload']['id']}"
        context.bot.send_message(
            ERROR_LOGS,
            text=f"#{context.error.identifier}\n<b>Darling, i have an Error :"
            f"</b>\n<code>{e}</code>",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("See The Error Darling!", url=url)]],
            ),
            parse_mode=ParseMode.HTML,
        )