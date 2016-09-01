# -*- coding:utf-8 -*-
from numpy import *

def sim(l1,l2):
	return corrcoef(array(l1),array(l2),rowvar=0)[0][1]

def standardrizedScore(scoreList):
	a=average(scoreList)
	maxS=max(scoreList)
	minS=min(scoreList)
	standardScore=[]
	for score in scoreList:
		if maxS-minS==0:
			standardScore.append(0)
		else:
			standardScore.append((score-a)/(maxS-minS))
	return standardScore

# print standardScore(7.0,[4.8,5.5,6.6,7.7,7.5])



def getWeight(i,n,d):
	i=n-double(i)
	n=double(n)
	dp=math.atan(-d/10)/8+3.15/3
	w=2*i/(n*(n-1))
	cw=(dp/10+w)/2
	return cw

def sim_pearson(prefs,p1,p2):
    #得到双方曾评价过的物品列表
    si = {}
    for item in prefs[p1]:
        if item in prefs[p2]:
            si[item] = 1
    #得到列表元素个数
    n = len(si)

    #如果两者没有共同之处，则返回1
    if not n:
        return  1

    #对所有偏好求和
    sum1 = sum([prefs[p1][it] for it in si])
    sum2 = sum([prefs[p2][it] for it in si])

    #求平方和
    sum1Sq = sum([pow(prefs[p1][it],2) for it in si])
    sum2Sq = sum([pow(prefs[p2][it],2) for it in si])

    #求乘积之和
    pSum = sum([prefs[p1][it] * prefs[p2][it] for it in si])

    #计算皮尔逊评价值
    num = pSum -(sum1 * sum2 / 2)
    den = sqrt((sum1Sq - pow(sum1,2) / n) * (sum2Sq - pow((sum2,2) / 2)))
    if not den:
        return 0
    r = num/den
    return r

