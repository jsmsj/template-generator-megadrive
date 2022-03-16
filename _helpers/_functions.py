import re,bs4
import urllib.parse as urlparse
from urllib.parse import parse_qs
from imdb import Cinemagoer
from googlesearch import search
import PTN
import requests
import re
from requests.structures import CaseInsensitiveDict

ia = Cinemagoer()


class GoogleDriveObject():
    def __init__(self,link,size=None):
        self.link = link
        if size:
            self.size = size
        else:
            self.size = None

    def getIdFromUrl(self):
        if len(self.link) in [33, 19]:
            return self.link
        if "folders" in self.link or "file" in self.link:
            regex = r"https://drive\.google\.com/(drive)?/?u?/?\d?/?(mobile)?/?(file)?(folders)?/?d?/(?P<id>[-\w]+)[?+]?/?(w+)?"
            res = re.search(regex,self.link)
            if res is None:
                raise IndexError("GDrive ID not found.")
            return res.group('id')
        parsed = urlparse.urlparse(self.link)
        return parse_qs(parsed.query)['id'][0]

    def full_name(self):
        try:
            query = "http://drive.google.com/open?id=" + self.getIdFromUrl()
        except IndexError:
            return "Please send Google Drive link in some other format."
        req = requests.get(query)
        soup = bs4.BeautifulSoup(req.text, "html.parser")
        name = str(soup.title).replace("<title>","").replace("</title>","")
        if name == "Meet Google Drive – One place for all your files":
            raise ValueError("Unable to get name")
        name = name[:-15]
        return name

    def name(self):
        try:
            initial_name = self.full_name()
        except IndexError:
            return "Please send Google Drive link in some other format."
        except ValueError:
            return "Unable to get name"
        final_name = initial_name.replace("."," ")
        return final_name

    def parsed_name(self):
        return PTN.parse(self.full_name())

    def main_name(self):
        info_dict = self.parsed_name()
        try:
            title = info_dict["title"]
        except:
            title=""
        try:
            year = info_dict["year"]
        except:
            year=""
        final_name = str(title) + " " + str(year)
        if final_name == "": raise ValueError("Cannot find the title and year of the link provided")
        return final_name

    def file_size_from_id(self):
        url = "https://drive.google.com/uc?id="+str(self.getIdFromUrl)+"&export=download"
        x = requests.get(url)
        return1=bs4.BeautifulSoup(x.text, 'html.parser').find('div', id = "uc-text")
        web_page = return1.find('a')
        len1=len(str(web_page)[77:-4])
        size=str(return1)[len1+241:-291].replace("G"," GB").replace("M"," MB").replace("T"," TB")
        if "</span> is too large for" in size:
            size = size[:-94]
        if size == "":
            raise ValueError("User rate limit exceeded. Unable to get size")
        return size

    def give_size(self):
        if self.size: return self.size
        url = "http://gdrivesize.jsmsj.repl.co/checksize"
        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/json"
        data = "{" + '"link"' + ":" + f'"{self.link}"' + "}"
        try:
            resp = requests.post(url, headers=headers, data=data)
            return resp.json()['size']
        except:
            try:
                return self.file_size_from_id()
            except:
                raise ValueError("Unable to get size")

class ImdbObject():
    def id_from_imdblink(self,url):
        pattern = re.compile(r"https?://(www\.)?imdb\.com/title/tt(\d+)/?")
        matches = pattern.finditer(url)
        for match in matches:
            return str(match.group(2))

    def brute_imdb_link(self,name):
        query = name+ " site:imdb.com"
        pool = search(query, tld="com",num=1,stop=1,pause=2)
        for i in pool:
            return i
    
    def imdb_movie_list(self,name):
        return ia.search_movie(name)

    def movie_title_with_year(self,movie):
        try:
            name =  movie['title'] + " " + str(movie['year'])
        except:
            name = movie['title']
        return name

    def movie_id(self,movie):
        return movie.movieID

    def movie_obj(self,movie_id):
        return ia.get_movie(str(movie_id))

    def get_genre_list(self,imdb_movie_object):
        return imdb_movie_object.get('genres')


