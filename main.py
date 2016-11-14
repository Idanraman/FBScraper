import requests
import pprint
import time
import datetime
import operator
import os.path
import json
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import ast
from collections import defaultdict
import collections
from collections import Counter
import re

class Scraper():

    def main(self):
        allresults = []
        time_stamp = ''
        group_name = 'Facts'
        group_id = '140579966013837'
        sample_size = 120
        stamp = group_id+'_'+group_name+'_'+str(sample_size)+'_'

        if os.path.isfile('dataset.txt'):
            allresults=self.extract()

        else:
            for x in range(sample_size):
                print(time_stamp, " iteration :", x)
                algo = self.getfeed(group_id, time_stamp=time_stamp)
                if algo[2] != 200: break
                time_stamp = self.timestamp(algo[1])
                allresults = algo[0] + allresults

        meta = self.metadata(allresults)

        if 1:
            allresults = sorted(allresults, key=lambda x: x['comments'])
            topcomments = allresults[len(allresults) - 1]
            allresults = sorted(allresults, key=lambda x: x['shares'])
            topshares = allresults[len(allresults) - 1]
            allresults = sorted(allresults, key=lambda x: x['likes'])
            toplikes = allresults[len(allresults) - 1]
            allresults = sorted(allresults, key=lambda x: x['date'])

            stats = [toplikes , topcomments , topshares]

            pp = pprint.PrettyPrinter(depth=6)
            output = pp.pformat(stats)
            output2 = pp.pformat(allresults)
            output3 = pp.pformat(meta)
            with open(stamp+'stats.txt', 'w', encoding='utf-8') as f:
                f.write(str(output))
            with open(stamp+'outpost.txt', 'w', encoding='utf-8') as f:
                f.write(str(output2))
            with open(stamp+'meta.txt', 'w', encoding='utf-8') as f:
                f.write(str(meta))


    def extract(self,filename='dataset.txt'):
        with open('dataset.txt',encoding='utf-8') as f:
            a = f.read()
            content = ast.literal_eval(a)
        return(content)


    def metadata(self,allresults):
        words = self.colameter(allresults,['פיצה','קולה','מים','טלפון','פלאפון'])

        totals_pic = self.photopre(allresults)
        like_hrs = self.likeshours(allresults)
        like_days = self.likesdays(allresults)

        allresults = sorted(allresults, key=lambda x: x['likes'])
        allresults = allresults[int(len(allresults)*0.9):]

        totals_pic_10 = self.photopre(allresults)
        like_hrs_10 = self.likeshours(allresults)
        like_days_10 = self.likesdays(allresults)

        return([
            {'pictures':totals_pic,
            'like_hrs':like_hrs,
            'like_days':like_days}
            ,
            {'pictures_10':totals_pic_10,
            'like_hrs_10':like_hrs_10,
            'like_days_10':like_days_10}
            ])


    def colameter(self,allresults,keywordlist):
        d = defaultdict(int)
        words=[]
        total_words = [0]*len(keywordlist)

        for result in allresults:
            for idx,keyword in enumerate(keywordlist):
                total_words[idx]+=result['text'].count(keyword)
            words += re.findall(r'\w+', result['text'])

        newlist = [x / len(allresults) for x in total_words]

        print(total_words)
        print(newlist)
        print(len(allresults))

        with open('words_uvdot.txt', 'w', encoding='utf-8') as f:
            f.write(str(Counter(words).most_common()))


    def photopre(self,allresults):
        batch_size = int(len(allresults)/100)
        totals_pic = [0]*100
        for idx, result in enumerate(allresults):
            precentile = int(idx/len(allresults)*100)
            try: 
                totals_pic[precentile]+=result['picture']
            except:
                pass
        totals_pic = [x / batch_size for x in totals_pic]
        x,y = range(100), totals_pic
        plt.bar(x,y,label="bars1")
        plt.legend()
        #plt.show()
        return totals_pic


    def likeshours(self,allresults):
        post_hrs,like_hrs = [0]*24, [0]*24
        for idx, result in enumerate(allresults):
            precentile = result['seconds']
            try: 
                like_hrs[precentile]+=result['likes']
                post_hrs[precentile]+=1
            except:
                pass
        for x in range(24): 
            try: like_hrs[x]=like_hrs[x]/post_hrs[x]
            except: like_hrs[x] = 0

        x,y = range(24), like_hrs
        plt.bar(x,y,label="bars1")
        plt.legend()
        #plt.show()
        return(like_hrs)


    def likesdays(self,allresults):
        post_days,like_days = [0]*7,[0]*7
        for idx, result in enumerate(allresults):
            precentile = result['day']
            try: 
                like_days[precentile]+=result['likes']
                post_days[precentile]+=1
            except:
                pass
        for x in range(7):
            try: like_days[x]=like_days[x]/post_days[x]
            except: like_days[x]=0
        return(like_days)


    def timestamp(self, formatted):
        time_stamp = time.mktime(datetime.datetime.strptime(
            formatted, "%Y-%m-%dT%H:%M:%S+0000").timetuple())
        return str(int(time_stamp))


    def getgapi(self, url='', time_stamp='', batch_size=100):
        cred = '?key=value&access_token=110910202352439|c6cbe0499f9fd5a401bb1905be519b21&limit=' + \
            str(batch_size + 50) + \
            '&fields=comments.limit(1).summary(true),likes.limit(1).summary(true),shares,message,picture'
        URL = 'https://graph.facebook.com/' + url + cred
        if time_stamp != '':
            URL += "&until=" + time_stamp
        r = requests.get(URL)
        if r.status_code!=200:
            return(self.getgapi(url=url, time_stamp=time_stamp, batch_size=batch_size))
        try:
            return(r.status_code, r.json(), r.elapsed.total_seconds())
        except:
            return(self.getgapi(url=url, time_stamp=time_stamp, batch_size=batch_size))


    def getfeed(self, groupid, time_stamp=''):
        batch_size = 450
        in_data = self.getgapi(url=groupid + '/feed/',
                               time_stamp=time_stamp,
                               batch_size=batch_size)
        print(in_data[2])
        in_data = in_data[1]
        try:
            posts = in_data['data']
        except:
            print("An error has accurd. data: \n\n", in_data)

        clean_posts = []
        for post in posts:
            try:
                try:
                    text = post['message']
                    txt_len = len(text)
                except:
                    text = ''
                userid = post['id']
                link = 'https://www.facebook.com/' + \
                    str(post['id']).replace('_', '/posts/')
                date = post['updated_time']

                hour = datetime.datetime.strptime(
                    str(date), "%Y-%m-%dT%H:%M:%S+0000").strftime("%H")
                minute = datetime.datetime.strptime(
                    str(date), "%Y-%m-%dT%H:%M:%S+0000").strftime("%M")
                second = datetime.datetime.strptime(
                    str(date), "%Y-%m-%dT%H:%M:%S+0000").strftime("%S")

                seconds = (int(hour)*3600+int(minute)*60+int(second)+7200)%86400
                seconds = (int(hour)+2)%24
                day = (datetime.datetime.strptime(
                    str(date), "%Y-%m-%dT%H:%M:%S+0000").weekday()+1)%7
                try:
                    likes = post['likes']['summary']['total_count']
                except:
                    likes = 0
                try:
                    comments = post['comments']['summary']['total_count']
                except:
                    comments = 0
                try:
                    shares = post['shares']['count']
                except:
                    shares = 0
                try:
                    post['shares']
                except:
                    pass
                try:
                    post['picture']
                    picture = 1
                except:
                    picture = 0
                clean_posts.append({
                    'txt_len': txt_len,
                    'date': date,
                    'text': text,
                    'user id': userid,
                    'link': link,
                    'id': post['id'],
                    'likes': likes,
                    'comments': comments,
                    'shares': shares,
                    'picture':picture,
                    'seconds':seconds,
                    'day':day,
                })
            except:
                pass
        if len(clean_posts) < batch_size:
            return(0, 0, 500)
        foo = sorted(clean_posts, key=lambda x: x['date'])
        x = foo[len(foo)-batch_size-1]
        time = x['date']
        x = foo[len(foo)-batch_size-1:]

        print(len(clean_posts))
        return(x, time, 200)
if __name__ == '__main__':
    a = Scraper()
    Scraper.main(a)
