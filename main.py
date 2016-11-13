import requests
import pprint
import time
import datetime
import operator
import itertools
import collections


class Scraper():

    def main(self):
        allresults = []
        time_stamp = ''
        for x in range(30):
            print(time_stamp, " iteration :", x)
            # Enter group ID here
            algo = self.getfeed('140579966013837', time_stamp=time_stamp)
            if algo[2] != 200:
                break
            time_stamp = self.timestamp(algo[1])
            allresults = algo[0] + allresults

        allresults = sorted(allresults, key=lambda x: x[1]['likes'])
        toplikes = allresults[len(allresults) - 1]
        allresults = sorted(allresults, key=lambda x: x[1]['comments'])
        topcomments = allresults[len(allresults) - 1]
        allresults = sorted(allresults, key=lambda x: x[1]['shares'])
        topshares = allresults[len(allresults) - 1]

        stats = toplikes + topcomments + topshares
        pp = pprint.PrettyPrinter(depth=6)
        output = pp.pformat(stats)
        with open('clean_posts.txt', 'w', encoding='utf-8') as f:
            f.write(str(output))

    def timestamp(self, formatted):
        time_stamp = time.mktime(datetime.datetime.strptime(
            formatted, "%Y-%m-%dT%H:%M:%S+0000").timetuple())
        return str(int(time_stamp))

    def getgapi(self, url='', time_stamp='', batch_size=100):
        cred = '?key=value&access_token=110910202352439|c6cbe0499f9fd5a401bb1905be519b21&limit=' + \
            str(batch_size + 100) + \
            '&fields=comments.limit(1).summary(true),likes.limit(1).summary(true),shares,message'
        URL = 'https://graph.facebook.com/' + url + cred
        if time_stamp != '':
            URL += "&until=" + time_stamp
        r = requests.get(URL)
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
        # print(type(in_data['data']))
        try:
            posts = in_data['data']
        except:
            print("An error has accurd. data: \n\n", in_data)

        clean_posts = collections.OrderedDict()
        for post in posts:
            try:
                try:
                    text = post['message']
                except:
                    text = ''
                userid = post['id']
                link = 'https://www.facebook.com/' + \
                    str(post['id']).replace('_', '/posts/')
                date = post['updated_time']
                try:
                    likes = post['likes']['summary']['total_count']
                    # print("happened")
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
                clean_posts[date] = {
                    'text': text,
                    'user id': userid,
                    'link': link,
                    'id': post['id'],
                    'likes': likes,
                    'comments': comments,
                    'shares': shares
                }
            except:
                pass
        if len(clean_posts) < 500:
            return(0, 0, 500)
        foo = collections.OrderedDict(
            sorted(clean_posts.items(), key=lambda x: x[0]))

        print(len(clean_posts))

        x = list(itertools.islice(
            foo.items(),
            len(foo) - batch_size - 1,
            len(foo) - batch_size))

        time = x[0][0]

        x = list(itertools.islice(
            foo.items(),
            len(foo) - batch_size,
            len(foo)))

        return(x, time, 200)
if __name__ == '__main__':
    a = Scraper()
    Scraper.main(a)
