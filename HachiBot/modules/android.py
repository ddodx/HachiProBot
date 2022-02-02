from distutils import command
import re
import time
from datetime import datetime

from bs4 import BeautifulSoup
from hurry.filesize import size as sizee
from requests import get
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram.error import BadRequest
from ujson import loads
from yaml import load, Loader

from HachiBot import dispatcher
from HachiBot.modules.sql.clear_cmd_sql import get_clearcmd
from HachiBot.modules.github import getphh
from HachiBot.modules.disable import DisableAbleCommandHandler
from HachiBot.modules.helper_funcs.alternate import typing_action
from HachiBot.modules.helper_funcs.decorators import ddocmd
from HachiBot.modules.helper_funcs.misc import delete

GITHUB = "https://github.com"
DEVICES_DATA = "https://raw.githubusercontent.com/androidtrackers/certified-android-devices/master/by_device.json"


@ddocmd(command="device", can_disable=True)
@typing_action
def device(update, context):
    args = context.args
    if len(args) == 0:
        reply = "No codename provided, write a codename for fetching informations."
        del_msg = update.effective_message.reply_text(
            "{}".format(reply),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
        time.sleep(5)
        try:
            del_msg.delete()
            update.effective_message.delete()
        except BadRequest as err:
            if err.message in [
                "Message to delete not found",
                "Message can't be deleted",
            ]:
                return
    devices = " ".join(args)
    db = get(DEVICES_DATA).json()
    newdevice = devices.strip("lte") if devices.startswith("beyond") else devices
    try:
        reply = f"Search results for {devices}:\n\n"
        brand = db[newdevice][0]["brand"]
        name = db[newdevice][0]["name"]
        model = db[newdevice][0]["model"]
        codename = newdevice
        reply += (
            f"<b>{brand} {name}</b>\n"
            f"Model: <code>{model}</code>\n"
            f"Codename: <code>{codename}</code>\n\n"
        )
    except KeyError:
        reply = f"Couldn't find info about {devices}!\n"
        del_msg = update.effective_message.reply_text(
            "{}".format(reply),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
        time.sleep(5)
        try:
            del_msg.delete()
            update.effective_message.delete()
        except BadRequest as err:
            if err.message in [
                "Message to delete not found",
                "Message can't be deleted",
            ]:
                return
    update.message.reply_text(
        "{}".format(reply), parse_mode=ParseMode.HTML, disable_web_page_preview=True
    )


@ddocmd(command="gsi", can_disable=True)
@typing_action
def gsi(update, context):
    message = update.effective_message

    usr = get(
        "https://api.github.com/repos/phhusson/treble_experimentations/releases/latest"
    ).json()
    reply_text = "*Gsi'S Latest release*\n"
    for i in range(len(usr)):
        try:
            name = usr["assets"][i]["name"]
            url = usr["assets"][i]["browser_download_url"]
            reply_text += f"[{name}]({url})\n"
        except IndexError:
            continue
    message.reply_text(reply_text, parse_mode=ParseMode.MARKDOWN)


@ddocmd(command="checkfw", can_disable=True)
def checkfw(update: Update, context: CallbackContext):
    args = context.args
    message = update.effective_message
    chat = update.effective_chat

    if len(args) == 2:
        temp, csc = args
        model = f"sm-" + temp if not temp.upper().startswith("SM-") else temp
        fota = get(
            f"http://fota-cloud-dn.ospserver.net/firmware/{csc.upper()}/{model.upper()}/version.xml"
        )

        if fota.status_code != 200:
            msg = f"Couldn't check for {temp.upper()} and {csc.upper()}, please refine your search or try again later!"

        else:
            page = BeautifulSoup(fota.content, "lxml")
            os = page.find("latest").get("o")

            if page.find("latest").text.strip():
                msg = f"*Latest released firmware for {model.upper()} and {csc.upper()} is:*\n"
                pda, csc, phone = page.find("latest").text.strip().split("/")
                msg += f"• PDA: `{pda}`\n• CSC: `{csc}`\n"
                if phone:
                    msg += f"• Phone: `{phone}`\n"
                if os:
                    msg += f"• Android: `{os}`\n"
                msg += ""
            else:
                msg = f"*No public release found for {model.upper()} and {csc.upper()}.*\n\n"

    else:
        msg = "Give me something to fetch, like:\n`/checkfw SM-N975F DBT`"

    delmsg = message.reply_text(
        text=msg,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
    )

    cleartime = get_clearcmd(chat.id, "checkfw")

    if cleartime:
        context.dispatcher.run_async(delete, delmsg, cleartime.time)


@ddocmd(command="getfw", can_disable=True)
def getfw(update: Update, context: CallbackContext):
    args = context.args
    message = update.effective_message
    chat = update.effective_chat
    btn = ""

    if len(args) == 2:
        temp, csc = args
        model = f"sm-" + temp if not temp.upper().startswith("SM-") else temp
        fota = get(
            f"http://fota-cloud-dn.ospserver.net/firmware/{csc.upper()}/{model.upper()}/version.xml"
        )

        if fota.status_code != 200:
            msg = f"Couldn't check for {temp.upper()} and {csc.upper()}, please refine your search or try again later!"

        else:
            url1 = f"https://samfrew.com/model/{model.upper()}/region/{csc.upper()}/"
            url2 = f"https://www.sammobile.com/samsung/firmware/{model.upper()}/{csc.upper()}/"
            url3 = f"https://sfirmware.com/samsung-{model.lower()}/#tab=firmwares"
            url4 = f"https://samfw.com/firmware/{model.upper()}/{csc.upper()}/"
            fota = get(
                f"http://fota-cloud-dn.ospserver.net/firmware/{csc.upper()}/{model.upper()}/version.xml"
            )
            page = BeautifulSoup(fota.content, "lxml")
            os = page.find("latest").get("o")
            msg = ""
            if page.find("latest").text.strip():
                pda, csc2, phone = page.find("latest").text.strip().split("/")
                msg += f"*Latest firmware for {model.upper()} and {csc.upper()} is:*\n"
                msg += f"• PDA: `{pda}`\n• CSC: `{csc2}`\n"
                if phone:
                    msg += f"• Phone: `{phone}`\n"
                if os:
                    msg += f"• Android: `{os}`\n"
            msg += "\n"
            msg += f"*Downloads for {model.upper()} and {csc.upper()}*\n"
            btn = [[InlineKeyboardButton(text=f"samfrew.com", url=url1)]]
            btn += [[InlineKeyboardButton(text=f"sammobile.com", url=url2)]]
            btn += [[InlineKeyboardButton(text=f"sfirmware.com", url=url3)]]
            btn += [[InlineKeyboardButton(text=f"samfw.com", url=url4)]]
    else:
        msg = "Give me something to fetch, like:\n`/getfw SM-N975F DBT`"

    delmsg = message.reply_text(
        text=msg,
        reply_markup=InlineKeyboardMarkup(btn),
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
    )

    cleartime = get_clearcmd(chat.id, "getfw")

    if cleartime:
        context.dispatcher.run_async(delete, delmsg, cleartime.time)


__help__ = """
Get the latest Magsik releases or TWRP for your device!
*Android related commands:*
× /magisk - Gets the latest magisk release for Stable/Beta/Canary.
× /phhmagisk - Gets Latest los build.
× /device <codename> - Gets android device basic info from its codename.
× /twrp <codename> -  Gets latest twrp for the android device using the codename.
× /orangefox <codename> -  Gets latest orangefox recovery for the android device using the codename.
× /los <codename> - Gets Latest los build.
× /evo <codename> - Gets Latest evolution build.
× /gsi <codename> - Gets Latest gsi build.
× /pixys <codename> - Gets Latest pixyos build.
× /miui <devicecodename>- Fetches latest firmware info for a given device codename
× /realmeui <devicecodename>- Fetches latest firmware info for a given device codename
× /phh : Get lastest phh builds from github
× /miui <devicecodename>- Get samsung spesifikasi
× /whatis <devicecodename>- to get information from codename
× /variant <devicecodename>- same yang atas
× /samget <devicecodename>- get samsung spesifikasi
× /checkfw <model> <csc> - Samsung only - Shows the latest firmware info for the given device, taken from samsung servers
× /getfw <model> <csc> - Samsung only - gets firmware download links from samfrew, sammobile and sfirmwares for the given device
"""

__mod_name__ = "Android"
