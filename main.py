from json import load
from os import remove, mkdir
from os.path import exists
from importlib import reload, import_module

from discord.ext.commands import Bot, Context

with (open('token.json', 'r', encoding='UTF-8') as token_file,
      open('config.json', 'r', encoding='UTF_8') as config_file):

    token = load(token_file)[0]
    config = load(config_file)


app = Bot('python ')

cpython = {}


@app.event
async def on_ready():
    print(f'on-line, account: {app.user}')


@app.command(name=config['commands']['open_python_interpreter'])
async def open_python_interpreter(ctx: Context):
    if not exists('__p4dcache__'):
        mkdir('__p4dcache__')
        open('__init__.py', 'w').close()

    if str(ctx.author.id) not in cpython:
        with open(f'__p4dcache__/{ctx.author.id}.py', 'w') as file:
            file.write('')

        cpython[str(ctx.author.id)] = {
            'file_name': str(ctx.author.id),
            'enable': True,
            'imported': False
        }

        await ctx.send(f'**``p4d`` active for** @{ctx.author}')

    elif cpython[str(ctx.author.id)]['enable']:
        await ctx.send(f'**p4d was already active for the user** @{ctx.author}, **p4d will'
                       f' be deactivated for the same**')

        remove(f'__p4dcache__/{cpython[str(ctx.author.id)]["file_name"]}.py')
        del cpython[str(ctx.author.id)]

        await ctx.send(f'**``p4d`` has been disabled for** @{ctx.author}')


@app.command(name=config['commands']['exit_python_interpreter'])
async def exit_python_interpreter(ctx: Context):
    if str(ctx.author.id) in cpython:
        if cpython[str(ctx.author.id)]['enable']:
            remove(f'__p4dcache__/{cpython[str(ctx.author.id)]["file_name"]}.py')

            del cpython[str(ctx.author.id)]

            await ctx.send(f'**``p4d`` has been disabled for** @{ctx.author}')


@app.command(name=config['commands']['run_code'])
async def run_code(ctx: Context):
    content = ctx.message.content[
        len(app.command_prefix) + len(config['commands']['run_code']) + 6:-3] \
        .replace('print', 'await ctx.send') \
        .replace('\n', '\n  ')

    with open(f'__p4dcache__/{cpython[str(ctx.author.id)]["file_name"]}.py', 'w', encoding='UTF-8') as module:
        module.write(f'async def main(ctx):\n  {content}')

    module = import_module(f'__p4dcache__.{cpython[str(ctx.author.id)]["file_name"]}')
    module = reload(module)

    try:
        await module.main(ctx)

    except Exception as e:
        await ctx.send(f'```\n'
                       f'{e}'
                       f'```')

        remove(f'__p4dcache__/{cpython[str(ctx.author.id)]["file_name"]}.py')
        del cpython[str(ctx.author.id)]

        await ctx.send(f'**``p4d`` has been disabled for** @{ctx.author}')


if __name__ == '__main__':
    app.run(token)
