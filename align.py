from simalign import SentenceAligner

myAligner = SentenceAligner(model="bert", token_type="bpe", matching_methods="mai")
def alignSentencePair(source_sentence:list, target_sentence:list):
	result = myAligner.get_word_aligns(source_sentence, target_sentence)
	indexList = result['itermax']
	return indexList

# An example
with open("data/PUD-Chinese.txt") as sf:
	sourceFile = sf.read()
sourceSentenceList =sourceFile.split("\n\n")
with open("data/PUD-English.txt") as tf:
	targetFile = tf.read()
sourceSentenceList =sourceFile.split("\n\n")
targetSentenceList =targetFile.split("\n\n")
print(len(sourceSentenceList))
print(len(targetSentenceList))
result = []
for i in range(1):
	sourceSentenceDP = sourceSentenceList[i].split("\n")
	targetSentenceDP = targetSentenceList[i].split("\n")
	sourceSentenceDP = [x.split("\t")[1] for x in sourceSentenceDP if not x.startswith("#")]
	targetSentenceDP = [x.split("\t")[1] for x in targetSentenceDP if not x.startswith("#")]
	print(list(enumerate(sourceSentenceDP)))
	print(list(enumerate(targetSentenceDP)))
	indexList = alignSentencePair(sourceSentenceDP, targetSentenceDP)
	print(indexList)














