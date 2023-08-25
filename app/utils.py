import re
import spacy
from spacy_streamlit import visualize_ner

nlp = spacy.load("en_core_web_md")

print("spacy version:", spacy.__version__)


key = 0

def next_key():
    global key
    key = key + 1
    return key


def visualize_entities(text):
    print("text:", text)
    doc = nlp(text)
    print("doc:", doc)
    visualize_ner(doc, labels=nlp.get_pipe("ner").labels, title=None, show_table=False, key=str(next_key()))


def strip_html(text):
    return re.sub('<[^<]+?>', '', text)


def prepare_text(text):
    text = strip_html(text)

    doc = nlp(text)

    entities = []
    for ent in doc.ents:
        print(ent.text, ent.start_char, ent.end_char, ent.label_)
        entities.append(ent)

    # Handle case where there are no NERs found

    if len(entities) == 0:
        return [text]

    prepare_data = []

    last_entity = None

    for i, entity in enumerate(entities):
        # if first token
        # get first span of text
        if i == 0:
            span_of_text = text[0: entity.start_char]
            prepare_data.append(span_of_text)
        else:
            span_of_text = text[last_entity.end_char: entity.start_char]
            prepare_data.append(span_of_text)
        print(i, entity)
        prepare_data.append((entity.text, entity.label_))
        last_entity = entity

    if last_entity and last_entity.end_char < len(text):
        span_of_text = text[last_entity.end_char: len(text)]
        prepare_data.append(span_of_text)

    return prepare_data
