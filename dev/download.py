import urllib.request
from urllib.request import Request, urlopen
import sys
import urllib.parse
import time
import os
import os.path
import io

from wayback import WaybackClient


# see https://stackoverflow.com/questions/34576665/setting-proxy-to-urllib-request-python3
def set_http_proxy(proxy):
    if proxy == None: # Use system default setting
        proxy_support = urllib.request.ProxyHandler()
    elif proxy == '': # Don't use any proxy
        proxy_support = urllib.request.ProxyHandler({})
    else: # Use proxy
        proxy_support = urllib.request.ProxyHandler({'http': '%s' % proxy, 'https': '%s' % proxy})
    opener = urllib.request.build_opener(proxy_support)
    urllib.request.install_opener(opener)


# see https://stackoverflow.com/questions/16627227/problem-http-error-403-in-python-3-web-scraping
# Function to get the page content
def get_page_content(url, head=None):
    """
    Function to get the page content
    """
    if not head:
        head = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive',
        #'refere': 'https://example.com',
        #'cookie': """your cookie value ( you can get that from your web page) """
        }

    req = Request(url, headers=head)
    return urlopen(req)





class ViaClasicaAdapter:
    def __init__(self, verbose=0):
        self.adblock_log = "adblock.log"
        self.done_log = "done.log"
        self.error_log = "error.log"
        self.sleep_time = 0
        self.cache = True
        self.user_agent = "Mozilla/5.0 (Windows NT 5.1; rv:40.0) Gecko/20100101 Firefox/40.0"
        self.urls = [ 
            'http://www.viaclasica.com/aportaciones_croquis/fotos/Picos_Europa/frailecillo_lolillo.pdf'
            #'http://www.viaclasica.com/web/wp-content/uploads/2016/08/bigwaleros-perdizeros-300x300.jpg',
            #'http://www.viaclasica.com//web/wp-content/uploads/*'
            #'http://www.viaclasica.com/croquis/*'
            
            
        ]
        self.verbose = verbose

    def get_iframe_url(self, url):
        data = urllib.parse.urlparse(url)
        items = data.path.split('/')
      
        # item #2 add if_
        items[2] += "if_"
        data = data._replace(path = "/".join(items))
        new_url = urllib.parse.urlunparse(data)
        print(new_url)
        sys.exit(0)
        #https://web.archive.org/web/20160703071420if_/http://www.viaclasica.com/croquis/A1_Risco_Familia.pdf

    def get_download_url(self, url):
        data = urllib.parse.urlparse(url)
        items = data.path.split('/')
      
        # item #2 replace id_ with if_
        items[2] = items[2].replace('id_','if_')
        data = data._replace(path = "/".join(items))
        new_url = urllib.parse.urlunparse(data)
        return(new_url)

    def save_adblock_log(self, entry):
        fd = open(self.adblock_log,"a")
        fd.write("%s\n" % entry)
        fd.close()

    def save_done_log(self, entry):
        fd = open(self.done_log,"a")
        fd.write("%s\n" % entry)
        fd.close()
    
    def save_error_log(self, entry):
        fd = open(self.error_log,"a")
        fd.write("%s\n" % entry)
        fd.close()

    def download_item(self, url, cache=False):
        data = urllib.parse.urlparse(url)
        items = data.path.split('/')
        odir  = items[-2] # dir name
        fname = items[-1] # fname
        if not odir or not fname:
            return(False)
        
        out_fname = "%s/%s" % (odir, fname)
        if os.path.exists(out_fname) and cache:
            return(True)

        try:
            fd = get_page_content(url)
            data = io.BytesIO(fd.read())
            read_ok = True
        except Exception as e:
            read_ok = False
        finally:
            fd.close()

        if not read_ok:
            return(False)

        # check if we have some js
        
        if str(data.getvalue()).find('data-adblockkey') >= 0:
            print("  Warning: File is HTML and is not valid" )
            self.save_adblock_log(url)
            return(False)


        if not os.path.exists(odir):
            os.mkdir(odir)
        out_fname = "%s/%s" % (odir, fname)

        ofd = open(out_fname,"wb")
        ofd.write(data.getbuffer())
        ofd.close()
        return(True)
        
    def process(self):
        for url in self.urls:
            self.process_url(url)

    def list(self):
        for url in self.urls:
            self.list_url(url)
          
    def clean(self):
        for i in [ self.adblock_log, self.done_log, self.error_log]:
            if os.path.exists(i):
                os.remove(i)

    def process_url(self, url, limit=10000):
        client = WaybackClient()
        results = client.search(url, limit=limit)

        links_done = []

        for item in results:
            #print(item)
            try:
                memento = client.get_memento(item)
            except Exception as e:
                print("Can't get memento for %s, skipping" % item.url)
                continue
            
            if not memento.ok:
                print("Skipping %s: bad memento" % item.url)
                continue

            links = {}
            for l in memento.links:
                if l not in ['first memento', 'last memento', 'prev memento', 'next memento']:
                    continue
                #print(l, memento.links[l]['url'])
                links[memento.links[l]['url']] = memento.links[l]['url']

            links = list(links.keys())
            for link in links:
                if link in links_done:
                    continue
                links_done.append(link)
                download_url = self.get_download_url(link)
                print("Downloading: %s" % (download_url))
                if self.download_item(download_url, self.cache):
                    # continue processing another item
                    print("  -> Download OK!")
                    self.save_done_log(url)
                    break
                else:
                    print("  -> Can't download trying next")
                    self.save_error_log(url)
        
            if self.sleep_time > 0.0:
                print("sleeping: %3.3f s" % self.sleep_time)
                time.sleep(self.sleep_time)

    def list_url(self, url, limit=10000):
        client = WaybackClient()
        results = client.search(url, limit=limit)

        links_done = []

        for item in results:
            try:
                memento = client.get_memento(item)
            except Exception as e:
                print("Can't get memento for %s, skipping" % item.url)
                continue
            
            if not memento.ok:
                print("Skipping %s: bad memento" % item.url)
                continue

            links = {}
            for l in memento.links:
                if l not in ['first memento', 'last memento', 'prev memento', 'next memento']:
                    continue
                #print(l, memento.links[l]['url'])
                links[memento.links[l]['url']] = memento.links[l]['url']

            links = list(links.keys())
            for link in links:
                print(link)
        
            if self.sleep_time > 0.0:
                print("sleeping: %3.3f s" % self.sleep_time)
                time.sleep(self.sleep_time)       

#  pip3 install wayback

if __name__ == "__main__":

    vc = ViaClasicaAdapter()
    vc.clean()
    #vc.list()
    vc.process()