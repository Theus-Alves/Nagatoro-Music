# Please check the README and the requirements.txt to get your code working perfectly.

from fileinput import filename
import discord
from discord.ext import commands
from decouple import config
from dotenv import load_dotenv
import youtube_dl
import asyncio

load_dotenv()

intents = discord.Intents().all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='.',intents=intents)
url_aux = 'teste'

players = {}
COR = 0xF7FE2E

    #       YOUTUBE_DL CONFIGURATION       #
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename

#Comandos do Bot = PLAY | PAUSE | RESUME | STOP | LEAVE


@bot.command(name='play', help='Tocar Musica')
async def play(ctx, url):
     
    # Comandos para o BOT tocar uma musica do YT atravéz de um link
    try:
        if not ctx.message.author.voice:
            await ctx.send("koe, {}. Vc precisa tá conectado a um canal de voz".format(ctx.message.author.name))
            return
        else:
            channel = ctx.message.author.voice.channel
            await channel.connect()
    except:
        pass
    FFMPEG_OPTIONS = {'before_options':'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options':'-vn'}
    YDL_OPTIONS = {'format':'bestaudio'}
    vc = ctx.voice_client
    vc.stop()

    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info['formats'][0]['url']
        source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
        vc.play(source)
        titulo = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
        await ctx.send(f'*Solicitada por {ctx.message.author.name}*')
        await ctx.send(f'***Tocando Agora*** : {titulo}')
        ctx.url_aux = url    

@bot.command(name='pause', help='Este comando pausa a música')
async def pause(ctx):
    vc = ctx.message.guild.voice_client
    if vc.is_playing():
        vc.pause()
        titulo = await YTDLSource.from_url(url_aux, loop=bot.loop, stream=True)
        await ctx.send(f'*Solicitada por {ctx.message.author.name}*')
        await ctx.send(f'***Musica Pausada*** : {titulo}')
    else:
        await ctx.send("O bot não está tocando nada no momento.")
    
@bot.command(name='resume', help='Retorna a musica')
async def resume(ctx):
    vc = ctx.message.guild.voice_client
    if vc.is_paused():
        vc.resume()
        titulo = await YTDLSource.from_url(url_aux, loop=bot.loop, stream=True)
        await ctx.send(f'*Solicitada por {ctx.message.author.name}*')
        await ctx.send(f'***Tocando Agora*** : {titulo}') 
    else:
        await ctx.send("O bot não estava tocando nada antes disso. Use o comando .play")

@bot.command(name='stop', help='Parar a Música')
async def stop(ctx):
    vc = ctx.message.guild.voice_client
    if vc.is_playing():
        vc.stop()
        titulo = await YTDLSource.from_url(url_aux, loop=bot.loop, stream=True)
        await ctx.send(f'*Solicitada por {ctx.message.author.name}*')
        await ctx.send(f'***Encerrado*** : {titulo}')
        await ctx.send('Use o comando .play + link da sua música favorita.')
    else:
        await ctx.send("O bot não está tocando nada no momento.")

@bot.command(name='leave', help='Para fazer o bot sair do canal de voz')
async def leave(ctx):
    vc = ctx.message.guild.voice_client
    if vc.is_connected():
        await vc.disconnect()
        await ctx.send("O BOT saiu da call, para chamar novamente")
        await ctx.send("Use o comando .play + link da sua música favorita.")
    else:
        await ctx.send("O bot não está conectado a um canal de voz.")

@bot.command(name='list', help='Exibe a lista de Reprodução')
async def list(ctx):
    await ctx.send("**Em Desenvolvimento. Em breve você poderá usar.**")

if __name__ == "__main__" :
    TOKEN = config("TOKEN_SECRETO")
    bot.run(TOKEN)