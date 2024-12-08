import logging, sys
logging.disable(sys.maxsize)

import time
import lucene
import os
from org.apache.lucene.store import MMapDirectory, SimpleFSDirectory, NIOFSDirectory
from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions, DirectoryReader
from org.apache.lucene.search import IndexSearcher, BoostQuery, Query
from org.apache.lucene.search.similarities import BM25Similarity
import json

lucene.initVM(vmargs=['-Djava.awt.headless=true'])

class Indexer:
    def __init__(self, fileName="final-recipes.json", directory="recipes", queryType="Directions", resultCount=10, sampleSize=0):
        self.sample_doc = json.load(open(fileName))
        self.directory = directory
        self.storeDirectory = self.directory + "/"
        self.queryType = queryType
        self.resultCount=resultCount
        self.sampleSize = sampleSize
        self.timing = 0
        self.docSize = len(self.sample_doc)

        
    def create_index(self):
        if not os.path.exists(self.directory):
            os.mkdir(self.directory)

        store = SimpleFSDirectory(Paths.get(self.directory))
        analyzer = StandardAnalyzer()
        config = IndexWriterConfig(analyzer)
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        writer = IndexWriter(store, config)

        metaType = FieldType()
        metaType.setStored(True)
        metaType.setTokenized(False)
        
        informationType = FieldType()
        informationType.setStored(True)
        informationType.setTokenized(True)
        informationType.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)
        
        contextType = FieldType()
        contextType.setStored(False)
        contextType.setTokenized(True)
        contextType.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)

        if self.sampleSize != 0:
            self.docSize = self.docSize//self.sampleSize
            self.sample_doc = self.sample_doc[:self.docSize]
            
        start = time.time()   
        for sample in self.sample_doc:
            title = sample['title']
            url = sample['url']
            ingredients = sample['ingredients']
            directions = sample['directions']
            totalTime = sample['stats'].get('totalTime', "---")
            servings = sample['stats'].get('servings', "---")
            calories = sample['stats']['nutrition'].get('calories', "---")
            carbs = sample['stats']['nutrition'].get('carbs', "---")
            fat = sample['stats']['nutrition'].get('fat', "---")
            protein = sample['stats']['nutrition'].get('protein', "---")

            doc = Document()
            
            doc.add(Field('title', str(title), informationType))
            doc.add(Field('url', str(url), metaType))
            doc.add(Field('ingredients', str(ingredients), contextType))
            doc.add(Field('directions', str(directions), contextType))
            doc.add(Field('total Time', str(totalTime), metaType))
            doc.add(Field('servings', str(servings), metaType))
            doc.add(Field('calories', str(calories), metaType))
            doc.add(Field('carbohydrates', str(carbs), metaType))
            doc.add(Field('fat', str(fat), metaType))
            doc.add(Field('protein', str(protein), metaType))
                
            writer.addDocument(doc)
        end = time.time()
        
        self.timing = (end - start)
        writer.close()


    def retrieve(self, query):
        searchDir = NIOFSDirectory(Paths.get(self.storeDirectory))
        searcher = IndexSearcher(DirectoryReader.open(searchDir))

        parser = QueryParser(self.queryType.lower(), StandardAnalyzer())
        parsed_query = parser.parse(query)

        topDocs = searcher.search(parsed_query, int(self.resultCount)).scoreDocs
        topkdocs = []
        for hit in topDocs:
            doc = searcher.doc(hit.doc)
            topkdocs.append({
                "score": hit.score,
                # "text": doc.get("Ingredients"),
                "url": doc.get("url")
            })

        print(topkdocs)

    def get_time(self):
        return self.timing
    
    def get_docSize(self):
        return self.docSize

if __name__ == "__main__":
    args = sys.argv[1::]
    config = {'filename':"final-recipes.json", 'directory':"recipes",'queryType':"Directions",
              'testing':'False', 'sampleSize':0, 'resultCount':10}
    for flag in args:
        value = flag.split("=")

        if value[1] != '':
            config[value[0]] = value[1]
    
    if config['testing'] == "True":
        docSizes = []
        times = []
        for i in range(1, int(config['sampleSize'])):
            indexer = Indexer(fileName=config['filename'],
                            directory=config['directory'],
                            queryType=config['queryType'],
                            resultCount=config['resultCount'],
                            sampleSize=i)
            indexer.create_index()
            docSizes.append(indexer.get_docSize())
            times.append(indexer.get_time())
        print("times:", times)
        print("docSize:",docSizes)
    else:
        indexer = Indexer(fileName=config['filename'],
                directory=config['directory'],
                resultCount=config['resultCount'],
                sampleSize=0)
        indexer.create_index()

    query = "quit()"

    while True:
        query = input("\nEnter your desired " + config['queryType'].lower() + " you are looking for: ")

        if query == "":
            print("Query cannot be empty.")
        elif query == "quit()":
            quit()

        indexer.retrieve(query)



