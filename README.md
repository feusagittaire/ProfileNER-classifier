# NLP Classification Python Package For Profile Category and NER

## Functionality of the Package

Performs Classification using Regex for social media user's profile categorization and NER tasks
1. If profile:
    * Categories: Politician, Information Vehicule, Health Professional, Science, Education Professional, Artist, Organization and Journalist;
2. NER: 
    * Vaccines, Products, Drugs, Diseases, Symptoms, Science, Part of the body; returns a dataframe that has information of the entity id, name and it's occurence frequency on the input text.


## The package takes the following parameters as input:

1. Profile: 
    * Text containing informations about the user's biography or channel description in the context of communication reaseach porpuses
2. NER: 
    * Text

## Usage

```
pip install ProfileNER-classifier

```


### Example

```
from nlpclassifier_profilener import NLPClassifier

#Instatiate the classifier

#If profile classification is the task of choice
nlpc = NLPClassifier('profile')

#Preprocess the text. Its's important to lowercase and remove accents
yt['channelDesc'] = yt['channelDesc'].apply(lambda x: pipeline.preprocess(x, lower = True)).apply(lambda x: pipeline.strip_accents(x))

#Classify channelCategory
yt['channelCategory'] = yt['channelDesc'].apply(lambda x: tpc.classifier(str(x)))

#See the distribution of profile categories if Profile task
yt['channelCategory'].value_counts()


#If NER classification, there's two options
#The first is to get the entities name as you would get with Spacy, for example. For this purpose, use the classifier function with 'ner' use.
nlpc = NLPClassifier('ner')
yt['ner'] = yt['videoTranscription'].apply(lambda x: nlpc.classifier(str(x))) #already preprocessed

#The second is to get the entities occurence frequency in the text. For this purpose, use the ner_classifier function with 'ner' use. Remember that it returns the input dataframe updated with the ner entities as new columns and their frequency as their rows.
nlpc = NLPClassifier('ner')
yt = yt['videoTranscription'].apply(lambda x: nlpc.ner_classifier(str(x))) #already preprocessed
```

### Note
The package is still a work is in progress.
In case of error, feel free to contact me.