from transformers import pipeline, AutoModelForTokenClassification, AutoTokenizer

sentiment_analysis = pipeline("sentiment-analysis")

# model = AutoModelForTokenClassification.from_pretrained("dbmdz/bert-large-cased-finetuned-conll03-english")
# tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")

# recognizer = pipeline("ner", model=model, tokenizer=tokenizer)
