import sys
import re

def cleanInput(corpus):
    # Replace all none alphanumeric characters with spaces
    corpus = re.sub(r'[^a-zA-Z0-9\s]', ' ', corpus)
    corpus = re.sub('\n+', " ", corpus)
    return corpus


def getNgrams(N):
    corpus = '''
    Mary had a little lamb its fleece was white as snow;
    And everywhere that Mary went, the lamb was sure to go. 
    It followed her to school one day, which was against the rule;
    It made the children laugh and play, to see a lamb at school.
    And so the teacher turned it out, but still it lingered near,
    And waited patiently about till Mary did appear.
    "Why does the lamb love Mary so?" the eager children cry;"Why, Mary loves the lamb, you know" the teacher did reply."
    '''

    #corpus = 'ONE TWO ONE TWO THREE TWO THREE'

    corpus = cleanInput(corpus)
    tokens = [token for token in corpus.split(" ") if token != ""]
    grams = [tokens[i:i + N] for i in range(len(tokens) - N + 1)]
    return grams


def calc_probability(ngrams, wp):
    total_occurence = 0
    predicts = {}

    for gram in ngrams:
        prefix = ' '.join(gram[:-1])

        if wp == prefix:
            choice = gram[-1]
            total_occurence += 1
            predicts[choice] = predicts.get(choice, 0) + 1

    predicts = {k: v / total_occurence for k, v in predicts.items()}
    sorted_order = sorted(predicts.items(), key=lambda t: (-t[1], t[0]))
    return sorted_order


for line in sys.stdin:
    #print(line, end="")
    line = line.split(',')
    N, word = int(line[0]), line[1].rstrip().lstrip()
    ngrams = getNgrams(N)
    predictions = calc_probability(ngrams, word)

    sorted_order = calc_probability(ngrams, word)

    for key in sorted_order:
        print("{},{:.3f}".format(key[0], key[1]), end=";", flush=True)