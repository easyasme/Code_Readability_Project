import cherrypy

import os
import time
import json

import colouringFunctions as cf
from greedyColouring import greedy_colouring_random, greedy_colouring_ordered, greedy_smallest_last
from DSatur import DSatur
from RLF import RLF
from exhaustive import exhaustive_colouring
from contraction import addition_contraction, deletion_contraction
from organiseGraph import organise, organiseNX
from analyseAlgorithms import algorithm_analysis


class GraphPage(object):
    @cherrypy.expose
    def index(self):
        return open('public/pages/index.html')

    @cherrypy.expose
    def compare(self):
        return open('public/pages/compare.html')
    
    @cherrypy.expose
    def analyse(self):
        return open('public/pages/analyse.html')


@cherrypy.expose
class GraphGenerationWebService(object):

    @cherrypy.tools.accept(media='text/plain')
    def GET(self):
        try:
            return cherrypy.session['edgestring']
        except KeyError:
            return ''

    def POST(self, vertices, edges):
        edge_string = cf.generate_graph(int(vertices), int(edges))
        cherrypy.session['edgestring'] = edge_string
        return edge_string


@cherrypy.expose
class GraphStringWebService(object):

    @cherrypy.tools.accept(media='text/plain')
    def GET(self):
        try:
            return cherrypy.session['edgestring']
        except KeyError:
            return ''

    def POST(self, edge_string):
        cherrypy.session['edgestring'] = edge_string
        return edge_string


@cherrypy.expose
class GraphLayoutStringWebService(object):

    @cherrypy.tools.accept(media='text/plain')
    def GET(self):
        try:
            return cherrypy.session['layoutstring']
        except KeyError:
            return ''

    def POST(self, layout_string):
        cherrypy.session['layoutstring'] = layout_string
        return layout_string


@cherrypy.expose
class GraphColouringWebService(object):

    @cherrypy.tools.accept(media='text/plain')
    def GET(self):
        return cherrypy.session['graphcolours']

    def POST(self, edge_string, algorithm, layout_string):
        start = time.time()
        if algorithm == 'greedy-random':
            colours = greedy_colouring_random(edge_string)
        elif algorithm == 'greedy-ordered':
            colours = greedy_colouring_ordered(edge_string)
        elif algorithm == 'greedy-smallest':
            colours = greedy_smallest_last(edge_string)
        elif algorithm == 'DSatur':
            colours = DSatur(edge_string)
        elif algorithm == 'RLF':
            colours = RLF(edge_string)
        elif algorithm == 'Acontraction':
            colours = addition_contraction(edge_string)
        elif algorithm == 'Dcontraction':
            colours = deletion_contraction(edge_string)
        elif algorithm == 'exhaustive':
            colours = exhaustive_colouring(edge_string)
        timetaken = time.time() - start
        print(timetaken)

        if algorithm not in ['Acontraction', 'Dcontraction']:
            if layout_string:
                forHistory = [algorithm, len(set(colours.values())), timetaken, cf.col_dict_to_string(colours), edge_string, layout_string]
                try:
                    cherrypy.session['colourhistory'].append(forHistory)
                except KeyError:
                    cherrypy.session['colourhistory'] = [forHistory]

            cherrypy.session['graphcolours'] = colours
            return cf.col_dict_to_string(colours) + '///' + str(timetaken)
        else:
            if layout_string:
                forHistory = [algorithm, colours, timetaken, [], edge_string, layout_string]
                try:
                    cherrypy.session['colourhistory'].append(forHistory)
                except KeyError:
                    cherrypy.session['colourhistory'] = [forHistory]

            return str(colours) + '///' + str(timetaken)


@cherrypy.expose
class GraphLayoutWebService(object):

    @cherrypy.tools.accept(media='text/plain')
    def GET(self):
        return cherrypy.session['graphlayout']

    def POST(self, edge_string, type):
        if type == '1':
            ordering = organise(edge_string)
        else:
            ordering = organiseNX(edge_string)

        cherrypy.session['graphlayout'] = ordering
        return ordering


@cherrypy.expose
class GraphColouringHistory(object):

    @cherrypy.tools.accept(media='text/plain')
    def GET(self):
        try:
            history = cherrypy.session['colourhistory']
        except KeyError:
            cherrypy.session['colourhistory'] = []
            return ''

        json = ''
        for colouring in reversed(history):
            colstr = ''

            colstr += '"algorithm": "' + str(colouring[0]) + '", '
            colstr += '"colours": "' + str(colouring[1]) + '", '
            colstr += '"timetaken": ' + str(colouring[2]) + ', '
            colstr += '"colouring": "' + str(colouring[3]) + '", '
            colstr += '"edgestring": "' + str(colouring[4]) + '", '
            colstr += '"layoutstring": "' + str(colouring[5]) + '"'

            json += '{' + colstr + '};'

        return json[:-1]
    
    def POST(self, history):
        cherrypy.session['colourhistory'] = history
        return history

    def DELETE(self):
        cherrypy.session['colourhistory'] = []


@cherrypy.expose
class GraphAnalysisWebService(object):

    @cherrypy.tools.accept(media='text/plain')
    def GET(self):
        return cherrypy.session['graphlayout']

    def POST(self, params):
        params = json.loads(params)
        return algorithm_analysis(int(params['graphs']), int(params['iterations']), params['algorithms'], list(map(int, params['graph_size'])), list(map(int, params['graph_density'])))


if __name__ == '__main__':
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/generator': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'text/plain')],
        },
        '/graphstring': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'text/plain')],
        },
        '/layoutstring': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'text/plain')],
        },
        '/colour': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'text/plain')],
        },
        '/history': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'text/plain')],
        },
        '/layout': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'text/plain')],
        },
        '/analysis': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'text/plain')],
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './public'
        }
    }
    webapp = GraphPage()
    webapp.generator = GraphGenerationWebService()
    webapp.graphstring = GraphStringWebService()
    webapp.layoutstring = GraphLayoutStringWebService()
    webapp.colour = GraphColouringWebService()
    webapp.history = GraphColouringHistory()
    webapp.layout = GraphLayoutWebService()
    webapp.analysis = GraphAnalysisWebService()
    cherrypy.quickstart(webapp, '/', conf)
