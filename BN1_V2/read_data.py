__author__ = 'simanhuang'
import csv


def read_file(file):
    with open(file, 'r') as f:
        data = [row for row in csv.reader(f.read().splitlines())]
    return data


def getrows(row):
    volumes=row[5:12]
    speeds=row[12:19]

    data=[]

    for i in range(0,len(volumes)-2):


        speeds[i]=str(int(eval(speeds[i])/10)*10)
        volumes[i]=str(int(eval(volumes[i])/10)*10)
        temp={ "V1": eval(volumes[i]), "V2":eval(volumes[i+1]),"V3":eval(volumes[i+2])
            ,"S1": eval(speeds[i]),"S2" :eval(speeds[i+1]),"S3":eval(speeds[i+2])}

        data.append(temp)
    print data(-1)

    return data

def getdata2():
    d_5min_i270 = read_file('Short_Term_Prediction_with_5min_I270.csv')
    d_5min_i270 = d_5min_i270[2:-1]
    data=[]
    for row in d_5min_i270:
        temp=getrows(row)
        data+=temp
    return data




def getdata():
    d_weather = read_file('Weather_n_Geograph_for_I270_n_MO141_Weather.csv')
    d_weather = d_weather[1:-1]

    d_workzone = read_file('Weather_n_Geograph_for_I270_n_MO141_Workzone.csv')
    d_workzone = d_workzone[1:-1]

    d_5min_rt141 = read_file('Short_Term_Prediction_with_5min_RT141.csv')
    d_5min_rt141 = d_5min_rt141[2:-1]
    #print d_5min_rt141

    d_5min_i270 = read_file('Short_Term_Prediction_with_5min_I270.csv')
    d_5min_i270 = d_5min_i270[2:-1]
    #print d_5min_i270
    '''
    d_15min_rt141 = read_file('Short_Term_Prediction_with_15min_Rt141.csv')
    d_15min_rt141 = d_15min_rt141[2:-1]
    #print d_15min_rt141

    d_15min_i270 = read_file('Short_Term_Prediction_with_15min_I270.csv')
    d_15min_i270 = d_15min_i270[2:-1]
    #print d_15min_i270
    '''
    dctwk=dictworkzone(d_workzone)

    dcwt=dictweather(d_weather)
    data=mergdata(d_5min_i270,dctwk,dcwt)
    return data


#key=[ID,year,month,day]

def getNum(str):
    if str[0]=='0':
        return eval(str[1])
    else:
        return eval(str)


def dictweather(wtdata):
    wtdict=[]
    for row in wtdata:
        [year,month,day,visibility,weather]=row
        year=eval(year)
        month=getNum(month)
        day=getNum(day)
        visibility=eval(visibility)

        if visibility == 1 or visibility ==2:
            visibility = '1-2'

        elif visibility ==3 or visibility ==4:
            visibility = '3-4'

        elif visibility == 5 or visibility == 6:
            visibility = '5-6'

        elif visibility == 7 or visibility == 8:
            visibility = '7-8'

        elif visibility == 9 or visibility == 10:
            visibility = '9-10'


        if weather!='Clean':
            weather='NClean'

        wtdict.append([(year,month,day),[visibility,weather]])

    wtdict=dict(wtdict)
    return wtdict



def dictworkzone(wkdata):
    wkdict=[]
    for row in wkdata:
        [year,month,sdate,edate]= row[1:5]
        year=eval(year)
        sdate=eval(sdate)
        edate=eval(edate)
        month=getNum(month)

        [operation,laneclosed]=row[5:7]
        if row[9]=="NONE":
            speedlimit='null'
        else:
            speedlimit=eval(row[9])
            if speedlimit >= 40 and speedlimit <= 45:
                speedlimit = '40-45'
            if speedlimit >= 46 and speedlimit <=50:
                speedlimit = '46-50'
            if speedlimit >= 51 and speedlimit <= 55:
                speedlimit = '51-55'
            if speedlimit >= 56 and speedlimit <= 60:
                speedlimit = '56-60'
            if speedlimit >= 61 and speedlimit <= 65:
                speedlimit = '61-65'

        length=eval(row[16])
        if length >= 0.006 and length < 3.961:
            length = 'S'
        if length >= 3.961 and length < 7.916:
            length = 'M'
        if length >= 7.916 and length <=11.87:
            length = 'L'
        ID = eval (row[17])
        for date in range(sdate,edate+1):
            wkdict.append([(ID,year,month,date),[operation,laneclosed,speedlimit,length]])

    wkdict=dict(wkdict)
    return wkdict


def getworkzone(key,wkdict):
    try:
        wkrecord=wkdict[key]
    except KeyError:
        wkrecord=['NONE',0,'None','S']
    return wkrecord


def getWeather(key,wtdict):
    key=(key[1],key[2],key[3])
    try:
        wtrecord=wtdict[key]
    except KeyError:
        wtrecord=None
    return wtrecord



#"Speed":["0","10","20","30","40","50","60","70"]
#"Volumes":["100","200","300","400","500"
def getspdvlm(row):
    [date,stime,etime,ID]=row[1:5]
    time_intv=5
    stime=eval(stime)
    etime=eval(etime)
    ID=eval(ID)
    volumes=row[5:12]
    speeds=row[12:19]
    year=eval(date[0:4])
    month=getNum(date[4:6])
    day=getNum(date[6:8])

    data=[]

    for i in range(0,len(volumes)-1):
        time=int((stime+i*time_intv)/100)
        if time>21:
            time=21
        temp=[]

        temp.append([ID,year,month,day])

        speeds[i]=str(int(eval(speeds[i])/10)*10)
        volumes[i]=str(int(eval(volumes[i])/200)*200+200)
        '''
        if speeds[i] >= 0 and speeds[i] <10:
            speeds[i] = '0'
        if speeds[i] >=10 and speeds[i] < 20:
            speeds[i] = '10'
        if speeds[i] >=20 and speeds[i] < 30:
            speeds[i] = '20'
        if speeds[i] >= 20 and speeds[i] <40:
            speeds[i] = '30'
        if speeds[i] >= 40 and speeds[i] <50:
            speeds[i] ='40'
        if speeds[i] >= 50 and speeds[i] <60:
            speeds[i] = '50'
        if speeds[i] >= 60 and speeds [i] <70:
            speeds[i] ='60'
        if speeds[i] >= 70:
            speeds[i] = '70'

        if volumes[i] >= 0 and volumes[i] < 200:
            volumes[i] = '200'
        if volumes[i] >= 200 and volumes[i] < 400:
            volumes[i] = '400'
        if volumes[i] >= 400 and volumes[i] < 600:
            volumes[i] = '600'
        if volumes[i] >= 600 and volumes[i] < 800:
            volumes[i] = '800'
        if volumes[i] >= 800 and volumes[i] < 1000:
            volumes[i] = '1000'
        if volumes[i] >= 1000 and volumes[i] < 1200:
            volumes[i] = '1200'
        if volumes[i] >= 1200 and volumes[i] < 1400:
            volumes[i] = '1400'
        if volumes[i] >= 1400 and volumes[i] < 1600:
            volumes[i] = '1600'
        if volumes[i] >= 1600 and volumes[i] < 1800:
            volumes[i] = '1800'
        if volumes[i] >= 1800 and volumes[i] < 2000:
            volumes[i] = '2000'
        '''
        temp=temp+[str(time), volumes[i], volumes[i+1], speeds[i], speeds[i+1]]

        data.append(temp)

    return data


#data[0]:key=[ID year month day]
#data[1:-1]: hour, volume, volume_t+1, speed, speed_t+1, operation,laneclosed,speedlimit,length,visibility,weather
def mergdata(traffic,workdict,weatherdict):
    data=[]
    count=0
    for row in traffic:
        #print count,row
        d1=getspdvlm(row)

        #ID year month day
        key=tuple(d1[0][0])

        #select certern data
        if key[2]!=7:
            continue
        wk=getworkzone(key, workdict)
        wt=getWeather(key, weatherdict)
        #if weather condition not exsist skip

        if wt==None:
            continue

        for i in range(0, len(d1)):
            data.append(d1[i]+wk+wt)
        count = count + 1
    return data

'''
dctwk=dictworkzone(d_workzone)

dcwt=dictweather(d_weather)


data=mergdata(d_5min_i270,dctwk,dcwt)
# print data


b=[[(1,2,3),2]]
b=dict(b)
print b[(1,2,3)]
'''