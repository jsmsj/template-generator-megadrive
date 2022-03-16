"""Importing Modules"""
from _helpers import secrets
from _helpers._functions import *
import discord
from discord.ext import commands

intents = discord.Intents.default()

bot = commands.Bot(command_prefix=secrets.prefix, intents=intents,help_command=None)
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name=f"{secrets.prefix}info"))
    print("Bot is ready!")

"""
`genre1 | genre2 | genre3 | genre4 | genre5`
:drive: Name with spaces

> Size: XX GB
> Link: https://drive.google.com/xxxxx

https://imdb.com/title/ttxxxxxx
"""

@bot.command()
@commands.max_concurrency(1,per=commands.BucketType.default,wait=False)
async def template(ctx,google_drive_link=None,actual_imdb_link=None,actual_size=None):
    if not google_drive_link: return await ctx.send(f"Please provide Google Drive Link. Run `{secrets.prefix}info template` for syntax.")
    async with ctx.typing():
        drive_obj = GoogleDriveObject(google_drive_link,actual_size)
        imdb_obj = ImdbObject()
        if not actual_imdb_link:
            async with ctx.typing():
                try:
                    search_name_for_imdb = drive_obj.main_name()
                except ValueError:
                    return await ctx.send(f"Please provide imdb link as well. Run `{secrets.prefix}info template` for syntax.")
                try:
                    list_of_movies = imdb_obj.imdb_movie_list(search_name_for_imdb)
                except:
                    return await ctx.send(f"Please provide imdb link as well. Run `{secrets.prefix}info template` for syntax.")
                if len(list_of_movies) == 0 :
                    try:
                        linkk = imdb_obj.brute_imdb_link(search_name_for_imdb)
                        if linkk:
                            mov_id = imdb_obj.id_from_imdblink(imdb_obj.brute_imdb_link(search_name_for_imdb)).replace(" ","")
                        else:
                            return await ctx.send(f"Please provide imdb link as well. Run `{secrets.prefix}info template` for syntax.")
                        if mov_id == "": return await ctx.send(f"Please provide imdb link as well. Run `{secrets.prefix}info template` for syntax.")
                    except:
                        return await ctx.send(f"Please provide imdb link as well. Run `{secrets.prefix}info template` for syntax.")
                    imdb_id = mov_id
                else:
                    new_movie_ls = []
                    i=1
                    for movie in list_of_movies:
                        new_movie_ls.append(f"{i}. {imdb_obj.movie_title_with_year(movie)}")
                        i+=1
                    temp = '\n'.join(new_movie_ls)[-1989::]
                    movie_list_msg = await ctx.send(f"```\n{temp}\n```")
                    await ctx.send("Choose the index number of the name of the series/movie\nEg: reply 2 for the second value\nIf your movie/show is not in the list reply none")
                    def check(m):
                        return m.author == ctx.author
                    msg = await bot.wait_for('message', check=check)
                    try:
                        index = int(msg.content) - 1
                    except:
                        if msg.content.lower() == "none":
                            linkk = imdb_obj.brute_imdb_link(search_name_for_imdb)
                            if linkk:
                                mov_id = imdb_obj.id_from_imdblink(imdb_obj.brute_imdb_link(search_name_for_imdb)).replace(" ","")
                            else:
                                return await ctx.send(f"Please provide imdb link as well. Run `{secrets.prefix}info template` for syntax.")
                            if mov_id == "":
                                return await ctx.send(f"Please provide imdb link as well. Run `{secrets.prefix}info template` for syntax.")
                            else:
                                imdb_id = mov_id
                        else:
                            return await ctx.send("You have to enter an integer for the index number !!")
                    try:
                        try:
                            final_movie = list_of_movies[index]
                        except:
                            if not msg.content.lower() == "none": return await movie_list_msg.reply("You have entered the index number which is not in this list")
                        imdb_id = imdb_obj.movie_id(final_movie)
                    except:
                        pass
            async with ctx.typing():
                list_of_genres = imdb_obj.get_genre_list(imdb_obj.movie_obj(imdb_id))
                if len(list_of_genres) ==0: list_of_genres = ['No Genre Found']
                try:
                    name_string = drive_obj.name()
                except:
                    name_string = "Unable to get name"
                genre_string = f"`{' | '.join(list_of_genres)}`"
                try:
                    sizeee = drive_obj.give_size()
                except ValueError:
                    sizeee = "Unable to get size"
                size_string = f"> Size: **{sizeee}**"
                link_string = f"> Link: <{google_drive_link}>"
                imdb_link_string = f"https://www.imdb.com/title/tt{imdb_id}"

                ultimate = genre_string + "\n" + ":drive: " + name_string + "\n\n" + size_string + "\n" + link_string + "\n\n" + imdb_link_string
                await ctx.send(f"Preview:\n\n{ultimate}")
                await ctx.send(f"Copy paste this:\n```\n{ultimate}\n```")
                return    
        else:
            async with ctx.typing():
                mov_id = imdb_obj.id_from_imdblink(actual_imdb_link)
                list_of_genres = imdb_obj.get_genre_list(imdb_obj.movie_obj(mov_id))
                if len(list_of_genres) ==0: list_of_genres = ['No Genre Found']
                name_string = drive_obj.name()
                genre_string = f"`{' | '.join(list_of_genres)}`"
                try:
                    sizeee = drive_obj.give_size()
                except ValueError:
                    sizeee = "Unable to get size"
                size_string = f"> Size: **{sizeee}**"
                link_string = f"> Link: <{google_drive_link}>"
                imdb_link_string = actual_imdb_link

                ultimate = genre_string + "\n" + ":drive: " + name_string + "\n\n" + size_string + "\n" + link_string + "\n\n" + imdb_link_string

                await ctx.send(f"Preview:\n\n{ultimate}")
                await ctx.send(f"Copy paste this:\n```\n{ultimate}\n```")

@template.error
async def temp_error(ctx,error):
    if isinstance(error, commands.MaxConcurrencyReached):
        return await ctx.reply('An instance of this command is already running. Please wait for it to finish.')

@bot.group(invoke_without_command=True)
async def info(ctx):
    em = discord.Embed(title="Megadrive Template Generator",description="This bot will generate posting template for movies/series. You just need to input the gdrive link. Rest will be handled by the bot.\nHosted on Heroku.",color=discord.Color.green())
    em.add_field(name="Made Bye",value="jsmsj#5252\n(DMs Open for recommendations.)")
    em.add_field(name="Commands",value=f"`{secrets.prefix}template`\n`{secrets.prefix}info template`\n`{secrets.prefix}info`")
    em.add_field(name="Repository Link",value="[GitHub](https://github.com/jsmsj/template-generator-megadrive)")
    await ctx.send(embed=em)
    
@info.command()
async def template(ctx):
    em = discord.Embed(title="Info for `template` command",description="Generate template for posting on megadrive using this command.",color=discord.Color.random())
    em.add_field(name="Syntax",value=f"```fix\n{secrets.prefix}template <drive_link> [imdb_link] [size]\n```",inline=False)
    em.add_field(name="Examples", value=f"```fix\n{secrets.prefix}template https://drive.google.com/file/d/1Q-niQVk91hDoTzXFFymSKaSrR32Is9x2/view?usp=sharing\n```\n```fix\n{secrets.prefix}template https://drive.google.com/file/d/1Q-niQVk91hDoTzXFFymSKaSrR32Is9x2/view?usp=sharing https://www.imdb.com/title/tt1129442\n```\n```fix\n{secrets.prefix}template https://drive.google.com/file/d/1Q-niQVk91hDoTzXFFymSKaSrR32Is9x2/view?usp=sharing https://www.imdb.com/title/tt1129442 55.71GB\n```\n")
    em.add_field(name="Note:",value="The size which is automatically detected by the bot does not happens for folders for now.",inline=False)
    em.set_footer(text="Parameters in <> are required, while in [] are optional")
    await ctx.send(embed=em)

bot.run(secrets.bot_token)