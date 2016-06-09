#! /usr/bin/env python
# coding=utf-8
import pycurl
import StringIO
from lxml import etree
import datetime
import re
import time
import random
import json


def getList(page=1):
    useragent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:43.0) Gecko/20100101 Firefox/43.0"
    url = 'https://www.freelancer.com/freelancers/skills/php-Website_Design-Graphic_Design-html/%s/' % str(
        page)
    s = StringIO.StringIO()
    crl = pycurl.Curl()
    crl.setopt(pycurl.URL, url)
    crl.setopt(pycurl.REFERER, url)
    crl.setopt(pycurl.FOLLOWLOCATION, True)
    crl.setopt(pycurl.TIMEOUT, 60)
    crl.setopt(pycurl.ENCODING, 'gzip')
    crl.setopt(pycurl.USERAGENT, useragent)
    crl.setopt(pycurl.NOSIGNAL, True)
    crl.setopt(pycurl.WRITEFUNCTION, s.write)
    crl.perform()
    html = s.getvalue()
    # parsing html
    tree = etree.HTML(html)
    number = tree.xpath('//*[@id="freelancer_list"]/li')
    result = []
    result_id = []
    for i in range(1, len(number) + 1):
        node = tree.xpath(
            '//*[@id="freelancer_list"]/li[%s]/div[2]/h3/a' % str(i))
        node_id = tree.xpath(
            '//*[@id="freelancer_list"]/li[%s]/div[1]/a' % str(i))
        result_id.append(node_id[0].get('data-user_id'))
        result.append(node[0].get('href'))
    return result_id


def getReviews(user_id, offset=0, limit=11):
    useragent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:43.0) Gecko/20100101 Firefox/43.0"
    url = r'https://www.freelancer.com/api/projects/0.1/reviews/?compact=true&contest_details=false&contest_job_details=false&limit=' + str(limit) + r'&offset=' + str(offset) + r'&project_details=false&project_job_details=false&review_types%5B%5D=project&review_types%5B%5D=contest&role=freelancer&to_users%5B%5D=' + str(user_id) + r'&user_avatar=false&user_country_details=false&user_details=false'
    s = StringIO.StringIO()
    crl = pycurl.Curl()
    crl.setopt(pycurl.URL, url)
    crl.setopt(pycurl.TIMEOUT, 600)
    crl.setopt(pycurl.USERAGENT, useragent)
    crl.setopt(pycurl.WRITEFUNCTION, s.write)
    crl.perform()
    result = s.getvalue()
    json_result = json.loads(result)
    number = len(json_result['result']['reviews'])
    reviews = json_result['result']['reviews']
    projects_id = []
    for i in range(number):
        if reviews[i]["review_project_status"] == "complete":
            projects_id.append(reviews[i]['project_id'])
    #return len(projects_id)
    #print projects_id
    return projects_id


def nextDays(now, day):
    now
    now = now.split('T')[0]
    now_list = now.split('-')
    d1 = datetime.date(int(now_list[0]), int(now_list[1]), int(now_list[2]))
    d1 = d1 + datetime.timedelta(days=day)
    return d1.strftime('%Y-%m-%d')


def getProjectPeriod(project_id, worker_id):
    useragent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:43.0) Gecko/20100101 Firefox/43.0"
    url = 'https://www.freelancer.com/ajax/project/getBids.php?project_id=%s' % str(project_id)
    s = StringIO.StringIO()
    crl = pycurl.Curl()
    crl.setopt(pycurl.URL, url)
    crl.setopt(pycurl.TIMEOUT, 30)
    crl.setopt(pycurl.USERAGENT, useragent)
    crl.setopt(pycurl.WRITEFUNCTION, s.write)
    crl.perform()
    result = s.getvalue()
    json_result = json.loads(result)
    result = {}
    for it in json_result['bids']:
        if it['users_id'] == worker_id and it['completed'] == True:
            result['startedOn'] = it['submitdate'].replace(' ', 'T')
            result['endedOn'] = nextDays(result['startedOn'], int(it['period']))
            # result['startedOn'], it['period'], result['endedOn']
            result['project_id'] = project_id
            #print result
            return result
    return None


def getAllRecord(user_id):
    record = []
    projects_id = getReviews(user_id, 0, 30)
    #getReviews(user_id, 10, 11)
    for pid in projects_id:
        try:
            item = getProjectPeriod(str(pid), str(user_id))
            if item is not None:
                record.append(item)
        except:
            print 'TimeOut'
    return record


def output(uid, record):
    with open('result.txt', 'a') as f:
        f.write(str(uid) + ':' + json.dumps(record) + '\n')


if __name__ == "__main__":
    for i in range(6, 51):
        print 'page ', i
        try:
            users_id = getList(i)
            for uid in users_id:
                print uid
                record = getAllRecord(uid)
                output(uid, record)
        except:
            print 'pass, page', i
