import nltk
import contractions
from nltk.corpus import stopwords
from nltk.stem import LancasterStemmer, WordNetLemmatizer
import re, string
from textblob import TextBlob

class textProcessing:

    #this method removes all the noises from the news articles
    def removeNoise(self, text):
        #removing all urls
        textNoUrl = re.sub(r'https\S','',text)
        #removing all paranthesis
        textNoParentheses = re.sub('\(.*?\)','',textNoUrl)
        #removing all brackets
        textNoBrackets = re.sub('[.*?]', '', textNoParentheses)
        #removing all percent signs
        textNoPercent = textNoBrackets.replace("%", "")
        #removing all digits
        textNoDigit = re.sub(r'\d+','',textNoPercent)
        textNoDash = textNoDigit.replace("—", "")
        #removing all dollar signs
        textNoDollarSign = textNoDash.replace("$", "")
        #removing all punctuation marks
        trans = str.maketrans('', '', string.punctuation)
        textNoPunc = textNoDollarSign.translate(trans)
        #removing all white spaces
        textNoWhiteSpace = ' '.join(textNoPunc.split())
        #removing all simicolons
        textNoSimicolon = re.sub('“|”', '', textNoWhiteSpace)
        textNoNoise = textNoSimicolon
        return textNoNoise

    #this function corrects the spelling mistakes of news articles
    def spellChecker(self, text):
        textBlb = TextBlob(text)
        textCorrected = textBlb.correct()
        return str(textCorrected)
    #this function convert all the words to the lower case, contracts the text and tokenized the news article
    def normalizing(self, text):
        lowerText = text.lower()
        contractionsText = contractions.fix(lowerText)
        #nltk.download('punkt')
        tokens = nltk.word_tokenize(contractionsText)
        return tokens
    #this nethod removes the stop words
    def removeStopWords(self, tokenizedText):
        #nltk.download('stopwords')
        textNoStopWord = []
        for i in tokenizedText:
            if i not in stopwords.words('english'):
                textNoStopWord.append(i)
        return textNoStopWord
    #this methos apply stemming to the news article
    def stemming(self, tokenizedText):
        stemmer = LancasterStemmer()
        stemmed = []
        for i in tokenizedText:
            stem = stemmer.stem(i)
            stemmed.append(stem)
        return stemmed
    #this method apply lemmatizationj to the news article
    def lemmatization(self, tokenizedText):
        # nltk.download('wordnet')
        # nltk.download('omw-1.4')
        lemma = WordNetLemmatizer()
        lemmas = []
        for i in tokenizedText:
            lem = lemma.lemmatize(i, pos='v')
            lemmas.append(lem)
        return lemmas
    #this method removes non-english words from the news article
    def removeNonEnglish(self, tokenizedText):
        #nltk.download('words')
        words = set(nltk.corpus.words.words())
        textEnglish = []
        for i in tokenizedText:
            if i in words:
                textEnglish.append(i)
        return textEnglish

    def removeEnglish(self, tokenizedText):
        nltk.download('words')
        words = set(nltk.corpus.words.words())
        textNonEnglish = []
        for i in tokenizedText:
            if i not in words:
                textNonEnglish.append(i)
        return textNonEnglish