from simalign import SentenceAligner
import math
myAligner = SentenceAligner()
def alignSentencePair(source_sentence:list, target_sentence:list):
	result = myAligner.get_word_aligns(source_sentence, target_sentence)
	alignList = result['itermax']
	return alignList

# transform the original dependency to a format like [(head, label, tail)...]
def newDP(originalDp):
	result = []
	for dp in originalDp:
		item = dp.split("\t")
		wordID = item[0]
		wordToken = item[1]
		headID = item[6]
		label = item[7]
		if headID != "0":
			headToken = originalDp[int(headID)-1].split("\t")[1]
		else:
			headToken = "ROOT"	
		result.append((headToken+"~"+headID, label, wordToken+"~"+wordID))
	return result

# source_sentence = "“ 雖然 美國 的 許多 數字化 轉型 都是 史無前例 的 ，但 權力 的 和平 轉移 卻 存在 先例 ， ” 奧巴馬 的 特別 助理 科瑞 · 舒爾曼 在 周 一 發布 的 博客 中 寫道 。"
# target_sentence = "“ While much of the digital transition is unprecedented in the United States , the peaceful transition of power is not , ” Obama special assistant Kori Schulman wrote in a blog post Monday ."

# model = simalign.SentenceAligner()
# Build Hypergraph from dependencies
def findLeaves(dp):
	dpTail = list(set([dp[i][2] for i in range(len(dp))]))
	dpHead = list(set([dp[i][0] for i in range(len(dp))]))
	dpLeaves = [tail for tail in dpTail if tail not in dpHead]
	return dpLeaves

def buildHyperGraph(dp):
	dictHG = {}
	for item in dp:
		# print(item)
		label = item[0]+"~"+[x[1] for x in dp if x[2] == item[0]][0] if item[0] != "ROOT~0" else item[0]
		# print(label)
		# print("##########")
		if label not in dictHG:
			dictHG[label] = []		
		dictHG[label].append(item[2]+"~"+item[1])
	dpLeaves = findLeaves(dp)
	for leaf in dpLeaves:
		leafLabel = leaf + "~" + [dp[j][1] for j in range(len(dp)) if dp[j][2] == leaf][0]
		if leafLabel not in dictHG:
			dictHG[leafLabel] = []
	return dictHG
# Compare two hypergraphs according to the alignment and obtain their similarity matrix
def s(a:str,b:str,alignList:list):
	return 1 if (int(a)-1, int(b)-1) in alignList else 0
def r(a:str,b:str):
	return 1.1 if a.lower() == b.lower() else 1 # 1.1 is an initialization of a multiplier if labels of two headNodes are the same
def t(a:str,b:str):
	return 1.5 if a.lower() == b.lower() else 1 # 1.5 is an initialization of a multiplier if labels of two tailNodes are the same
def nodeCompare(hyperGraph1, hyperGraph2, dependencySimMatirx, alignList):
	for head1 in hyperGraph1:
		for head2 in hyperGraph2:
			if head1 == "ROOT~0" or head2  == "ROOT~0":
				continue
			else:
				headTokenScore = s(head1.split("~")[1], head2.split("~")[1], alignList)
				if headTokenScore == 0:
					continue
				else:
					headLabelScore = r(head1.split("~")[2], head2.split("~")[2])
					tailScore = 1
					for tail1 in hyperGraph1[head1]:
						for tail2 in hyperGraph2[head2]:
							tailTokenScore = s(tail1.split("~")[1], tail2.split("~")[1], alignList)
							if tailTokenScore == 0:
								continue
							else:
								tailLabelScore = t(head1.split("~")[2], head2.split("~")[2])
								tailScore += tailTokenScore + tailLabelScore
					
					dependencySimMatirx[int(head1.split("~")[1])-1][int(head2.split("~")[1])-1] = headTokenScore * headLabelScore * tailScore

	return dependencySimMatirx

# Update similarity matrix using level weights of each hyperedges
def findLeavesEdge(dp):
	dpHead = list(set([dp[i][0] for i in range(len(dp))]))
	dpLeavesEdge = [item for item in dp if item[2] not in dpHead]
	return dpLeavesEdge

def levelWeight(dp,level,addValue,levelDict):
	currentLevel = findLeavesEdge(dp)
	while currentLevel:
		tmp = []
		for current in currentLevel:
			levelDict[current[2].split("~")[1]] = level
			tmp.extend([dp[i] for i in range(len(dp)) if dp[i][2] == current[0]])
		level += addValue # Both initial level value and addValue are parameters
		dp = [item for item in dp if item not in currentLevel]
		currentLevel = tmp
	return levelDict

def levelWeightForNorm(dp,level,addValue,levelDict):
	currentLevel = findLeavesEdge(dp)
	while currentLevel:
		tmp = []
		for current in currentLevel:
			levelDict[current[2].split("~")[0]+"~"+current[2].split("~")[1]] = level
			tmp.extend([dp[i] for i in range(len(dp)) if dp[i][2] == current[0]])
		level += addValue # Both initial level value and addValue are parameters
		dp = [item for item in dp if item not in currentLevel]
		currentLevel = tmp
	return levelDict

with open("data/PUD-German.txt") as sf:
	sourceFile = sf.read()
sourceSentenceList =sourceFile.split("\n\n")
with open("data/PUD-English.txt") as tf:
	targetFile = tf.read()
sourceSentenceList =sourceFile.split("\n\n")
targetSentenceList =targetFile.split("\n\n")
print(len(sourceSentenceList))
print(len(targetSentenceList))
result = []
for i in range(1000):
	print(i)
	score = 0
	sourceSentenceDP = sourceSentenceList[i].split("\n")
	targetSentenceDP = targetSentenceList[i].split("\n")
	sourceSentenceDP = [x for x in sourceSentenceDP if not x.startswith("#")]
	targetSentenceDP = [x for x in targetSentenceDP if not x.startswith("#")]
	newDP1 = newDP(sourceSentenceDP)
	newDP2 = newDP(targetSentenceDP)
	print(newDP1)
	print(newDP2)
	norm1 = 0
	norm2 = 0
	normDict1 = levelWeightForNorm(newDP1,1,0.2,{})
	normDict2 = levelWeightForNorm(newDP2,1,0.2,{})
	for (head1,label1,tail1) in newDP1:
		if head1 != "ROOT~0":
			norm1 += normDict1[head1]**2
			norm1 += normDict1[tail1]**2
	for (head2,label2,tail2) in newDP2:
		if head2 != "ROOT~0":
			norm2 += normDict2[head2]**2
			norm2 += normDict2[tail2]**2
	norm1 = math.sqrt(norm1)
	norm2 = math.sqrt(norm2)
	
	hyperGraph1 = buildHyperGraph(newDP1)
	hyperGraph2 = buildHyperGraph(newDP2)
	# print(hyperGraph1)
	# print(hyperGraph2)
	sourceSentence = [x.split("\t")[1] for x in sourceSentenceDP if not x.startswith("#")]
	targetSentence = [x.split("\t")[1] for x in targetSentenceDP if not x.startswith("#")]
	alignList = alignSentencePair(sourceSentence, targetSentenceDP)	
	dpSim = [[0] * len(newDP2) for _ in range(len(newDP1))]
	dpSim = nodeCompare(hyperGraph1, hyperGraph2, dpSim, alignList)
	levelDict1 = levelWeight(newDP1,1,0.2,{})
	levelDict2 = levelWeight(newDP2,1,0.2,{})
	
	for i in range(len(dpSim)):
		for j in range(len(dpSim[0])):
			dpSim[i][j] *= levelDict1[str(i+1)] * levelDict2[str(j+1)]
			score += dpSim[i][j]
	score = score / (norm1 * norm2)
	result.append(score)
	# print(score)
	# print("##################")

print(result)















