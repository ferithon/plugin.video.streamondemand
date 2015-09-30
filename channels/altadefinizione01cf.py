# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canal para altadefinizione01
# http://blog.tvalacarta.info/plugin-xbmc/streamondemand.
# ------------------------------------------------------------
import urlparse
import re
import sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "altadefinizione01"
__category__ = "F,S,A"
__type__ = "generic"
__title__ = "AltaDefinizione01"
__language__ = "IT"

sito = "http://www.altadefinizione01.com/"

headers = [
    ['Host','www.altadefinizione01.com'],
    ['User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:38.0) Gecko/20100101 Firefox/38.0'],
    ['Accept-Encoding', 'gzip, deflate'],
    ['Referer', 'https://www.google.com'],
    ['Cookie','__cfduid=dac9bb25ed00a859a9110ef6b704de05d1443568760; cf_clearance=769e9603f6ce90d193236d954e3eb83e6f5c1d47-1443568764-604800; _ga=GA1.2.1244324045.1443568764; _gat=1; __atuvc=1%7C39; __atuvs=560b1da67eedd20a000'],
    ['Connection', 'keep-alive']
]

DEBUG = config.get_setting("debug")


def isGeneric():
    return True


def mainlist(item):
    logger.info("streamondemand.altadefinizione01 mainlist")

    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Ultimi film inseriti[/COLOR]",
                     action="peliculas",
                     url=sito,
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film Sub-Ita[/COLOR]",
                     action="peliculas",
                     url=sito+"genere/sub-ita/",
                     thumbnail="http://i.imgur.com/qUENzxl.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Categorie film[/COLOR]",
                     action="categorias",
                     url=sito,
                     thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/All%20Movies%20by%20Genre.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca...[/COLOR]",
                     action="search",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search")]

    return itemlist


def peliculas(item):
    logger.info("streamondemand.altadefinizione01 peliculas")
    itemlist = []

    # Descarga la pagina
    data = anti_cloudflare(item.url)

    ## ------------------------------------------------
    cookies = ""
    matches = re.compile( '(.altadefinizione01.com.*?)\n', re.DOTALL ).findall( config.get_cookie_data() )
    for cookie in matches:
        name = cookie.split( '\t' )[5]
        value = cookie.split( '\t' )[6]
        cookies+= name + "=" + value + ";"
    headers.append( ['Cookie',cookies[:-1]] )
    import urllib
    _headers = urllib.urlencode( dict( headers ) )
    ## ------------------------------------------------

    # Extrae las entradas (carpetas)
    patron = '<a\s+href="([^"]+)"\s+title="[^"]*">\s+<img\s+width="[^"]*"\s+height="[^"]*"\s+src="([^"]+)"\s+class="[^"]*"\s+alt="([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        html = scrapertools.cache_page(scrapedurl)
        start = html.find("<div class=\"aciklama\">")
        end = html.find("<div class=\'bMavi\'>Titolo originale:", start)
        scrapedplot = html[start:end]
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle.replace("Streaming", ""))
        scrapedplot = re.sub(r'<[^>]*>', '', scrapedplot)
        scrapedplot = scrapertools.decodeHtmlentities(scrapedplot)
        if DEBUG: logger.info("title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        scrapedthumbnail+= "|" + _headers
        itemlist.append(
            Item(channel=__channel__,
                 action="findvid",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 viewmode="movie_with_plot",
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True))

    # Extrae el paginador
    patronvideos = 'class="nextpostslink" rel="next" href="([^"]+)">&raquo;'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png",
                 folder=True))

    return itemlist


def categorias(item):
    logger.info("streamondemand.altadefinizione01 categorias")
    itemlist = []

    data = anti_cloudflare(item.url)
    logger.info(data)

    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data, '<ul class="kategori_list">(.*?)</ul>')

    # The categories are the options for the combo  
    patron = '<li><a href="([^"]+)">([^<]+)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for url, titulo in matches:
        scrapedtitle = titulo
        scrapedurl = urlparse.urljoin(item.url, url)
        scrapedthumbnail = ""
        scrapedplot = ""
        if DEBUG: logger.info("title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot))

    return itemlist


def search(item, texto):
    logger.info("[altadefinizione01.py] " + item.url + " search " + texto)
    item.url = "%sindex.php/?s=%s" % (sito, texto)
    try:
        return peliculas(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def findvid(item):
    logger.info("[altadefinizione01.py] findvideos")

    ## Descarga la página
    data = anti_cloudflare(item.url)
    data = scrapertools.find_single_match(data, "(eval.function.p,a,c,k,e,.*?)\s*</script>")
    if data != "":
        from core import unpackerjs3
        data_unpack = unpackerjs3.unpackjs(data)
        if data_unpack == "":
            from lib.jsbeautifier.unpackers import packer
            data_unpack = packer.unpack(data)

        itemlist = servertools.find_video_items(data=data_unpack.replace(r'\\/', '/'))

        for videoitem in itemlist:
            videoitem.title = "".join([item.title, videoitem.title])
            videoitem.fulltitle = item.fulltitle
            videoitem.thumbnail = item.thumbnail
            videoitem.channel = __channel__
    else:
        itemlist = servertools.find_video_items(item=item)

    return itemlist

def anti_cloudflare(url):
    # global headers

    try:
        resp_headers = scrapertools.get_headers_from_response(url, headers=headers)
        resp_headers = dict(resp_headers)
    except urllib2.HTTPError, e:
        resp_headers = e.headers

    if 'refresh' in resp_headers:
        time.sleep(int(resp_headers['refresh'][:1]))

        # dict_headers = {v[0]: v[1] for v in headers}
        # dict_headers['cookie'] = resp_headers['set-cookie'].split(';')[0]

        # resp_headers = scrapertools.get_headers_from_response(sito + resp_headers['refresh'][7:], headers=[[k, v] for k, v in dict_headers.iteritems()])
        scrapertools.get_headers_from_response(sito + resp_headers['refresh'][7:], headers=headers)
        # resp_headers = {v[0]: v[1] for v in resp_headers}

        # dict_headers['cookie'] = dict_headers['cookie'] + resp_headers['set-cookie'].split(';')[0]
        # headers = [[k, v] for k, v in dict_headers.iteritems()]

    return scrapertools.cache_page(url, headers=headers)
