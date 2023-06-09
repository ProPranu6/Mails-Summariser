#!/usr/bin/env python
# coding: utf-8

# In[1]:



""" In this we compare a few Python libaries for Extractive 
text summarization. In Extractive text summarization, the 
algorithm selects the most representative sentences from the 
paragraph that can effectively summarize it. Unlike Abstractive 
summarization, it does not paraphrase the text.
We compare the following Python packages:
    Sumy (with the following algorithms)
        Luhn's algorithm
        LSA (Latent Semantic Analysis)
        TextRank
        LexRank
        SumBasic
        KL Distance
    Gensim's TextRank algorithm
    PyTeaser/TextTeaser
    PyTextRank
"""


def sumySummarize(filename, language="english", num_sents=1):
    
    """
    Luhn's algorithm is the most basic:
    1. Ignore Stopwords
    2. Determine Top Words: The most often occuring words in the document are counted up.
    3. Select Top Words: A small number of the top words are selected to be used for scoring.
    4. Select Top Sentences: Sentences are scored according to how many of the top words they 
    contain. The top N sentences are selected for the summary.
    
    SumBasic uses a simple concept:
    1. get word prob. p(wi) = ni/N (ni = no. of times word w exists, N is total no. of words)
    2. get sentence score sj = sum_{wi in sj} p(wi)/|wi| (|wi| = no. of times wi comes in sj)
    3. choose sj with highest score
    4. update pnew(wi) = pold(wi)^2 for words in the chosen sentence (we want probability to include the same words to go down)
    5. repeat until you reach desired no. of sentences
    
    KL algorithm solves arg min_{S} KL(PD || PS) s.t. len(S) <= # sentences, where 
    	KL = Kullback-Lieber divergence = sum_{w} PD(w)log(PD(w)/PS(w))
    	PD = unigram word distribution of the entire document
    	PS = unigram word distribution of the summary (optimization variable)
    
    LexRank and TextRank use a PageRank kind of algorithm
    1. Treat each sentence as the node in the graph
    2. Connect all sentences to get a complete graph (a clique basically)
    3. Find similarity between si and sj to get weight Mij of the edge conecting i and j
    4. Solve the eigen value problem Mp = p for similarity matrix M.
    5. L = 0.15 + 0.85*Mp.  L gives the final score for each sentence.  Pick the top sentences
    LexRank uses a tf-idf modified cosine similarity for M.  TextRank uses some other similarity metric
    
    LSA uses a SVD based approach
    1. Get the term-sentence matrix A (rows is terms, columns is sentences).  Normalize with term-frequency (tf) only
    2. Do SVD; A = USV' (A=m x n, U=m x n, S=n x n, V=n x n)
    SVD derives the latent semantic structure of sentences.  The k dimensional sub-space get the key k topics
    of the entire text structure.  It's a mapping from n-dimensions to k
    If a word combination pattern is salient and recurring in document, this
    pattern will be captured and represented by one of the singular vectors. The magnitude of the
    corresponding singular value indicates the importance degree of this pattern within the
    document. Any sentences containing this word combination pattern will be projected along
    this singular vector, and the sentence that best represents this pattern will have the largest
    index value with this vector. As each particular word combination pattern describes a certain
    topic/concept in the document, the facts described above naturally lead to the hypothesis that
    each singular vector represents a salient topic/concept of the document, and the magnitude of
    its corresponding singular value represents the degree of importance of the salient
    topic/concept.
    Based on this, summarization can be based on matrix V.  V describes an importance degree 
    of each topic in each sentence. It means that the k’th sentence we choose has the largest 
    index value in k’th right singular vector in matrix V.  An extension of this is using 
    SV' as the score for each sentence
    """
    from sumy.parsers.plaintext import PlaintextParser
    from sumy.nlp.tokenizers import Tokenizer
    from sumy.nlp.stemmers import Stemmer
    from sumy.utils import get_stop_words
    from sumy.summarizers.luhn import LuhnSummarizer
    from sumy.summarizers.lsa import LsaSummarizer
    from sumy.summarizers.text_rank import TextRankSummarizer
    from sumy.summarizers.lex_rank import LexRankSummarizer
    from sumy.summarizers.sum_basic import SumBasicSummarizer
    from sumy.summarizers.kl import KLSummarizer
    
    parser = PlaintextParser.from_file(filename, Tokenizer(language))
    
    def getSummary(sumyAlgorithm):
        sumyAlgorithm.stop_words = get_stop_words(language)
        summary = sumyAlgorithm(parser.document, num_sents)
        sents = [str(sentence) for sentence in summary]
        return sents
    
    stemmer = Stemmer(language)
    
    summaries = {}
    summaries['Luhn'] = getSummary(LuhnSummarizer(stemmer))
    summaries['LSA'] = getSummary(LsaSummarizer(stemmer))
    summaries['TextRank'] = getSummary(TextRankSummarizer(stemmer))
    summaries['LexRank'] = getSummary(LexRankSummarizer(stemmer))
    summaries['SumBasic'] = getSummary(SumBasicSummarizer(stemmer))
    summaries['KL'] = getSummary(KLSummarizer(stemmer))
    
    
    return summaries


def gensimSummarize(filename, coverage_fraction=0.2):
    
    """
    Gensim uses its own TextRank algorithm.  The algorithm is same as the 
    LexRank algorithm described above.  Only difference - instead of cosine similarity
    it uses a more sophisticated BM-25 similarity metric 
    """
    from gensim.summarization.summarizer import summarize
    
    fh = open(filename,"r")
    text = fh.read()
    fh.close()
    
    summary = summarize(text, coverage_fraction)
    
    
    return summary


def pyteasSummarize(filename, title, num_sents=1):
    
    """
    TextTeaser/PyTeaser uses basic summarization features and build from it. Those features are:
    1. Title feature is used to score the sentence with the regards to the title. It is calculated 
    as the count of words which are common to title of the document and sentence.
    2. Sentence length is scored depends on how many words are in the sentence. TextTeaser defined 
    a constant “ideal” (with value 20), which represents the ideal length of the summary, in terms 
    of number of words. Sentence length is calculated as a normalized distance from this value.
    3. Sentence position is where the sentence is located. I learned that introduction and conclusion 
    will have higher score for this feature.
    4. Keyword frequency is just the frequency of the words used in the whole text in the bag-of-words 
    model (after removing stop words).
    """
    
    from pyteaser import Summarize
    
    fh = open(filename,"r")
    text = fh.read()
    fh.close()
    
    summary = Summarize(title, text)
    sents = " ".join([str(sentence) for sentence in summary[:num_sents]])
    
    
    return sents


def createJSON(filename):
    
    import re
    import json
    
    fh = open(filename,"r")
    text = fh.read()
    fh.close()
    
    # Remove quotes
    text = re.sub("\"",'', text)
    
    d = {}
    d['id'] = 707
    d['text'] = text
    
    jsonFile = filename.split(".")[0] + ".json"
    fh = open(jsonFile,'w')
    fh.write(json.dumps(d))
    fh.close()
    
    return jsonFile


def pytrankSummarize(filename):
    
    """
    This is another TextRank algorithm. It works in four stages, each feeding its output to the next
    1. Part-of-Speech Tagging and lemmatization are performed for every sentence in the document.
    2. Key phrases are extracted along with their counts, and are normalized.
    3. Calculates a score for each sentence by approximating jaccard distance between the sentence and key phrases.
    4. Summarizes the document based on most significant sentences and key phrases.
    """
    
    import pytextrank
    
    jsonText = createJSON(filename)
    
    path_stage0 = jsonText
    path_stage1 = "o1.json"
    
    with open(path_stage1, 'w') as f:
        for graf in pytextrank.parse_doc(pytextrank.json_iter(path_stage0)):
            f.write("%s\n" % pytextrank.pretty_print(graf._asdict()))
    
    path_stage2 = "o2.json"
    
    graph, ranks = pytextrank.text_rank(path_stage1)
    
    with open(path_stage2, 'w') as f:
        for rl in pytextrank.normalize_key_phrases(path_stage1, ranks):
            f.write("%s\n" % pytextrank.pretty_print(rl._asdict()))
    		
    path_stage3 = "o3.json"
    
    kernel = pytextrank.rank_kernel(path_stage2)
    
    with open(path_stage3, 'w') as f:
        for s in pytextrank.top_sentences(kernel, path_stage1):
            f.write(pytextrank.pretty_print(s._asdict()))
            f.write("\n")
    		
    phrases = ", ".join(set([p for p in pytextrank.limit_keyphrases(path_stage2, phrase_limit=12)]))
    sent_iter = sorted(pytextrank.limit_sentences(path_stage3, word_limit=50), key=lambda x: x[1])
    s = []
    
    for sent_text, idx in sent_iter:
        s.append(pytextrank.make_sentence(sent_text))
    
    graf_text = " ".join(s)
    
    return graf_text
    

def getAlgorithmChoice():
    
    print(" ")
    print("Algorithm/library choices for summarization ... ")
    print("1. Sumy (all algorithms)")
    print("2. Gensim")
    print("3. PyTeaser")
    print("4. PyTextRank")
    print(" ")
    ch = int(input("Enter your choice: "))
    return ch
    

if __name__ == "__main__":
    
    TEXT_FILE = "sample_text.txt"
    LANGUAGE = "english"
    SENTENCE_COUNT = 2
    
    choice = getAlgorithmChoice()
    
    if choice == 1:
        sumySummarize(TEXT_FILE, LANGUAGE, SENTENCE_COUNT)
    elif choice == 2:
        gensimSummarize(TEXT_FILE, 0.2)
    elif choice == 3:
        pyteasSummarize(TEXT_FILE, "Topic Modelling", SENTENCE_COUNT)
    elif choice == 4:
        pytrankSummarize(TEXT_FILE)
    else:
        print("Wrong choice")
     


# In[ ]:




