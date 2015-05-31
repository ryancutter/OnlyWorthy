#!/usr/bin/env python

"""
onlyworthy_dev.py
~~~~~~~~~~~~~
Find relevant tweets by bootstrapping a text mining application using a lucene index. Relevancy based on cosine-
similarity and BM25 algorithms using pre-determined desired tweets.
"""

INDEX_DIR = "OnlyWorthy.index"

from lucene import initVM
from os import path, mkdir
from sys import argv
from getopt import getopt, GetoptError
from csv import reader
from datetime import datetime, timedelta
from logging import basicConfig, getLogger, INFO
from operator import mul, itemgetter
from math import sqrt, log
import twitter_apps, tweepy

from java.io import File
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.index import FieldInfo, IndexReader, IndexWriter, IndexWriterConfig, MultiFields
from org.apache.lucene.search import IndexSearcher, TopScoreDocCollector
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene import util
from org.apache.lucene.search.similarities import BM25Similarity

class DocVector():
    """ TF-IDF term vectors for a single doc. """

    def __init__(self, terms_dict, idf_dict):
        self.terms_dict = terms_dict
        self.idf_dict = idf_dict
        self.vector = dict((k, 0) for k in range(len(terms_dict)))

    def set_entry(self, term, tf):
        """ set vector position to tf-idf value. """

        if term in self.terms_dict:
            pos = self.terms_dict.get(term)
            self.vector[pos] = tf * self.idf_dict[term]

class CosineSimilarityScorer():
    """ Calculate cosine-similarity scores of all tweets versus a single, liked tweet. """

    def __init__(self, doc_vector, reader, searcher, tweets):
        self.doc_vector = doc_vector
        self.reader = reader
        self.searcher = searcher
        self.tweets = tweets

    def get_cosine_similarity(self, d1, d2):
        """ compute cosine similarity of 2 vectors. dot product of vectors / (L2 norm of vector1 * L2 norm of vector2). """

        return sum(map(mul, d1, d2)) / (self.get_norm(d1) * self.get_norm(d2))

    def get_norm(self, d):
        """ compute L2 norm of a vector. """

        d_norm = 0
        for v in d:
            d_norm += v * v
        return sqrt(d_norm)

    def get_scores(self, fav_doc):
        """ compare cosine similarities of each tweet to another tweet and return dict of all scores.  """

        scores = {}
        for i in range(0, self.reader.maxDoc()):
            if i == fav_doc: continue

            # sometimes duplicate tweets get sent out which will cause false positives so skip those
            if self.searcher.doc(fav_doc).get("contents") == self.searcher.doc(i).get("contents"):
                scores[i] = 0
                continue

            # calculate cosine similarity of these 2 documents and determine if this is a new leader
            cs = self.get_cosine_similarity(self.doc_vector[fav_doc].vector.values(), self.doc_vector[i].vector.values())

            # if sender is the same, issue 10% penalty
            source_penalty = 0.0
            if self.tweets[fav_doc][1].source == self.tweets[i][1].source:
                source_penalty = 0.1

            # if tweets were sent within 2 hours of eachother, issue 20% penalty
            time_penalty = 0.0
            time_delta = abs((self.tweets[fav_doc][1].created_at - self.tweets[i][1].created_at).total_seconds())
            if time_delta < 7200:
                time_penalty = 0.2

            # determine final cs score for these 2 tweets
            scores[i] = cs * (1 - (source_penalty + time_penalty))

        return scores

class BM25Scorer(object):
    """ Calculate BM25 similarity scores of all tweets versus a single, liked tweet. """

    def __init__(self, doc_vectors, searcher, queryparser):
        self.doc_vectors = doc_vectors
        self.searcher = searcher
        self.queryparser = queryparser

    def get_scores(self, fav_doc):
        """ identify important terms from a liked tweet, determine similarity scores of these terms against all other
         tweets and return dict of all scores.  """

        bm25_scores = {}
        doc_vector = self.doc_vectors[fav_doc]

        # get the 3 most significant terms from favorite tweet then get similar tweets via BM25
        top_terms = dict(sorted(doc_vector.vector.iteritems(), key=itemgetter(1), reverse=True)[:3])
        for key, value in top_terms.iteritems():
            actual_term = doc_vector.terms_dict.keys()[doc_vector.terms_dict.values().index(key)]

            # set up and run query against index
            query = self.queryparser.parse(actual_term)
            collector = TopScoreDocCollector.create(6, True)
            self.searcher.search(query, collector)
            hits = collector.topDocs().scoreDocs

            for hit in hits:
                # skip if this is the favorite tweet being examined
                if hit.doc == fav_doc: continue

                if hit.doc not in bm25_scores:
                    bm25_scores[hit.doc] = 0.0

                # note the final score is weighted depending on top term IDF significance
                bm25_scores[hit.doc] += value * hit.score

        return bm25_scores

class IndexTweets(object):
    """ index the tweets and run the comparisons. """

    def __init__(self, tweets, storeDir, analyzer):

        # first, index the tweets
        if not path.exists(storeDir):
            mkdir(storeDir)

        store = SimpleFSDirectory(File(storeDir))
        analyzer = LimitTokenCountAnalyzer(analyzer, 1048576)
        config = IndexWriterConfig(Version.LUCENE_CURRENT, analyzer)
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        writer = IndexWriter(store, config)

        self.index_docs(tweets, writer)
        writer.commit()
        writer.close()

        # set up IndexSearcher
        reader = IndexReader.open(store)
        n_docs = reader.numDocs()
        searcher = IndexSearcher(reader)
        searcher.setSimilarity(BM25Similarity())
        queryparser = QueryParser(Version.LUCENE_CURRENT, "contents", StandardAnalyzer(Version.LUCENE_CURRENT))

        # create document vectors
        doc_vectors = self.get_doc_vectors(reader, tweets, n_docs)

        cs_scorer = CosineSimilarityScorer(doc_vectors, reader, searcher, tweets)
        bm25_scorer = BM25Scorer(doc_vectors, searcher, queryparser)

        # find relevant tweets
        for fav_doc in (1, 26, 51):
            cs_scores = cs_scorer.get_scores(fav_doc)
            bm25_scores = bm25_scorer.get_scores(fav_doc)

            top_cs_scores = dict(sorted(cs_scores.iteritems(), key=itemgetter(1), reverse=True)[:5])
            top_bm25_scores = dict(sorted(bm25_scores.iteritems(), key=itemgetter(1), reverse=True)[:5])

            # print "top_cs_scores", top_cs_scores
            # print "top_bm25_scores", top_bm25_scores

            # calculate composite score by multiplying cs scores by 100 and keeping bm25 scores as is.
            # cs is bounded from 0.0-1.0. bm25 scores is actually idf * bm25_similarity_score so values
            # above 10.0 are not uncommon
            top_blended_scores = {}
            for key, value in top_cs_scores.iteritems():
                top_blended_scores[key] = value * 100.0

            for key, value in top_bm25_scores.iteritems():
                if key not in top_blended_scores:
                    top_blended_scores[key] = 0.0
                top_blended_scores[key] += value

            top_score = dict(sorted(top_blended_scores.iteritems(), key=itemgetter(1), reverse=True)[:1])

            # print "\n"
            # print "results for", fav_doc
            # print tweets[fav_doc]
            print searcher.doc(fav_doc).get("contents")
            print top_score

            # if the top score fails to reach 10.0, this result is probably not of high quality so onlyworthy
            # will decline to identify a relevant match
            if top_score.values()[0] < 10.0:
                print "skipping"
                continue

            # print tweets[top_score.keys()[0]]
            print searcher.doc(top_score.keys()[0]).get("contents")
            print "\n"

    def get_dicts(self, reader, tweets, num_docs):
        """ investigate index by constructing term dict (term,id) and idf dict (term,idf_val). """

        terms_dict = {}
        idf_dict = {}
        terms_ctr = 0

        # iterate over each term in index
        term_enum = MultiFields.getTerms(reader, "contents").iterator(None)
        for bytes_ref in util.BytesRefIterator.cast_(term_enum):
            s = bytes_ref.utf8ToString()
            terms_dict[s] = terms_ctr
            terms_ctr += 1

            # count occurences of this term in the index and calculate idf
            doc_presence_ctr = 0
            for tweet in tweets:
                if s in tweet[1].text.lower():
                    doc_presence_ctr += 1

            idf_dict[s] = log(float(num_docs) / doc_presence_ctr, 10)

        return terms_dict, idf_dict

    def get_doc_vectors(self, reader, tweets, num_docs):
        """ plot each document in a vector space. """

        terms_dict, idf_dict = self.get_dicts(reader, tweets, num_docs)

        doc_vectors = []
        liveDocs = MultiFields.getLiveDocs(reader)
        for i in range(0, reader.maxDoc()):
            if liveDocs is not None and not liveDocs.get(i): continue

            doc_vectors.append(DocVector(terms_dict, idf_dict))

            tfvs = reader.getTermVector(i, "contents")
            terms_enum = tfvs.iterator(None)
            for bytes_ref in util.BytesRefIterator.cast_(terms_enum):
                doc_vectors[i].set_entry(bytes_ref.utf8ToString(), terms_enum.totalTermFreq())

        return doc_vectors

    def index_docs(self, tweets, writer):
        t1 = FieldType()
        t1.setIndexed(True)
        t1.setStored(True)
        t1.setTokenized(True)
        t1.setIndexOptions(FieldInfo.IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)
        t1.setStoreTermVectors(True)
        t1.setStoreTermVectorOffsets(True)

        # add each tweet to the index
        for tweet in tweets:
            try:
                # strip out URLs because they provide false index matches
                contents = []
                for word in tweet[1].text.split():
                    if word.startswith("http://") or word.startswith("https://"):
                        continue
                    contents.append(word)
                contents = " ".join(contents)

                if len(contents) == 0: continue

                doc = Document()
                doc.add(Field("contents", contents, t1))
                writer.addDocument(doc)
            except Exception, e:
                print "Failed in index_docs:", e

def evaluate_tweets(tweets, stop_time, start_time):
    """ cut down raw list of tweets to those in desired time window and grab some analytics. """

    scored_tweets = []
    for tweet in tweets:
        # skip if outside window
        if tweet.created_at > stop_time or tweet.created_at < start_time: continue

        score = tweet.favorite_count + tweet.retweet_count
        scored_tweets.append((score, tweet))

    # sort by score, descending
    scored_tweets.sort(key=lambda tup: tup[0], reverse=True)
    return scored_tweets

def get_worthy_tweets(logger, config_file, twitter_api):
    """ collect all tweets from an identified list of twitter accounts. """

    # create a 50 hour window ending 2 hours ago
    now = datetime.utcnow()
    stop_time = now - timedelta(hours=2)
    start_time = now - timedelta(hours=50)
    logger.info("stop_time = " + str(stop_time) + ", start_time = " + str(start_time))

    worthy_tweets = []
    for config in get_config(config_file):
        logger.info("Pulling @" + config[0])
        # to prevent a weird situation, only the 100 most recent tweets are pulled
        tweets = twitter_api.user_timeline(screen_name=config[0], count=100, include_rts=False)

        scored_tweets = evaluate_tweets(tweets, stop_time, start_time)
        logger.info("Narrowed " + str(len(tweets)) + " down to " + str(len(scored_tweets)))

        worthy_tweets.extend(scored_tweets)

    return worthy_tweets

def setup_logger(log, app):
    """ just some basic logging setup. """

    basicConfig(level=INFO,
              format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
              datefmt='%m-%d-%y %H:%M:%S',
              filename=log,
              filemode='w')
    return getLogger(app)

def get_config(config_file):
    """ read config file and return list of username/# of tweets tuples. """

    with open(config_file, 'rb') as configfile:
        return [row for row in reader(configfile)]

def usage():
    """ print usage. """
    print "usage:"
    print "  -c config file (csv file of twitter_username,optional_weight_not_yet_implemented)"

def main():
    logger = setup_logger("/tmp/onlyworthy.log", "onlyworthy.py")
    logger.info("Starting onlyworthy.py")

    # parse args
    try:
        opts, args = getopt(argv[1:], "c:", ["help"])
    except GetoptError, err:
        print str(err)
        usage()
        exit(2)

    for o, a in opts:
        if o == "-c":
            config_file = a
        else:
            assert False, "unhandled option"

    # init auth
    auth = tweepy.OAuthHandler(twitter_apps.CONSUMER_KEY, twitter_apps.CONSUMER_SECRET)
    auth.set_access_token(twitter_apps.ACCESS_TOKEN, twitter_apps.ACCESS_SECRET)
    twitter_api = tweepy.API(auth)

    # assemble list of tweets
    worthy_tweets = get_worthy_tweets(logger, config_file, twitter_api)

    # add tweets to index
    initVM(vmargs=['-Djava.awt.headless=true'])
    try:
        base_dir = path.dirname(path.abspath(argv[0]))
        IndexTweets(worthy_tweets, path.join(base_dir, INDEX_DIR), StandardAnalyzer(Version.LUCENE_CURRENT))
    except Exception, e:
        print "Failed: ", e
        raise e

if __name__ == "__main__":
    main()
