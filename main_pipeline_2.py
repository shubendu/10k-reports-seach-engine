from file_1 import TableCategory



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
        
        



