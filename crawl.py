#!/usr/bin/env python
# Submission link: http://www.udacity-forums.com/cs101/answer_link/66994/

################################################################################
#
# LUPA_HTMLParser - Implements a more complete html parser for the web crawler
#
################################################################################
from HTMLParser import HTMLParser
from re import sub
import urlparse

class LUPA_HTMLParser( HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.__text = []
        # Stack of tags already found in document
        self.stack = []
        self.extracted_links = []
        self.title = []
        self.base_path = ''
        self.base_url = ''
        # HTML tags are grouped by behavior of the crawler:
        self.tags_STARTEND_IGNORE = ['br', 'col', 'hr', 'input', 'link', 'param']
        self.tags_STARTEND_ALT = ['area', 'img']
        self.tags_STARTEND_LINK = ['base', 'frame']
        self.tags_STARTEND_SPECIAL = ['meta']
        self.tags_OPEN_CLOSE = ['acronym', 'abbr', 'b', 'bdo', 'big', 'blockquote',
                                'body', 'button', 'caption', 'center', 'cite', 'code',
                                'colgroup', 'dd', 'del', 'dfn', 'dir', 'div',
                                'dl', 'dt', 'em', 'fieldset', 'font', 'form',
                                'frameset', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                                'html', 'i', 'ins', 'kbd', 'label', 'legend', 'li',
                                'map', 'menu', 'ol', 'optgroup', 'option', 'p',
                                'pre', 'q', 's', 'samp', 'select', 'small',
                                'span', 'strike', 'strong', 'sub', 'sup',
                                'table', 'tbody', 'td', 'textarea', 'tfoot',
                                'th', 'thead', 'tr', 'tt', 'u', 'ul', 'var']
        self.tags_OPEN_CLOSE_DISCARD = ['address', 'applet', 'head', 'noframes',
                                        'noscript', 'object', 'script', 'style']
        self.tags_OPEN_CLOSE_LINK = ['a', 'iframe']
        self.tags_OPEN_CLOSE_SPECIAL = ['title']

    def set_base_url(self, url):
        self.base_url = url

    def url_fix(self, url):
        link = urlparse.urlparse( url, 'http')
        if link.netloc:
            return url
        if self.base_path:
            url = urlparse.urljoin( self.base_path, url)
            link = urlparse.urlparse( url, 'http')
            if link.netloc:
                return url
        return urlparse.urljoin( self.base_url, url)

    #
    # Handles plain text content of html document
    #
    def handle_data(self, data):
        text = data.strip()
        if len(text) > 0:
            text = sub('[ \t\r\n]+', ' ', text)
            self.__text.append(text + ' ')

    #
    # Handles the start of a OPEN_CLOSE type html tags
    #
    def handle_starttag(self, tag, attrs):
        # Push state onto the parse stack
        self.stack.append([tag, attrs, self.__text])
        self.__text = []

        if not tag in self.tags_OPEN_CLOSE and         \
           not tag in self.tags_OPEN_CLOSE_LINK and    \
           not tag in self.tags_OPEN_CLOSE_SPECIAL and \
           not tag in self.tags_OPEN_CLOSE_DISCARD:
            print '[HTMLParser:]Unknown Tag:' + tag

    #
    # Handles the end of a OPEN_CLOSE type html tags
    #
    def handle_endtag(self, endtag):
        # Pops items from the stack until we find a matching start tag
        attrs = []
        while self.stack:
            text = self.__text
            tag, attrs, self.__text = self.stack.pop()
            if tag == endtag: break
            self.__text = self.__text + text
            text = []

        if endtag in self.tags_OPEN_CLOSE_DISCARD:
            self.__text = []
        elif endtag in self.tags_OPEN_CLOSE_LINK:
            # capture link in 'a'(capture link text) and 'iframe' tags:
            attrs = dict( attrs)
            self.__text = self.__text + text
            if endtag == 'a' and 'href' in attrs:
                self.extracted_links.append([self.url_fix(attrs['href']), text])
            if endtag == 'iframe' and 'src' in attrs:
                self.extracted_links.append([self.url_fix(attrs['src']), []])
        elif endtag in self.tags_OPEN_CLOSE:
            # No need to do anything in this case
            self.__text = self.__text + text
        elif endtag in self.tags_OPEN_CLOSE_SPECIAL:
            # 'title'
            if endtag == 'title':
                self.title = self.title + text
        else:
            self.__text = self.__text + text
            print '[HTMLParser:]Unknown Tag:' + tag

    #
    # Handles STARTEND type html tags
    #
    def handle_startendtag(self, tag, attrs):
        attrs = dict( attrs)
        if tag in self.tags_STARTEND_IGNORE:
            # It is ok to do nothing with those tags
            do = 'Nothing'
        elif tag in self.tags_STARTEND_ALT:
            # [ToDo:] Collect ALT text to include in the index
            do = 'Nothing'
        elif tag in self.tags_STARTEND_LINK:
            # Process 'base' and 'frame' tags
            if tag == 'frame' and 'src' in attrs:
                # [ToDo:] Do we need to check if it is HTML?
                self.extracted_links.append( [self.url_fix(attrs['src']),''])
            if tag == 'base' and 'href' in attrs:
                # [ToDo:] It would be a good idea to sanitize 'href' contents
                self.base_path = attrs['href']
        elif tag in self.tags_STARTEND_SPECIAL:
            # Found 'meta' tag, we are interested in the 'name=' author, description, keywords
            if 'name' in attrs and 'contents' in attrs:
                if attrs['name'] == 'author' or      \
                   attrs['name'] == 'description' or \
                   attrs['name'] == 'keywords':
                    # [Todo:] Add metadata to search index
                    do = 'Nothing'
        else:
            print '[HTMLParser:]Unknown Tag:' + tag

    #
    # Return results of the parsed document
    #
    def get_results(self):
        #print '[HTMLParser:] Page title:'+ ''.join(self.title).strip()
        #for link, txt in self.extracted_links:
        #    print '[HTMLParser:] Link:' + link + ' Anchor Text:' + ''.join(txt).strip()
        text = ''.join(self.__text).strip().lower()
        text = sub('[~@#$%^&*-+|:;.?!,<>()"]', ' ', text)
        text = sub('[ \t\r\n]+', ' ', text)
        return [ text, self.extracted_links, { 'title': ''.join(self.title).strip() }]




################################################################################
#
# Web crawler core logic - Based on Udacity CS-101 class exercises
#
################################################################################
import urllib
import os.path
from time import time

def get_page( url):
    try:
        html_content = urllib.urlopen(url).read()
    except:
        print '[get_page:] Failed to load url: ' + url
        return ['',[],[]]
#    try:
    parser = LUPA_HTMLParser()
    parser.set_base_url( url)
    parser.feed( html_content)
    parser.close()
    return parser.get_results()
#    except:
#        return ['',[],[]]

def union(a, b):
    #for e in b:
    #    if e not in a:
    #        a.append(e)
    a += [e for e in b if e not in a]

def add_page_to_index( index, url, content):
    words = content.split()
    for keyword in words:
        if keyword in index:
            if url not in index[keyword]:
                index[keyword].append(url)
        else:
            index[keyword] = [url]
        
#
#    get_scope( url)
#
#    computes the crawl scope based on a url
#    basically returns the complete path, excluding filename (like index.html) and whatever comes after
#    the return value of this function can be used as 'site' in the is_child function
# 
def get_scope( url):
    scope = urlparse.urlparse( url, 'http')
    loc = scope.netloc
    path = os.path.dirname( scope.path).rstrip('/').split('/')
    if not scope.netloc:
        if path[0].find('.') >= 0:
            loc = path[0]
            path = path[1:]
        else:
            # is url relative?
            return ''
    return { 'scheme': scope.scheme, 'netloc': loc, 'path': path}

#
#   is_child( site, url)    
#
#   tests if url is an hierarchical child (or at the same level) of the site
#   site is a dict of the form { 'scheme': 'http', 'netloc': 'www.python.org', 'path': ''}
#
def is_child( site, url):
    link = urlparse.urlparse( url)
    if link.netloc != site['netloc']:
        return False
    i = 0
    len_s = len(site['path'])
    p = os.path.dirname( link.path).rstrip('/').split('/')
    len_p = len(p)
    if len_p < len_s:
        return False
    while i < min( len_s, len_p):
        if not site['path'][i] == p[i]:
            return False
        i += 1
    return True

#
#   is_inscope( scope, url)    
#
#   tests if url is within the crawling scope
#
def is_inscope( scope, url):
    for s in scope:
        if is_child( s, url):
            return True
    return False
    
def crawl_web( scope, tocrawl, index, graph, url_info, limits = [-1, 0, 0.0, 1.0]): # returns index, graph of inlinks
    tocrawl_next = []    # used for depth control
    depth = 0
    pages = 0
    max_pages, max_depth, max_time, time_delay = limits

    if max_time > 0.0: start_time = time()
    while tocrawl or tocrawl_next:
        if not tocrawl:
            #
            #   Descent one more level (depth)
            #
            tocrawl = tocrawl_next
            tocrawl_next = []
            depth += 1
            if max_depth >= 0 and depth > max_depth:
                print 'Reached maximum depth. Interrupting crawler.'
                break
            
        page = tocrawl.pop(0)
        # Remove fragment portion from the url
        page = urlparse.urldefrag(page)[0]
        if not page in graph:
            pages += 1
            print 'Crawling page:', page
            if max_time != 0.0: print 'time = ', time()-start_time, ' max_time = ', max_time 
            if max_pages > 0:
                print 'Pages crawled:', pages, 'max_pages = ', max_pages

            # [ToDo:]Transform meta_data into a dictionary
            text, outlinks, meta_data = get_page( page)
            add_page_to_index( index, page, text)
            # Need to filter outlinks only to current scope
            outlinks = [ [urlparse.urldefrag(l[0])[0],l[1]] for l in outlinks if is_inscope( scope, l[0]) and (l[0].endswith('.html') or l[0].endswith('.htm')) ]
            newlinks = [ urlparse.urldefrag(l[0])[0] for l in outlinks]
            graph[page] = outlinks
            url_info[page] = meta_data
            tocrawl_next = list( set(tocrawl_next + newlinks))
            
            if pages >= max_pages:
                print 'Reached number of pages limit. Interrupting crawler.'
                break
            if max_time > 0.0 and max_time > time()-start_time:
                print 'Reached time limit. Interrupting crawler.'
                break

    tocrawl = list( set(tocrawl + tocrawl_next))
    return tocrawl, index, graph, url_info

def compute_ranks( graph):
    d = 0.8 # damping factor
    numloops = 10
    
    ranks = {}
    npages = len(graph)
    for page in graph:
        ranks[page] = 1.0 / npages
    
    for i in range(0, numloops):
        newranks = {}
        for page in graph:
            newrank = (1 - d) / npages
            for node in graph:
                # [ToDo:] Too ugly!!! Need to change data structure.
                if page in [l[0] for l in graph[node]]:
                    newrank = newrank + d * (ranks[node] / len(graph[node]))
            newranks[page] = newrank
        ranks = newranks
    return ranks

#index, graph = crawl_web('http://udacity.com/cs101x/urank/index.html')
#ranks = compute_ranks(graph)




################################################################################
#
# Program entry point:
#    - process command line arguments and start crawl process
#    - calculate page ranks
#    - save data structures in a index file
#
################################################################################
import argparse
try:
   import cPickle as pickle
except:
   import pickle
from pprint import pprint


def main():
    ##########
    #
    #  Define command line options/parameters
    #
    ##########

    cmdLine_parser = argparse.ArgumentParser( \
             description = 'Webcrawler based on Udacity CS-101 classes code. Produces an index file as output.',\
             epilog = '''
                      When no seed pages are supplied and the input index file contain no pages
                      'left to crawl' the crawler defaults to crawl: http://udacity.com/cs101x/urank/index.html
                      ''' \
    )
           
    cmdLine_parser.add_argument(                \
        'outfile',                      \
        nargs = '?',                    \
        #type = argparse.FileType('wb'),  \
        default = 'index.dat',          \
        help = 'output index file name, defaults to index.dat' \
    )

    cmdLine_parser.add_argument(     \
        '-d',                \
        default = -1,         \
        type = int,          \
        dest = 'max_depth',  \
        metavar = 'DEPTH',   \
        help = '''
               maximum crawling depth,
               starting from seed pages (and 'left to crawl' pages in the input index when specified)
               '''
    )

    cmdLine_parser.add_argument(       \
        '-i',                          \
        type=argparse.FileType('rb'),  \
        dest = 'infile',           \
        metavar = '<index file>',      \
        help = 'input index file name' \
    )

    cmdLine_parser.add_argument(       \
        '-m',                  \
        default = 10,          \
        type = int,            \
        dest = 'max_pages', \
        metavar = 'MAXPAGES',  \
        help = 'maximum number of pages to be added to index' \
    )

    cmdLine_parser.add_argument(   \
        '-r',              \
        default = 1.0,     \
        type = float,      \
        dest = 'rate', \
        metavar = 'RATE',  \
        help = 'number of pages to be requested per second (max)' \
    )

    cmdLine_parser.add_argument(          \
        '-s',                             \
        action = 'append',                \
        metavar = 'SEEDPAGE',             \
        default = [],                     \
        help = 'page to be used as seed, when not specified it defaults to http://udacity.com/cs101x/urank/index.html'  \
    )

    cmdLine_parser.add_argument(          \
        '-scope', '-sc',                  \
        dest = 'scope',                    \
        action = 'append',                \
        metavar = 'URL',                  \
        default = [],                     \
        help = '''
               defines crawling scope (pages outside the scope are not crawled),
               when not specified the crawling scope will consist of
               pages at the same directory as the seed urls and their sub-directories.
               This argument can be specified multiple times.
               '''                        \
    )

    cmdLine_parser.add_argument(     \
        '-t',                \
        default = 0,         \
        type = int,          \
        dest = 'time',       \
        metavar = 'TIME',    \
        help='time to crawl in seconds, default is 0 (no time limit)' \
    )

    args = cmdLine_parser.parse_args()
    crawl_limits = [ args.max_pages, args.max_depth, args.time, args.rate]
    
    #
    #  Read input index file
    #
    scope = []
    tocrawl = []
    index = {}
    graph = {}
    url_info = {}
    if args.infile:
        try:
            print 'Opening input index file for read...'
            scope = pickle.load( args.infile)
            tocrawl = pickle.load( args.infile)
            index = pickle.load( args.infile)
            graph = pickle.load( args.infile)
            url_info = pickle.load( args.infile)
            # [ToDo:] Is there a way to use the previous ranks as starting point/make it incrementally?
            # Do not load the ranks for now
            #ranks = pickle.load(args.infile)
            args.infile.close()
            if index: print 'Found ', len(index), 'indexed words.'
            if tocrawl: print 'Found ', len(tocrawl), 'pages left to crawl in input file.'
        except:
            print '[Error:] Cannot read input index file.'
            quit()

    #
    #  Compute seed pages and crawl scope
    #
    if args.s:
        for url in args.s:
            tocrawl.append( url)
            if not args.scope:
                scope.append( get_scope(url))
    if args.scope:
        scope = list( set( scope + args.scope))
    if not tocrawl:
        tocrawl = ['http://udacity.com/cs101x/urank/index.html']
        scope.append( get_scope('http://udacity.com/cs101x/urank/'))
    
    #
    #  Crawl
    #
    print 'Starting crawler with following parameters:'
    if args.max_pages > 0: print 'Max. Pages: ', args.max_pages
    if args.max_depth > -1: print 'Max. Depth: ', args.max_depth
    if args.time > 0.0: print 'Max. Time(s): ', args.time
    print 'Max. Rate(urls/s): ', args.rate
    tocrawl, index, graph, url_info = crawl_web( scope, tocrawl, index, graph, url_info, crawl_limits)
    print 'Computing page ranks...'
    ranks = compute_ranks(graph)
    #for p in ranks: print p,ranks[p]
    print 'Sorting index...'
    #
    #   Sort results by rank
    #
    for keyword in index:
        index[keyword].sort( key=lambda url: ranks[url], reverse=True)

    try:
        print 'Saving index to file...'
        outfile = open( args.outfile, 'wb')
        pickle.dump( scope, outfile)
        pickle.dump( tocrawl, outfile)
        pickle.dump( index, outfile)
        pickle.dump( graph, outfile)
        pickle.dump( url_info, outfile)        
        pickle.dump( ranks, outfile)
        outfile.close()
        print 'Done.'
    except:
        print '[ERROR:] Failed to save index file.'

if __name__ == '__main__':
    main()
