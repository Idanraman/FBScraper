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
import string
import grequests

import gevent.monkey
gevent.monkey.patch_socket()
from gevent.pool import Pool
import requests

class Scraper():
    allcomments=[]
    access_token = '278563542169852|5f6a1af8b2d861e01b1c0f1f41dc67ae'
    group_name = 'Facts'
    group_id = '140579966013837'
    sample_size = 120
    stamp = group_name + '/' + group_id + '_' + \
            group_name + '_' + str(sample_size) + '_'
    def main(self):
        allresults = []
        time_stamp = ''
        group_name = self.group_name
        group_id = self.group_id
        sample_size = self.sample_size
        if not os.path.exists(group_name):
            os.makedirs(group_name)

        if os.path.isfile('dataset.txt'):
            print('using provided dataset')
            allresults = self.extract()

        else:
            for x in range(sample_size):
                print(time_stamp, " iteration :", x)
                algo = self.getfeed(group_id, time_stamp=time_stamp)
                if algo[2] != 200:
                    break
                time_stamp = self.timestamp(algo[1])
                allresults = algo[0] + allresults


        meta = self.metadata(allresults)
        if 0:
            allresults = sorted(allresults, key=lambda x: x['comments'])
            topcomments = allresults[len(allresults) - 1]
            allresults = sorted(allresults, key=lambda x: x['shares'])
            topshares = allresults[len(allresults) - 1]
            allresults = sorted(allresults, key=lambda x: x['likes'])
            toplikes = allresults[len(allresults) - 1]
            allresults = sorted(allresults, key=lambda x: x['date'])

            stats = [toplikes, topcomments, topshares]
            pp = pprint.PrettyPrinter(depth=6)
            output = pp.pformat(stats)
            output2 = pp.pformat(allresults)
            output3 = pp.pformat(meta[0])
            output4 = pp.pformat(meta[1])
            with open(self.stamp + 'stats.txt', 'w', encoding='utf-8') as f:
                f.write(str(output))
            with open(self.stamp + 'outpost.txt', 'w', encoding='utf-8') as f:
                f.write(str(output2))
            with open(self.stamp + 'meta.txt', 'w', encoding='utf-8') as f:
                f.write(str(output3))
            with open(self.stamp + 'meta_10.txt', 'w', encoding='utf-8') as f:
                f.write(str(output4))
            with open(self.stamp + 'words.txt', 'w', encoding='utf-8') as f:
                f.write(str(meta[2]))
            with open(self.stamp + 'words_10.txt', 'w', encoding='utf-8') as f:
                f.write(str(meta[3]))

    def extract(self, filename='dataset.txt'):
        with open('dataset.txt', encoding='utf-8') as f:
            a = f.read()
            content = ast.literal_eval(a)
        return(content)

    def metadata(self, allresults):
        self.totalcomments(allresults)

        self.batchmaker(allresults)
        print(len(self.allcomments))
        common_comment = self.colameter(self.allcomments)
        print('kaaa')
        with open(self.stamp + 'comments.txt', 'w', encoding='utf-8') as f:
                f.write(str(common_comment))

        words = self.colameter(allresults)
        totals_pic = self.photopre(allresults)
        like_hrs = self.likeshours(allresults)
        like_days,post_days = self.likesdays(allresults)
        like_length = self.likeslength(allresults)

        allresults = sorted(allresults, key=lambda x: x['likes'])
        allresults = allresults[int(len(allresults) * 0.9):]

        words_10 = self.colameter(allresults)
        totals_pic_10 = self.photopre(allresults)
        like_hrs_10 = self.likeshours(allresults)
        like_days_10,post_days_10 = self.likesdays(allresults)

        return(
            {'pictures': totals_pic,
             'like_hrs': like_hrs,
             'like_days': like_days,
             'post_days': post_days,
             'like_length': like_length,
             },
            {'pictures_10': totals_pic_10,
             'like_hrs_10': like_hrs_10,
             'like_days_10': like_days_10,
             'post_days_10': post_days_10}
        , words,words_10)

    def Badchars(self, inputString):
        return any(x.isdigit() or x.islower() or x.isupper() for x in inputString)

    def colameter(self, allresults, keywordlist=[]):
        chars = string.ascii_uppercase + string.digits + string.ascii_lowercase
        words = []

        with open("stopwords.txt", "r") as ins:
            array = []
            for line in ins:
                array.append(line[:-1])

        for result in allresults:
            words += re.findall(r'\w+', result['message'])

        print(len(words))
        words = [w for w in words if not w in array]  # Stopwords filtering
        words = [w for w in words if not self.Badchars(w)] # English and numerics
        words = [w for w in words if not len(w) == 1]  # Oneletter and numerics
        print(len(words))

        # print(newlist)
        print(len(allresults))
        return(str(Counter(words).most_common()))

    def batchmaker(self,allresults,):
        idlist = []
        URL2 = 'https://graph.facebook.com/'
        for result in allresults:
            idlist.append(result['id'])
        batch=[]
        batches=[]
        cred = '/comments/?key=value&access_token=' + self.access_token + \
            '&fields=likes.limit(0).summary(true),message&limit=10000'
        for idx in idlist:
            URL = '/' + idx + cred
            a={"method":"GET", "relative_url":URL}
            batch.append(a)
            if len(batch) % 50 ==0 and len(batch)>1:
                batches.append(batch)
                batch=[]

        pool = Pool(50)
        globvar = []
        def fetch(b):
            r = requests.post(URL2,
            data={'access_token': self.access_token, 'batch': str(b[1])})
            pp = pprint.PrettyPrinter(depth=6)
            with open(self.group_name + '/com/'+str(b[0])+'.txt', 'w', encoding='utf-8') as f:
                try:
                    for post in r.json():
                        a = json.loads(post['body'])
                        for comment in a['data']:
                            comment['likes']=comment['likes']['summary']['total_count']
                            self.allcomments.append(comment)
                        a['shnoozel']=a['data']
                        del a['data']
                        try: del a['paging']
                        except: pass
                        output = pp.pformat(a)
                        f.write(str(output))
                        f.write('\n')
                except:
                    print('probably limit reached, try to switch key')
            print(r.status_code)
        for a,b in enumerate(batches):
            pool.spawn(fetch,[a,b])
        pool.join()
        print('made it')

    def do_something(self,response):
        print(response.status_code)

    def totalcomments(self, allresults):
        total = 0
        for result in allresults:
                total += int(result['comments'])
        print('comments: ',total)

    def photopre(self, allresults):
        batch_size = int(len(allresults) / 100)
        totals_pic = [0] * 100
        for idx, result in enumerate(allresults):
            precentile = int(idx / len(allresults) * 100)
            try:
                totals_pic[precentile] += result['picture']
            except:
                pass
        totals_pic = [x / batch_size for x in totals_pic]
        x, y = range(100), totals_pic
        plt.bar(x, y, label="bars1")
        plt.legend()
        # plt.show()
        return totals_pic

    def likeslength(self, allresults):
        batch_size = int(len(allresults) / 100)
        totals_len = [0] * 100
        for idx, result in enumerate(allresults):
            precentile = int(idx / len(allresults) * 100)
            try:
                totals_len[precentile] += result['txt_len']
            except:
                pass
        totals_len = [x / batch_size for x in totals_len]
        x, y = range(100), totals_len
        plt.bar(x, y, label="bars1")
        plt.legend()
        # plt.show()
        return totals_len

    def likeshours(self, allresults):
        post_hrs, like_hrs = [0] * 24, [0] * 24
        for idx, result in enumerate(allresults):
            precentile = result['seconds']
            try:
                like_hrs[precentile] += result['likes']
                post_hrs[precentile] += 1
            except:
                pass
        for x in range(24):
            try:
                like_hrs[x] = like_hrs[x] / post_hrs[x]
            except:
                like_hrs[x] = 0

        x, y = range(24), like_hrs
        plt.bar(x, y, label="bars1")
        plt.legend()
        # plt.show()
        return(like_hrs)

    def likesdays(self, allresults):
        post_days, like_days = [0] * 7, [0] * 7
        for idx, result in enumerate(allresults):
            precentile = result['day']
            try:
                like_days[precentile] += result['likes']
                post_days[precentile] += 1
            except:
                pass
        for x in range(7):
            try:
                like_days[x] = like_days[x] / post_days[x]
            except:
                like_days[x] = 0
        return(like_days,post_days)

    def timestamp(self, formatted):
        time_stamp = time.mktime(datetime.datetime.strptime(
            formatted, "%Y-%m-%dT%H:%M:%S+0000").timetuple())
        return str(int(time_stamp))

    def getgapi(self, url='', time_stamp='', batch_size=100):
        cred = '?key=value&access_token='+ self.access_token + '&limit=' + \
            str(batch_size + 50) + \
            '&fields=comments.limit(0).summary(true),likes.limit(0).summary(true),shares,message,picture'
        URL = 'https://graph.facebook.com/' + url + cred
        if time_stamp != '':
            URL += "&until=" + time_stamp

        r = requests.get(URL)
        if r.status_code != 200:
            return(self.getgapi(url=url, time_stamp=time_stamp, batch_size=batch_size))
        try:
            return(r.status_code, r.json(), r.elapsed.total_seconds())
        except:
            return(self.getgapi(url=url, time_stamp=time_stamp, batch_size=batch_size))

    def getpage(self, pageid):
        pass

    def getfeed(self, groupid, time_stamp=''):
        batch_size = 200
        in_data = self.getgapi(url=groupid + '/posts/',
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
                    message = post['message']
                    txt_len = len(message)
                except:
                    message = ''

                userid = post['id']
                link = 'https://www.facebook.com/' + \
                    str(post['id']).replace('_', '/posts/')
                date = post['created_time']

                hour = datetime.datetime.strptime(
                    str(date), "%Y-%m-%dT%H:%M:%S+0000").strftime("%H")
                minute = datetime.datetime.strptime(
                    str(date), "%Y-%m-%dT%H:%M:%S+0000").strftime("%M")
                second = datetime.datetime.strptime(
                    str(date), "%Y-%m-%dT%H:%M:%S+0000").strftime("%S")

                seconds = (int(hour) * 3600 + int(minute) *
                           60 + int(second) + 7200) % 86400
                seconds = (int(hour) + 2) % 24
                day = (datetime.datetime.strptime(
                    str(date), "%Y-%m-%dT%H:%M:%S+0000").weekday() + 1) % 7
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
                    'message': message,
                    'link': link,
                    'id': userid,
                    'likes': likes,
                    'comments': comments,
                    'shares': shares,
                    'picture': picture,
                    'seconds': seconds,
                    'day': day,
                })
            except:
                print('somthing didnt went right')
                pass

        if len(clean_posts) < batch_size:
            return(0, 0, 500)
        foo = sorted(clean_posts, key=lambda x: x['date'])
        x = foo[len(foo) - batch_size - 1]
        time = x['date']
        x = foo[len(foo) - batch_size - 1:]

        print(len(clean_posts))
        return(x, time, 200)
if __name__ == '__main__':
    a = Scraper()
    Scraper.main(a)
