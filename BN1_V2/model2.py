import math
import scipy.stats
import read_data
import json
import itertools
from libpgm.nodedata import NodeData
from libpgm.graphskeleton import GraphSkeleton
from libpgm.discretebayesiannetwork import DiscreteBayesianNetwork
from libpgm.pgmlearner import PGMLearner
from libpgm.tablecpdfactorization import TableCPDFactorization
from libpgm.lgbayesiannetwork import LGBayesianNetwork
from libpgm.hybayesiannetwork import HyBayesianNetwork

#unused
def approximate_pro(sample,query):
	count=0
	total=len(sample)
	for i in range(0,total):
		if cmp(query,sample[i])==0:
			count+=1

	return float(count)/total


#given values for all nodes, calculate the joint probability
def all_prob(bn,query):
    nodes=bn.V
    ret=1
    for node in nodes:
        Vdataentry = bn.Vdata[node]
        p = Vdataentry["parents"]
        if (not p):
            distribution = Vdataentry["cprob"]
        else:
            pvalues = [str(query[t]) for t in Vdataentry["parents"]]
            distribution = Vdataentry["cprob"][str(pvalues)]

        indx=Vdataentry['vals'].index(query[node])
        ret*=distribution[indx]
    return ret


#calculate the log(e)-likelihood of give date set
def likelihood(data,bn):
    l=0
    for d in data:
        l+=math.log(all_prob(bn,d))
    return l


#
def data_with_hidden(data,bn):
    new_data=[]
    for d in data:
        #print d
        d2=bn.randomsample(3,d)#toolbox
        new_data+=d2
    return new_data


#data doesn't contain hidden variables
#use ramdon sample to generate data with hidden variables
def em(data,bn,skel):
    lk_last=100
    times=0
    while 1:
        d2=data_with_hidden(data,bn)
        learner = PGMLearner()#toolbox
        bn=learner.discrete_mle_estimateparams(skel,d2)#toolbox
        lk=likelihood(d2,bn)
        print "LogLikelihood:", lk
        times +=1

        if abs((lk-lk_last)/lk_last)<0.001:
            break
        lk_last=lk
    print times
    return bn



def classify(evidence,bn):
    #q1=dict(Speed=evidence['Speed'])
    q2=dict(Volume=evidence['Volume'])
   # del evidence['Speed']
    del evidence['Volume']

    #fn = TableCPDFactorization(bn)#toolbx
    #result=fn.condprobve(q1,evidence)#t
    #mx=max(result.vals)
    #indx=result.vals.index(mx)
    #sp= bn.Vdata['Speed']['vals'][indx]

    fn = TableCPDFactorization(bn)#t
    result=fn.condprobve(q2,evidence)#t
    mx=max(result.vals)
    indx=result.vals.index(mx)
    vl=bn.Vdata['Volume']['vals'][indx]
    return [0,vl]
    #return vl

#hour, volume, volume_t+1, speed, speed_t+1, operation,laneclosed,speedlimit,length,visibility,weather
def format_data(data):
    new_data=[]
    for d in data:
        new_data.append({"Hour":d[1],"Volume":d[2],#"Speed":d[4],
                         "Operation":d[6],"LaneClosed":d[7],"SpeedLimit":d[8],
                         "Length":d[9],"Visibility":d[10],"Weather":d[11]})

    return new_data



def precision(data,bn):
    total=len(data)
    correct_s=0;correct_v=0
    for d in data:
        #tr=[d['Speed'],d['Volume']]
        tr=[1000,d['Volume']]
        c=classify(d,bn)
        if tr[0]==c[0]:
            correct_s+=1;
        if tr[1]==c[1]:
            correct_v+=1

    return [float(correct_s)/total,float(correct_v)/total]


#continuous distribution, unused
def cal_prob(testdata,bn):
    probs=[0,0]
    for d in testdata:
        s=d['S3']
        v=d['V3']
        del d['S3']
        del d['V3']
        result=bn.randomsample(1,d,"verbose")
        dst1=result[0]['S3']
        dst2=result[0]['V3']
        p1=scipy.stats.norm(dst1[1], dst1[2]).pdf(s)
        p2=scipy.stats.norm(dst2[1], dst2[2]).pdf(v)
        probs[0]+=p1
        probs[1]+=p2
        probs[0]=probs[0]/len(testdata)
        probs[1]=probs[1]/len(testdata)
    return probs


#continuous distribution, unused
def net2():
    nd = NodeData()
    skel = GraphSkeleton()
    nd.load("net.txt")  # an input file
    skel.load("net.txt")

    # topologically order graphskeleton
    skel.toporder()

    # load bayesian network
    lgbn = LGBayesianNetwork(skel, nd)

    in_data=read_data.getdata2()
    learner = PGMLearner()
    bn=learner.lg_mle_estimateparams(skel,in_data)

    p=cal_prob(in_data[300:500],bn)
    print p
    return 0



def main():

    in_data=read_data.getdata()
    f_data=format_data(in_data)
    nd = NodeData()
    nd.load("net4.txt")    # an input file
    skel = GraphSkeleton()
    skel.load("net4.txt")
    skel.toporder()
    bn=DiscreteBayesianNetwork(skel,nd)


#training dataset:70%
    bn2=em(f_data[1:6000],bn,skel)

    pr_training = precision(f_data[1:6000],bn2)

    print "Prediction accuracy for training data:" , pr_training[1]

#testing dataset:30%
    pr=precision(f_data[6700:6800],bn2)
    print "Prediction accuracy for test data:", pr[1]

    #net2()

if __name__=='__main__':
    main()
