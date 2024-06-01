import asyncio, glob, io, os, threading, re
import aiohttp, selfcord, httpx, urllib.parse



from os.path import join
from datetime import datetime, timedelta, timezone
from selfcord.ext import commands
from random import choice, uniform, randint
from collections.abc import AsyncGenerator, Generator
from concurrent.futures import ThreadPoolExecutor

from rich.console import Console
from rich import print
from rich.panel import Panel

console = Console()

async def async_run(
    func, 
    *args: str, 
    **kwargs: str
    ) -> asyncio.Future:
    """
    await async_run(synchronous function, args, keyword args) -> asyncio future object

    Runs a synchronous function asynchronous

    :param func function: Synchronous function to run
    :param args str: Arguments
    :param kwargs str: Keyword arguments
    """

    loop = asyncio.get_event_loop()

    return await loop.run_in_executor(
        ThreadPoolExecutor(),
        lambda: func(*args, **kwargs)
    )

def async_wrap_iter(
    it: Generator
    ) -> AsyncGenerator:
    """
    async_wrap_iter(iterable) -> async generator

    Turns a synchronous iterable into an asynchronous generator

    :param it Generator: Generator
    :returns AsyncGenerator: Asynchronous generator
    """

    loop = asyncio.get_event_loop()
    q = asyncio.Queue(1)

    exception = None
    _END = object()

    async def yield_queue_items() -> AsyncGenerator:
        """
        await yield_queue_items() -> async generator

        Yields all the items from the queue

        :returns AsyncGenerator: Asynchronous generator
        """

        while 1:
            next_item = await q.get()

            if next_item is _END:
                break

            yield next_item

        if exception is not None:
            # the iterator has raised, propagate the exception
            raise exception

    def iter_to_queue() -> None:
        """
        iter_to_queue() -> nothing

        Moves all the items from the iterable into the queue

        :returns None: Nothing
        """

        nonlocal exception

        try:
            for item in it:

                # This runs outside the event loop thread, so we
                # must use thread-safe API to talk to the queue.
                asyncio.run_coroutine_threadsafe(
                    q.put(item), 
                    loop
                ).result()

        except Exception as e:
            exception = e

        finally:
            asyncio.run_coroutine_threadsafe(
                q.put(_END), 
                loop
            ).result()

    threading.Thread(
        target=iter_to_queue
    ) .start()

    return yield_queue_items()

def get_size(
    _bytes: int | float, 
    suffix = "B"
    ) -> str:
    """
    get_size(bytes, suffix) -> proper unit

    Gets the proper unit for the bytes

    :param bytes int or float: Bytes
    :param suffix str: Suffix to prepend
    :returns str: String with proper unit and suffix prepended
    """

    factor = 1024
    for unit in ["", "Ki", "Mi", "Gi", "Te", "Pe"]:
        
        if _bytes < factor:
            return f'{_bytes:.2f}{unit}{suffix}'

        _bytes /= factor
    
    return ''

def clear() -> None:
    """
    clear() -> nothing

    Clears the screen, thats it

    :returns None: Nothing
    """

    print('\033c', end='')

async def load_cogs(
    client: commands.Bot
    ) -> None:
    """
    await load_cogs(client) -> nothing

    Loads all cogs in the "src/cogs" directory

    :param client commands.Bot: The connected discord bot/client
    :returns None: Nothing
    """

    for file in glob.glob(join('src', 'cogs', '*')):
        if file.endswith('.py') and not '__' in file and not file.endswith('.disabled.py'):
            file = file.replace(os.sep, '.')[:-3]
            
            console.log(f'[#307866]Loading cog --> {file}')
            
            try:
                await client.load_extension(file)

            except commands.errors.ExtensionAlreadyLoaded:
                await client.unload_extension(file)
                await client.load_extension(file)

            except Exception as e:
                print(f'[red]Exception while loading cog "{file}"> {str(e).rstrip()}\n')
                continue

async def unload_cog(
    client: commands.Bot,
    cog: str
    ) -> bool | None | Exception:
    """
    await unload_cog(client, cog name) -> status

    Unloads the given cog

    :param client commands.Bot: The connected discord bot/client
    :param cog str: Cog name
    :returns bool or Exception: True if the cog was unloaded, False if not found and an Exception if any errors where raised
    """

    for file in glob.glob(join('src', 'cogs', '*')):
        if cog in file:
            file = file.replace(os.sep, '.')[:-3]

            try:
                await client.unload_extension(file)

                return True
            except Exception as e:
                return e
    
    return False

def randomstr(
    length: int, 
    chars: str | list = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM0123456789"
    ) -> str:
    """
    randomstr(length, allowed characters) -> created string

    Builds a random string

    :param length int: Length of the string
    :param chars str or list: Characters to pick from
    """

    return ''.join([choice(chars) for _ in range(length)])


def translate_confusable_characters(input_string):
    alphabet_map = {
    "a": ['ɑ', 'α', 'а', '⍺', '𝐚', '𝑎', '𝒂', '𝒶', '𝓪', '𝔞', '𝕒', '𝖆', '𝖺', '𝗮', '𝘢', '𝙖', '𝚊', '𝛂', '𝛼', '𝜶', '𝝰', '𝞪', 'ａ'],
    "A": ['Ａ', 'ᗅ', 'Α', 'А', 'Ꭺ', 'ꓮ', '𝐀', '𝐴', '𝑨', '𝒜', '𝓐', '𝔸', '𝖠', '𝗔', '𝘈', '𝔄', '𝘼', '𝙰', '𝚨', '𝛢', '𝜜', '𝝖', '𝞐'],

    "b": ['Ƅ', 'Ь', 'Ꮟ', 'ᑲ', 'ᖯ', '𝐛', '𝑏', '𝒃', '𝒷', '𝓫', '𝔟', '𝕓', '𝖇', '𝖻', '𝗯', '𝘣', '𝙗', '𝚋'],
    "B": ['Β', 'В', 'Ᏼ', 'ᗷ', 'ℬ', 'ꓐ', 'Ꞵ', '𐊂', '𐊡', '𐌁', '𝐁', '𝐵', '𝑩', '𝓑', '𝔅', '𝔹', '𝕭', '𝖡', '𝗕', '𝘉', '𝘽', '𝙱', '𝚩', '𝛣', '𝜝', '𝝗', '𝞑', 'Ｂ'],

    "c": ['ϲ', 'с', 'ᴄ', 'ⅽ', 'ⲥ', 'ꮯ', '𐐽', '𝐜', '𝑐', '𝒄', '𝒸', '𝓬', '𝔠', '𝕔', '𝖈', '𝖼', '𝗰', '𝘤', '𝙘', '𝚌', 'ｃ'],
    "C": ['Ϲ', 'С', 'Ꮯ', 'ℂ', 'ℭ', 'Ⅽ', 'Ⲥ', 'ꓚ', '𐊢', '𐌂', '𐐕', '𝐂', '𝐶', '𝑪', '𝒞', '𝓒', '𝕮', '𝖢', '𝗖', '𝘊', '𝘾', '𝙲', '🝌', 'Ｃ'],

    "d": ['ԁ', 'Ꮷ', 'ᑯ', 'ⅆ', 'ⅾ', 'ⅾ', '𝐝', '𝑑', '𝒅', '𝒹', '𝓭', '𝔡', '𝕕', '𝖉', '𝖽', '𝗱', '𝘥', '𝙙', '𝚍'],
    "D": ['Ꭰ', 'ᗞ', 'ᗪ', 'ⅅ', 'Ⅾ', 'ꓓ', '𝐃', '𝐷', '𝑫', '𝒟', '𝓓', '𝔇', '𝔻', '𝕯', '𝖣', '𝗗', '𝘋', '𝘿', '𝙳'],

    "e": ['е', 'ҽ', '℮', 'ℯ', 'ⅇ', 'ꬲ', '𝐞', '𝑒', '𝒆', '𝓮', '𝔢', '𝕖', '𝖊', '𝖾', '𝗲', '𝘦', '𝙚', '𝚎', 'ｅ'],
    "E": ['Ε', 'Е', 'Ꭼ', 'ℰ', '⋿', 'ⴹ', 'ꓰ', '𐊆', '𝐄', '𝐸', '𝑬', '𝓔', '𝔈', '𝔼', '𝕰', '𝖤', '𝗘', '𝘌', '𝙀', '𝙴', '𝚬', '𝛦', '𝜠', '𝝚', '𝞔', 'Ｅ'],

    "f": ['ſ', 'ẝ', 'ꞙ', 'ꞙ', '𝐟', '𝑓', '𝒇', '𝒻', '𝓯', '𝔣', '𝕗', '𝖋', '𝖿', '𝗳', '𝘧', '𝙛', '𝚏'],
    "F": ['Ϝ', 'ᖴ', 'ℱ', 'ꓝ', 'Ꞙ', '𐊇', '𐊥', '𝐅', '𝐹', '𝑭', '𝓕', '𝔉', '𝔽', '𝕱', '𝖥', '𝗙', '𝘍', '𝙁', '𝙵', '𝟊'],

    "g": ['ƍ', 'ɡ', 'ց', 'ᶃ', 'ℊ', '𝐠', '𝑔', '𝒈', '𝓰', '𝔤', '𝕘', '𝖌', '𝗀', '𝗴', '𝘨', '𝙜', '𝚐', 'ｇ'],
    "G": ['G', 'Ꮐ', 'Ᏻ', 'ꓖ', '𝐆', '𝐺', '𝑮', '𝒢', '𝓖', '𝔊', '𝔾', '𝕲', '𝖦', '𝗚', '𝘎', '𝙂', '𝙶'],

    "h": ['һ', 'հ', 'Ꮒ', 'ℎ', '𝐡', '𝒉', '𝒽', '𝓱', '𝔥', '𝕙', '𝖍', '𝗁', '𝗵', '𝘩', '𝙝', '𝚑', 'ｈ'],
    "H": ['Η', 'Н', 'Ꮋ', 'ᕼ', 'ℋ', 'ℌ', 'ℍ', 'Ⲏ', 'ꓧ', '𐋏', '𝐇', '𝐻', '𝑯', '𝓗', '𝕳', '𝖧', '𝗛', '𝘏', '𝙃', '𝙷', '𝚮', '𝛨', '𝜢', '𝝜', '𝞖', 'Ｈ'],

    "i": ['i', 'ı', 'ɩ', 'ι', 'і', 'Ꭵ', 'ℹ', 'ⅈ', 'ⅰ', '⍳', 'ꙇ', 'ꭵ', '𝐢', '𝑖', '𝒊', '𝒾', '𝓲', '𝔦', '𝕚', '𝖎', '𝗂', '𝗶', '𝘪', '𝙞', '𝚒', '𝚤', '𝛊', '𝜄', '𝜾', '𝝸', '𝞲', 'ｉ'],
    "I": ['ɪ', 'Ɩ', 'ǀ', 'Ι', 'Ι', 'І', 'Ӏ', '׀', 'ו', 'ן', 'ا', 'ߊ', 'ᛁ', 'ℐ', 'ℑ', 'I', '𝐈'],

    "j": ['ϳ', 'ј', 'ⅉ', '𝐣', '𝑗', '𝒋', '𝒿', '𝓳', '𝔧', '𝕛', '𝖏', '𝗃', '𝗷', '𝘫', '𝙟', '𝚓', 'ｊ'],
    'J': ['Ϳ', ],


    }
    # https://util.unicode.org/UnicodeJsps/confusables.jsp?a=B&r=None
    trans_table = str.maketrans({k: char for char, variations in alphabet_map.items() for k in variations})
    return input_string.translate(trans_table)

def create_panel(url, category, guild_name, message):
    panel_message = (
        f"Link detected: [b]{url}[/]\n"
        f"Category: [b]{category}[/]\n"
        f"Guild name: [b]{guild_name}[/]\n"
        f"Message: [b]{message.content}[/]\n\n"
        f"Sender: [b]{message.author.name}[/]\n"
        f"UID: [b]{message.author.id}[/]" 
    )
    panel = Panel.fit(panel_message, width=60, padding=(1, 2), title="Warning", subtitle=f"- {message.author.guild} -")
    print(panel)

def get_time_now():
    return datetime.now().strftime("%H:%M:%S")

def check_date(input_date, day):
    """
    This function checks if the given date is within the specified number of days.
    
    Parameters:
    input_date (str): The date to check in the format "YYYY-MM-DD HH:MM:SS%z".
    day (int): The number of days within which the given date should be.
    
    Returns:
    bool: True if the given date is within the specified number of days, otherwise False.
    """

    given_date_str = input_date
    given_date = datetime.strptime(given_date_str, "%Y-%m-%d %H:%M:%S%z")
    current_date = datetime.now(timezone.utc)
    time_difference = current_date - given_date 
    return time_difference < timedelta(days=day)

def extract_urls(messages):
    """
    Extract URLs from a list of messages.
    """
    url_pattern = r"https?://?[^\s)]+|discord\.gg/[^\s)]+|discord\.com/invite/[^\s)]+"
    matches = re.findall(url_pattern, messages)
    urls = [match.rstrip("/ >") for match in matches]
    return [url.replace("\\", "").replace("@", "").replace("/?", "").replace("///", "//") for url in urls]


def get_final_url(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    if not url.startswith('http'):
        url = 'https://' + url

    # Check if the URL is a Twitter short URL
    if url.startswith('https://t.co/'):
        try:
            response = httpx.get(url, headers=headers, follow_redirects=False)
            response.raise_for_status()  # Raise an exception if the status code is not 200
            data = response.text
            url = re.search("(?P<url>https?://[^\s]+)\"", data).group("url")
            return str(url)
        except httpx.HTTPError as err:
            print(f'An HTTP error occurred: {err}')
        except httpx.RequestError as err:
            print(f'An error occurred: {err}')

    try:
        with httpx.Client(timeout=50.0) as client:
            response = client.get(url, headers=headers, follow_redirects=True)
            response.raise_for_status()  # Raise an exception if the status code is not 200
            return str(response.url)
    except httpx.HTTPError as err:
        print(f'An HTTP error occurred: {err}')
    except httpx.RequestError as err:
        print(f'An error occurred: {err}')

async def sendmsg(
    ctx, 
    message: str = '',
    edit_after: bool = True,
    img: str | None = None
    ) -> bool:
    """
    await sendmsg(context, message, edit afterwards) -> status

    Sends a message, and adds some randomization to the delays

    :param ctx object: Context
    :param message str: Message to send
    :param img str or None: Image to send from url, leave empty for no image
    :param edit_after bool: Edit the message so it doesn't raise suspicions
    :returns bool: True if everything succeeded, False if not
    """

    attachments = []
    if img:
        async with aiohttp.ClientSession() as session:
            async with session.get(img) as resp:
                
                if resp.status != 200:
                    await ctx.message.send('Could not download file...')
                
                else:
                    data = io.BytesIO(await resp.read())
                    attachments = [selfcord.File(data, f'{randomstr(randint(1, 9))}.png')]

    await asyncio.sleep(uniform(1, 5))

    # overwrite the trigger message with our own message
    await ctx.message.edit(
        content=message, 
        attachments=attachments
    )

    if edit_after:
        await asyncio.sleep(uniform(10, 20))

        # after that, delete the message
        await ctx.message.delete()

    return True


