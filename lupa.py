#!/usr/bin/env python
# Submission link: http://www.udacity-forums.com/cs101/answer_link/66994/

#
#   HTML Template for search page
#
template_search_page = {
'header' :'''
<!doctype html>
<html lang="en-US">
  <head>
    <link rel="stylesheet" type="text/css" href="lupa.css" />
    <title>Lupa! Search</title>
  </head>
  <body>
    <div id="bd" class="sd" >
      <ul id="tabs">
''',
'tab_on_open' :'        <li class=" on">',
'tab_open' :'        <li class="">',
'tab_close' :'</li>',
'search_box' :'''      </ul>
      <form id="sf" action="/search.py" accept-charset="utf-8">
        <div id="sbx" class="shl-reg">
          <input type="text" id="srchtxt" class="sd" name="srch" value="''',
'search_box_complete' :'''" autocomplete="off" autofocus>
          <input type="submit" id="srchbt" value="Search">
        </div>
      </form>
    </div>''',
'pgs_open': '''    <div id="results">
      
      <div id="pgs">''',
'pgs_mid': '''      </div>
      <font color=#A0C0A0>''',
'pgs_close': '''</font><br>
    </div>''',
'footer' :'''    <div id="ft">
      <span>License:</span>
      <ul>
        <li><a>About <b>Lupa!</b> Search</a></li>
        <li><a href="https://github.com/edevaldo/cs101-lupa">Get <b>Lupa!</b> Source Code</a></li>
        <li><a href="http://www.udacity.com/overview/Course/cs101">Udacity - CS101 - Building a Search Engine</a></li>
      </ul>
    </div>
  </body>
</html>'''}

from time import time
from re import sub

#
#   clean_str( query)
#
def clean_str( s):
    return sub('[ \t\r\n]+', ' ', sub('[~@#$%^&*-+|:;.?!,<>()"]', ' ', s.strip().lower()))

#
#   process_query_str( query)
#
#       returns a list containing the cleaned up search terms
#       exact phrase searches are returned as a sub list of search terms
#
def process_query_str( query):
    result = []
    i, quote = [0, False]
    while True:
        j = query.find( '"', i)
        if j < 0:
            s = clean_str( query[i:]).split()
        else:
            s = ''
            if j > i: s = clean_str( query[i:j]).split()
            i = j+1
        if s:
            if quote: result += [s]
            else:     result += s
        if j < 0: break
        else:     quote = not quote
    return result

#
#   This file implements a very simple webserver based on Python standar library code
#
import string, cgi, urlparse, urllib
import os
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

#
#   Performs a lookup for a single keyword
#
def keyword_lookup( keyword, idx=0):
    l = 0
    if keyword in index:
        result = index[keyword]
        #result = sorted(result, key=lambda url: ranks[url], reverse=True)
        l = len(result)
        if l > idx + 1:
            return [result[idx:min(l,idx+10)], l]
        else: return [None, l]
    else: return [None, l]
    
def lookup( s_terms, idx=0):
    results = []
    lookups = []
    for term in s_terms:
        if isinstance( term, list):
            for k in term:
                if k in index:
                    lookups.append( index[k])
        else:
            if term in index:
                lookups.append( index[term])
        print term
    if len(lookups) == 0:
        return None, 0
    min_sz = -1
    look_min_sz = 0
    for i in range(len(lookups)):
        if min_sz > len(lookups[i]) or min_sz == -1:
            min_sz = len(lookups[i])
            look_min_sz = i
    for result in lookups[look_min_sz]:
        for j in range(len(lookups)):
            if look_min_sz == j: continue
            if not result in lookups[j]:
                break
        results.append(result)
    l = len(results)
    if l == 0: return None, 0
    if l > idx + 1:
        return results[idx:min(l,idx+10)], l

class LupaHandler( BaseHTTPRequestHandler):

    def do_GET(self):
        scheme, netloc, path, params, query, frag = urlparse.urlparse(self.path)
        query = urllib.unquote_plus(query)
        print 'GET request:\n    scheme:' + scheme + '\n    netloc:' + netloc
        print '    path:' +  path + '\n    params:' + params
        print '    query:' + query + '\n    frag:' + frag

        if query:
            query = urlparse.parse_qs(query)
            if 'srch' in query:
                s_terms = process_query_str( query['srch'][0])
                print 's_terms: ', s_terms
            else: query['srch'] = ['']
        else: query = { 'srch': ['']}

        req_type = 'unknown'        
        if path=="/" or path==""  or path.endswith(".py"):
            req_type = 'dynamic'
            
        if path.endswith(".html"):
            req_type = 'static'
            mime = 'text/html'
        elif path.endswith(".css"):
            req_type = 'static'
            mime = 'text/css'
        elif path.endswith(".txt"):
            req_type = 'static'
            mime = 'text/plain'
        
        search_scope = urlparse.urlunparse( (scope[0]['scheme'], scope[0]['netloc'], '/'.join(scope[0]['path']), '', '', ''))
        try:
            if req_type == 'static' or path.endswith("/favicon.ico"):
                f = open(os.getcwd() + os.sep + 'html' + os.sep + self.path)
                self.send_response(200)
                self.send_header('Content-type', mime)
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                return
            
            #
            #   Builds dynamic pages
            #
            if req_type == 'dynamic':
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                html_result = template_search_page['header']
                html_result += template_search_page['tab_on_open'] + 'Search: ' + search_scope + template_search_page['tab_close']
                html_result += template_search_page['tab_open'] + '<a href="help.txt">Search Help</a>' + template_search_page['tab_close']
                html_result += template_search_page['search_box']
                html_result += query['srch'][0]
                html_result += template_search_page['search_box_complete']
                if not query['srch'] == ['']:
                    s_time = time()
                    html_result += '    <div id="results">'
                    #
                    #   Performs the real search:
                    #
                    result, nresults = lookup(s_terms)
                    if result:
                        for url in result:
                            html_result += '      <li><div class="res"><div><h3><a href="'
                            html_result += url
                            html_result += '" class="resttl spt">'
                            html_result += url_info[url]['title']
                            html_result += '</a></h3></div><span class="url">'
                            html_result += url
                            html_result += '</span><br></div></li>'
                    html_result += '    </div>'
                    html_result += template_search_page['pgs_open']
                    html_result += template_search_page['pgs_mid']
                    s_time = time() - s_time
                    html_result += 'Found ' + str(nresults) + ' results in ' + ('%0.2e' % s_time) + ' seconds'
                    html_result += template_search_page['pgs_close']
                html_result += template_search_page['footer']       
                self.wfile.write( html_result)
                return

            if req_type == 'unknown':
                self.send_error( 404, 'File Not Found: %s' % self.path)

            return

        except IOError:
            self.send_error( 404, 'File Not Found: %s' % self.path)


    def do_POST(self):
        global rootnode
        print 'POST requesto to:' + self.path
        try:
            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
            if ctype == 'multipart/form-data':
                query = cgi.parse_multipart( self.rfile, pdict)
            self.send_response(301)

            self.end_headers()
            upfilecontent = query.get('upfile')
            print "filecontent", upfilecontent[0]
            self.wfile.write( "<HTML>POST OK.<BR><BR>")
            self.wfile.write( upfilecontent[0])

        except:
            pass

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

#
#   Keep indexing data as globals for now
#
scope = []
tocrawl = []
index = {}
graph = {}
ranks = {}
url_info = {}

def main():
    global scope
    global tocrawl
    global index
    global graph
    global ranks
    global url_info
    
    ##########
    #
    #  Define command line options/parameters
    #
    ##########

    cmdLine_parser = argparse.ArgumentParser( \
             description = 'Lupa! search engine based on Udacity CS-101 classes code. Reads an index file and provides search result tough http.',\
             epilog = '''
                      Hit ctrl-C to gracefully stop the server.
                      ''' \
    )
           
    cmdLine_parser.add_argument(        \
        'indexfile',                    \
        nargs = '?',                    \
        type = argparse.FileType('rb'), \
        default = 'index.dat',          \
        help = 'index file used for searches, defaults to index.dat' \
    )

    cmdLine_parser.add_argument(     \
        '-p',                \
        default = 8080,      \
        type = int,          \
        dest = 'http_port',  \
        help = '''
               defines tcp port where search results will be served,
               '''
    )
    
    args = cmdLine_parser.parse_args()

    #
    #  Read input index file
    #
    try:
        print 'Opening input index file for read...'
        scope = pickle.load(args.indexfile)
        tocrawl = pickle.load(args.indexfile)
        index = pickle.load(args.indexfile)
        graph = pickle.load(args.indexfile)
        url_info = pickle.load(args.indexfile)
        ranks = pickle.load(args.indexfile)
        args.indexfile.close()
        if index and graph and ranks:
            print 'Found ', len(index), 'indexed terms, and ', len(graph), 'indexed pages in database.'
    except:
        print '[Error:] Cannot read input index file.'
        quit()

    #
    #  Start http server
    #
    try:
        server = HTTPServer(('',args.http_port), LupaHandler)
        print 'Current directory: ', os.getcwd()
        print 'Started Lupa! Search httpserver...'
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C siginal received, shutting down server'
        server.socket.close()

if __name__ == '__main__':
    main()

