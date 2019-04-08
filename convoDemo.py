# MUST DOWNLOAD:
# NLTK
# NLTK punkt
# NLTK wordnet
# NLTK vader_lexicon
# NLTK averaged_perceptron_tagger


import symspellpy as symspellpy
import pip

import nltk as nltk

import string
import nltk
import pickle

from nltk.tag import pos_tag
from nltk.tokenize import PunktSentenceTokenizer
from nltk.tokenize import word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from spellchecker import SpellChecker

convoFile = open("convo.dat", "r")
topic = 0  # current topic
seq = 0  # current line of topic
memory = {}  # holds user answers as dictionary (eg, {"name": "Sam"})
saveAnswer = False  # whether to expect an answer to put into 'memory'
posNext = False  # whether to expect an answer where positivity level must be determined
lastAnswer = ""  # holds last saved answer variable (eg, 'name')
lastType = ""  # holds word type of expected answer (eg, 'NNP' [proper noun])
spell = SpellChecker()  # Spellchecker


# try to get word stem
def lemma(word):
    l = nltk.WordNetLemmatizer()

    if l.lemmatize(word, pos='v') != word:
        answer = l.lemmatize(word, pos='v')
    else:
        answer = l.lemmatize(word)

    return answer


# get the relevant word from the user's answer
def findAnswer(uIn, wordType):
    with open('sent_tokenizer.pickle', 'rb') as f:
        tokenizer = pickle.load(f)

    # if only one word is found
    if len(uIn.split(' ')) == 1:
        return lemma(uIn)

    # tokenize user's sentence, breaking into words
    tokenized = tokenizer.tokenize(uIn)
    words = list()
    matches = 0
    worseType = wordType[:-1]
    worseMatches = 0

    try:
        for t in tokenized:
            words += list(nltk.pos_tag(nltk.word_tokenize(t)))

        # find matches for word type specified in convo file (eg, NNP, VB)
        numWords = len(words)
        for i in range(0, numWords):
            if words[i][0] == "like":
                pass
            elif words[i][1] == wordType:
                matches += 1
            elif worseType in words[i][1]:
                worseMatches += 1

        # finds best answer found in user's sentence; if none or can't decide, returns NaN
        answer = "NaN"
        if matches == 1:
            for i in range(0, len(words)):
                if words[i][1] == wordType:
                    answer = lemma(words[i][0])
                    if "NN" not in words[i][1]:
                        answer = answer.lower()
        elif worseMatches == 1:
            for i in range(0, len(words)):
                if words[i][0] == "like":
                    pass
                elif worseType in words[i][1]:
                    answer = lemma(words[i][0])
                    if "NN" not in words[i][1]:
                        answer = answer.lower()
        return answer
    except Exception as e:
        print(str(e))


# choose response depending on positivity of user's last answer
def posResponse(uIn):
    global posNext

    # find user response happiness score and find appropriate response
    # note: pos & neg score thresholds may require more testing
    sid = SentimentIntensityAnalyzer()
    scores = sid.polarity_scores(uIn)  # scores the users input based on positivity
    line = convoFile.readline()
    if scores['pos'] > 0.7:
        while line[:1] != '+':
            line = convoFile.readline()
    elif scores['neg'] > 0.4:
        while line[:1] != '-':
            line = convoFile.readline()
    else:
        while line[:1] != '0':
            line = convoFile.readline()
    line = line[1:]  # remove placeholder character (+, -, 0)
    posNext = False  # resets global flag

    return line


# find if any word in a string array (words) is in a string (s)
def findWord(words, s):
    for w in words:
        if (' ' + w + ' ') in (' ' + s.translate(str.maketrans('', '', string.punctuation)) + ' '):
            return True


# checks if current topic has more lines or not
def topicContinues():
    if getTopic(seq) == '\n':
        return False
    else:
        return True


# get a line by topic number (and sequence number if specified)
def getTopic(sequence=2):
    global topic
    global seq

    count = -1  # keep track of current topic in file
    convoFile.seek(0)
    while True:
        line = convoFile.readline()
        if not line: break
        if line == "\n":
            count += 1
        if count == topic:
            for i in range(0, sequence):  # get current line of topic
                line = convoFile.readline()
            return line
    return "Response not found"


# prints the found response, dealing with placeholder values
def printResponse(response):
    global saveAnswer
    global lastAnswer
    global lastType
    global seq
    global posNext

    # skips irrelevant positivity responses
    while response[:1] == '+' or response[:1] == '-' or response[:1] == '0':
        response = convoFile.readline()

    if '$' in response:  # deals with $ (variable placeholders)
        r = response.split(' ')
        for e in r:
            if '$' in e:
                r2 = e
        index = r.index(r2)
        r2 = r2.translate(str.maketrans('', '', string.punctuation))
        if r2[-1:] == '\n':
            r2 = r2[:-1]
        if r2 in memory:  # checks if requested answer is saved in memory. otherwise, displays NaN
            response = response.replace('$' + r2, memory[r2])
        else:
            response = response.replace('$' + r2, "NaN")
    if '+' in response:  # deals with + (indicating user response positivity important in next reply)
        response = response.replace('+', '')
        posNext = True
    if '^' in response:  # deals with ^ (indicating must find answer in user's next response)
        r = response.split('^')
        r2 = r[1].split('.')
        saveAnswer = True
        lastAnswer = r2[0]
        lastType = r2[1][:-1]
        output = r[0]
    else:
        output = response

    # remove newline character
    if output[-1:] == '\n':
        output = output[:-1]
    # print final output and increment seq
    print(output)
    seq += 1


# finds most appropriate topic from user input
def findTopic(uIn):
    global topic
    global saveAnswer
    global seq
    maxCorr = 0  # keyword match correlation
    topMatch = -1  # best topic match
    matches = 0  # keyword matches for current topic
    count = 0  # keep track of current topic in file
    numKeywords = 0  # holds number of keywords for each topic (used to calculate correlation)
    firstLine = True  # keep track of whether next line is the start of a new topic

    # go through convo file, finding best match topic for user's sentence
    convoFile.seek(0)
    convoFile.readline()

    while True:  # loop until end of file
        line = convoFile.readline()
        if not line: break
        if firstLine:  # on the first line of each topic, gather keywords and compare user's input
            andSplit = line[1:-1].split('&')
            numKeywords = len(andSplit)
            for a in andSplit:
                orSplit = a.split('/')
                if findWord(orSplit, uIn):  # if keyword is found in user input, increment matches counter
                    matches += 1
            firstLine = False
        elif line == "\n":  # at the end of each topic, compute keyword correlation with user's input
            if (matches / numKeywords) > maxCorr:  # if highest correlation so far, replace topMatch with current
                maxCorr = matches / numKeywords
                topMatch = count
            matches = 0
            firstLine = True
            count += 1

    # if correlation of best topic above acceptable value, use that topic
    if maxCorr >= 0.5:
        topic = topMatch
        seq = 2
        return getTopic()
    # otherwise if max correlation is poor:
    else:  # continue topic if possible. otherwise, give user a default response
        if uIn[-1:] == '?':
            if topicContinues():
                if saveAnswer == True:  # if user asked unknown question while expecting answer, repeat question
                    seq -= 1
                    return getTopic(seq)
                if posNext == True:
                    return posResponse(uIn)
                else:  # if user asked question and not expecting answer, continue topic
                    return getTopic(seq)
            else:  # if not in the middle of a topic and user asks question, give default question response
                topic = 1
                seq = 2
                return getTopic()
        else:  # if user says unknown statement, give default statement response
            topic = 0
            seq = 2
            return getTopic()


# gets next response
def getResponse(uIn=""):
    global seq

    if '?' in uIn:  # if user asked a question
        printResponse(findTopic(uIn))
    elif posNext == True:  # if user didn't ask a question, and expect a pos/neg/neutral response next
        printResponse(posResponse(uIn))
    else:
        line = convoFile.readline()
        if line != "\n":  # if current topic has more lines, continue
            printResponse(line)
        else:  # reset sequence and find new topic
            seq = 2
            printResponse(findTopic(uIn))


# Start of conversation
uIn = ""  # user input variable
print("[Say hi!]\n\n")


# spell checker method
def spellChecker(uIn):
    misspelled = spell.unknown(uIn)

    for word in misspelled:
        uIn = spell.correction(word)
        return uIn


while "bye" not in uIn and "exit" not in uIn:  # exit conversation when user input contains "bye" or "exit"
    if uIn != "":  # make sure input isn't blank
        if saveAnswer == True and '?' not in uIn:  # check if answer is expected to be saved
            tagged = findAnswer(uIn, lastType)
            memory[lastAnswer] = tagged
            saveAnswer = False
        getResponse(uIn.lower())
        print()

    uIn = input()
    print()

printResponse("See you soon! Ten afternoon!!")

exit()

# receive_thread=Thread(target=)
# receive_thread.start()

root.mainloop()
