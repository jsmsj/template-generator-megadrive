import re,bs4
import urllib.parse as urlparse
from urllib.parse import parse_qs
from imdb import Cinemagoer
from googlesearch import search
import PTN
import requests
from requests.structures import CaseInsensitiveDict

ia = Cinemagoer()

async def make_request(url):
    return requests.get(url)

def getIdFromUrl(link: str):
    if len(link) in [33, 19]:
        return link
    if "folders" in link or "file" in link:
        regex = r"https://drive\.google\.com/(drive)?/?u?/?\d?/?(mobile)?/?(file)?(folders)?/?d?/(?P<id>[-\w]+)[?+]?/?(w+)?"
        res = re.search(regex,link)
        if res is None:
            raise IndexError("GDrive ID not found.")
        return res.group('id')
    parsed = urlparse.urlparse(link)
    return parse_qs(parsed.query)['id'][0]


async def file_size(id):
    url = "https://drive.google.com/uc?id="+str(id)+"&export=download"
    x = await make_request(url)
    return1=bs4.BeautifulSoup(x.text, 'html.parser').find('div', id = "uc-text")
    web_page = return1.find('a')
    len1=len(str(web_page)[77:-4])
    size=str(return1)[len1+241:-291].replace("G"," GB").replace("M"," MB").replace("T"," TB")
    if "</span> is too large for" in size:
        size = size[:-94]
    if size == "":
        size = "User rate limit exceeded. Unable to get size"
    return size

async def name_of_file(url):
    if "uc?id=" in url:
        i_d = getIdFromUrl(url)
        url = "https://drive.google.com/file/d/" + i_d + "/view"
    req = await make_request(url)
    soup = bs4.BeautifulSoup(req.text, "html.parser")
    name = str(soup.title).replace("<title>","").replace("</title>","")
    if name == "Meet Google Drive – One place for all your files":
        return "Error"
    name = name[:-15]
    return name

async def send_name(url):
    initial = await name_of_file(url)
    if initial == "Error":
        name = "Can't get name"
    else:
        name = initial

    name = name.replace("."," ")
    return name

def make_url(source):
    if "https://" in source or "http://" in source:
        return source
    else:
        if source.startswith("drive.google.com"):
            sour = "https://" + source
            return sour 
        else:
            sour = "http://drive.google.com/open?id=" + source
            return sour

def get_id(url):
    try:
        source = getIdFromUrl(url)
    except IndexError:
        return f"Source id not found in {url}"
    return source

def parse_name(name):
    return PTN.parse(name)

def imdb_name(name):
    info_dict = parse_name(name)
    try:
        title = info_dict["title"]
    except:
        title=""
    try:
        year = info_dict["year"]
    except:
        year=""
    final_name = str(title) + " " + str(year)
    if final_name == "": return "Cannot find the title and year of the link provided"
    return final_name

def imdb_movie_list(name):
    return ia.search_movie(name)

def movie_title_with_year(movie):
    try:
        name =  movie['title'] + " " + str(movie['year'])
    except:
        name = movie['title']
    return name

def movie_id(movie):
    return movie.movieID

def movie_obj(movie_id):
    return ia.get_movie(str(movie_id))

def get_genre_list(imdb_movie_object):
    return imdb_movie_object.get('genres')

async def give_size(drive_url):
    url = "http://gdrivesize.jsmsj.repl.co/checksize"

    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"

    data = "{" + '"link"' + ":" + f'"{drive_url}"' + "}"

    
    try:
        resp = requests.post(url, headers=headers, data=data)
        return resp.json()['size']
    except:
        try:
            return file_size(getIdFromUrl(drive_url))
        except:
            return "Unable to get size"


def brute_imdb_link(name):
    query = name+ " site:imdb.com"
    pool = search(query, tld="com",num=1,stop=1,pause=2)
    for i in pool:
        return i

def id_from_imdblink(url):
    return url[29:36]
