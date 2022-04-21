from file_1 import TableCategory
import re
import json
import requests
import numpy as np


def func1(id_per_table):
    #return shape of the tables
    url2 = "http://44.193.54.227:8000/backend/download_table"
    payload2 = json.dumps({"elastic_indx": "10k","ids": id_per_table,"select_fields": ["id",
    "PDF","page","table_png","table_np"],"format": [".png",".np"]})
    headers2 = {'Content-Type': 'application/json','Authorization': 'Token 26f9b124da0da589be592f666da4f45c3981f355'}
    response2 = requests.request("POST", url2, headers=headers2, data=payload2)
    dd2 = response2.json()
    np_table = np.array(json.loads(dd2['data'][0]['table_np']))
    return np_table

class FinalClassification:

    pl_ids,cf_ids,bs_ids = TableCategory("yahoo10-K.pdf",94,100).helper_func3()

    def test_pl(test = pl_ids):
        #return id if only 1 table
        if len(test.keys()) == 1:
            return list(test.keys())[0]
        
        #if 2 captions and contains continue return both
        if len(test.keys()) == 2:
            pattern = "continue"
            for i in test.keys():
                if test[i][0].find(pattern)!=-1:
                    return list(test.keys())
        
        #if more than 2 tables
        res = []
        for i in test.keys():
            if (test[i][0].find('consolidated')!=-1):
                res.append(i)
        if len(res)==1:
                return res[0]
        for i in test.keys():
            #return other id which does not have comprehensive
            if (test[i][0].find('comprehensive')==-1):
                return i


    def test_cf(test=cf_ids):
        pattern = re.compile(r'(cash and cash equivalents at end of period)|(cash and cash equivalents, end of year)|(cash and cash equivalents at end of period)|(cash and cash equivalents, end of period)|(cash, cash equivalents and restricted cash - end of period)|(cash, cash equivalents and restricted cash at end of period)|(cash, cash equivalents and restricted cash, end of period \(b\)|(cash, cash equivalents and restricted cash, ending balances)|(cash, cash equivalents and restricted cash, including discontinued operations....)|(cash, cash equivalents and restricted funds at end of period)|(cash, cash equivalents, and restricted cash at end of period)|(cash, cash equivalents, and restricted cash at end of year)|(cash, cash equivalents, and restricted cash, end of period)|(ending balance of cash and equivalents)|(total cash, restricted cash, and equivalents))')
        
        #return id if only 1 table
        if len(test.keys()) == 1:
            return list(test.keys())[0]
        #if 2 captions and contains continue return both
        if len(test.keys()) == 2:
            pattern = "continue"
            for i in test.keys():
                if (test[i][0].lower()).find(pattern)!=-1:
                    return list(test.keys())
        
        if len(test.keys()) == 2 and (func1(list(test.keys())[0])[0].shape[0] == func1(list(test.keys())[1])[0].shape[0]):
            ans = []
            for i in test.keys():
                temp = list(test.keys())[0]
                for j in func1(i):
                    if (len(j[0][1]) < 80) and  pattern.search(j[0][1].lower()):
                        ans.append(temp)
                        ans.append(i)
            return ans
        
        ans = []
        for i in test.keys():
            if len(test[i][0])!=0:
                temp = i
                
            for j in func1(i):
                if (len(j[0][1]) < 80) and  pattern.search(j[0][1].lower()):
                    ans.append(temp)
                    ans.append(i)
                    
        #sanity check if both elements are same            
        for i in range(len(ans)):
            try:
                if ans[i] == ans[i+1]:
                    ans = ans[i]
            except:
                continue
        return ans

    def test_bs(test=bs_ids):
        #return id if only 1 table
        if len(test.keys()) == 1:
            return list(test.keys())[0]
        pattern1 = "continue"
        pattern2 = "balance sheet"
        #if 2 captions and contains continue and columns should be same return both
        if len(test.keys()) == 2 and (func1(list(test.keys())[0])[0].shape[0] == func1(list(test.keys())[1])[0].shape[0]):
            for i in test.keys():
                if test[i][0].find(pattern1)!=-1:
                    return list(test.keys())
                
        # if number of columns are not same
        elif len(test.keys()) == 2 and test[list(test.keys())[0]][0].find(pattern2) !=-1 and test[list(test.keys())[1]][0].find(pattern2) !=-1:
            for i in test.keys():
                if test[i][0].find(pattern1)!=-1:
                    return list(test.keys())
            
        #else find the one which have balance sheet term
        else:
            pattern4 = "balance sheet"
            for i in test.keys():
                if (test[i][0].find(pattern4)!=-1) :
                    return i
        
#for profit loss
obj_pl = FinalClassification.test_pl()
print("profit loss table-->",obj_pl)

#for cash flow 
obj_cf = FinalClassification.test_cf()
print("cashflow table-->",obj_cf)

#for balance sheet
obj_bs = FinalClassification.test_bs()
print("balancesheet table-->",obj_bs)





