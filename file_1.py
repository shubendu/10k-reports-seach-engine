import re
import requests
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
model = SentenceTransformer('bert-base-nli-mean-tokens')


class TableCategory:
    
    bs = ['balance sheet as on' ,
    'balance sheets',
    'condensed consolidated balance sheets',
    'condensed consolidated statements of financial position',
    'consolidated and company balance sheets',
    'consolidated balance sheet',
    'consolidated balance sheets',
    'consolidated balance sheets unaudited',
    'consolidated condensed balance sheets',
    'consolidated statement of financial position',
    'consolidated statements of financial condition',
    'consolidated statements of financial position unaudited',
    'group statement of financial position',
    'statement of financial position',
    'statement of financial position as at',
    'unaudited condensed consolidated balance sheets',
    'equity',
    'liabilities', 
    'assets',
    'balance',
    'balance sheet']
    cf = ['condensed consolidated statements of cash flows',
    'condensed consolidated statements of cash flows unaudited',
    'consolidated cash flow statement',
    'consolidated condensed statements of cash flows',
    'consolidated statement of cash flows',
    'consolidated statements of cash flows',
    'consolidated statements of cash flows unaudited',
    'consolidated statements of cash flows unaudited',
    'group statement of cash flows',
    'statement of cash flow',
    'statement of cash flows for the year ended' ,
    'statement of cash flows for the year ended',
    'statement of consolidated cash flows',
    'unaudited condensed consolidated statements of cash flows']

    pl = ['condensed consolidated statements of operations',
    'consolidated income statement',
    'consolidated income statements',
    'consolidated profit and loss account',
    'consolidated statement of comprehensive income',
    'consolidated statement of profit and loss',
    'consolidated statements of income',
    'consolidated statements of operations',
    'group statement of comprehensive income',
    'statement of comprehensive income',
    'statement of financial activities for the year ended',
    'statemnent of profit and loss for the year ended',
    'unaudited condensed consolidated statements of loss',
    'operations',
    'operation',
    'statements of operations']
    
    url = "http://44.193.54.227:8000/backend/get_object_around_object"
    headers = {'Content-Type': 'application/json','Authorization': 'Token 26f9b124da0da589be592f666da4f45c3981f355'} 
    
    def __init__(self,company, page1, page2):
        self.company = company
        self.page1 = page1
        self.page2 = page2
    
    def page_range(self):
        return (list(range(self.page1,self.page2+1)))
    
    def func1(self,id_per_table):
        url2 = "http://44.193.54.227:8000/backend/download_table"
        payload2 = json.dumps({"elastic_indx": "10k","ids": id_per_table,"select_fields": ["id",
        "PDF","page","table_png","table_np"],"format": [".png",".np"]})
        headers2 = {'Content-Type': 'application/json','Authorization': 'Token 26f9b124da0da589be592f666da4f45c3981f355'}
        response2 = requests.request("POST", url2, headers=headers2, data=payload2)
        dd2 = response2.json()
        np_table = np.array(json.loads(dd2['data'][0]['table_np']))
        return np_table[0]
    
    def table_ids(self):
        payload = json.dumps({"elastic_indx": "10k","select_fields": ["id","PDF","page","type"],"type_around": ["text"],
                "position": ["top"],"max_distance": 200,"max_num_objects": 5,"type": [
                "table"],"PDF": self.company ,"page": self.page_range()})
        response = requests.request("POST", self.url, headers=self.headers, data=payload)
        pages = response.json()
        pattern = re.compile(r'((sheets?\b)|(balance\b)|(condensed flows\b)|(consolidated flows\b)|(statements\b)|(financial\b)|(position\b)|(unaudited\b)|(equity\b)|(liabilities\b)|(assets\b)|(cash\b)|(flows\b)|(operations\b)|(income\b)|(profit\b)|(loss\b)|(comprehensive\b)|(activities\b)|(statement\b))')
        result = {}
        shape = []
        for i in range(len(pages['data'])):
            #this if else will fix tables without captions
            if pages['data'][i]['objects_around']['top']:
                shape.append(self.func1(pages['data'][i]['id']).shape[0])
                res_content = []
                for j in range(0,len(pages['data'][i]['objects_around']['top'])):
                    if pattern.search(pages['data'][i]['objects_around']['top'][j]['text'].lower()):
                        res_content.append(pages['data'][i]['objects_around']['top'][j]['text'].lower())
                result[pages['data'][i]['id']] = res_content
            elif (pages['data'][i-1]['objects_around']['top']) and self.func1(pages['data'][i]['id']).shape[0] == self.func1(pages['data'][i-1]['id']).shape[0]:
                shape.append(self.func1(pages['data'][i]['id']).shape[0])
                res_content = []
                for j in range(0,len(pages['data'][i]['objects_around']['top'])):
                    if pattern.search(pages['data'][i]['objects_around']['top'][j]['text'].lower()):
                        res_content.append(pages['data'][i]['objects_around']['top'][j]['text'].lower())
                result[pages['data'][i]['id']] = res_content
        for i in result.keys():
            temp = result[i]
            temp = " ".join(temp)
            result[i] = temp
        return result
    
    def cosine_sim(self,query):
        #returns table label per id
        res = {}
        #bs
        final1 =[]
        final1= self.bs+query
        sentence_embeddings = model.encode(final1)
        bs_res = np.sort(cosine_similarity([sentence_embeddings[sentence_embeddings.shape[0]-1]],\
                sentence_embeddings)[0])[-2]
        res['bs'] = bs_res

        #cf
        final2 =[]
        final2= self.cf+query
        sentence_embeddings = model.encode(final2)
        cf_res = np.sort(cosine_similarity([sentence_embeddings[sentence_embeddings.shape[0]-1]],\
                sentence_embeddings)[0])[-2]
        res['cf'] = cf_res

        #pl
        final3 =[]
        final3 = self.pl+query
        sentence_embeddings = model.encode(final3)
        pl_res = np.sort(cosine_similarity([sentence_embeddings[sentence_embeddings.shape[0]-1]],\
                sentence_embeddings)[0])[-2]
        res['pl'] = pl_res

        return res
    
    def helper_func1(self):
        all_ids = self.table_ids()
        final_ans = {}
        for i in all_ids.keys():
            ans_temp = self.cosine_sim([all_ids[i]])
            Keymax = max(zip(ans_temp.values(), ans_temp.keys()))[1]
            final_ans[i] = [all_ids[i],Keymax]

        #changing label from previous id if content is empty
        for i in final_ans.keys():
            if len(final_ans[i][0])!=0:
                temp = final_ans[i][1]
            if len(final_ans[i][0])==0:
                final_ans[i][1] = temp
                final_ans[i][0] = 'EMPTY CAPTION CONTINUED'

        #deleting ids when empty
        for key in final_ans.copy():
            if len(final_ans[key][0])== 0:
                    del final_ans[key]
        return final_ans
    def helper_func2(self):
        final_ans = self.helper_func1()
        for i in final_ans.copy():
            pattern1 = re.compile(('stockhold|sharehold|partner'))
            pattern2 = re.compile('continue')
            #skip it if contains word continue
            if re.search(pattern1,final_ans[i][0]) and re.search(pattern2,final_ans[i][0]):
                continue
            elif re.search(pattern1,final_ans[i][0]):
                del final_ans[i]
        return final_ans
    
    def helper_func3(self):
        final_ans = self.helper_func2()
        #manually labelling with regex
        for i in final_ans.keys():
            op_pattern = "operations"
            bs_pattern = re.compile("(equity)|(liabilities)|(assets)|(balance sheet)")
            if (re.search(op_pattern,final_ans[i][0])):
                final_ans[i][1] = 'pl'
            elif (re.search(bs_pattern,final_ans[i][0])):
                final_ans[i][1] = 'bs'
        #splitting into 3 different dictionaries
        pl_ids = {}
        cf_ids = {}
        bs_ids = {}
        for i in final_ans.keys():
            if final_ans[i][1] == "pl":
                pl_ids[i] = final_ans[i]
            if final_ans[i][1] == "cf":
                cf_ids[i] = final_ans[i]
            if final_ans[i][1] == "bs":
                bs_ids[i] = final_ans[i]
        return pl_ids,cf_ids,bs_ids

if __name__ == "__main__":
   pl_ids,cf_ids,bs_ids = TableCategory("yahoo10-K.pdf",94,100).helper_func3()
