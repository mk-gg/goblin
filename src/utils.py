import asyncio, glob, io, os, threading
import aiohttp, selfcord



from os.path import join
from datetime import datetime
from selfcord.ext import commands
from random import choice, uniform, randint
from collections.abc import AsyncGenerator, Generator
from concurrent.futures import ThreadPoolExecutor

from rich.console import Console
from rich import print

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


def get_time_now():
    return datetime.now().strftime("%H:%M:%S")

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


