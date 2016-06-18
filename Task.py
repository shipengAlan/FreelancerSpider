#! /usr/bin/env python
# coding=utf-8
import pycurl
import StringIO
from lxml import etree
import json


def getList(page=1):
    useragent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:43.0) Gecko/20100101 Firefox/43.0"
    url = 'https://www.freelancer.com/jobs/Mobile_Phone/%s/' % str(page)
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
    project_num = tree.xpath('//*[@id="project_table_static"]/tbody/tr')
    f = open('task.txt', 'a')
    for i in range(1, len(project_num) + 1):
        task = {}
        task_items = tree.xpath(
            '//*[@id="project_table_static"]/tbody/tr[%s]/td' % str(i))
        endTime = tree.xpath(
            '//*[@id="project_table_static"]/tbody/tr[%s]/td[6]/small' % str(i))
        task_skills = tree.xpath(
            '//*[@id="project_table_static"]/tbody/tr[%s]/td[4]/a' % str(i))
        skills_list = []
        for k in range(len(task_skills)):  # task_items
            s = task_skills[k].text
            skills_list.append(s.replace(' ', '-'))
        task['startTime'] = task_items[4].text
        task['endTime'] = task_items[5].text
        task['endTimeS'] = endTime[0].text
        task['skills'] = skills_list
        f.write(json.dumps(task) + '\n')
    f.close()
    # tr_even = tr_even[1].xpath('/td')
    # print len(tr_even)
    # return result_id


if __name__ == "__main__":
    for i in range(1, 501):
        try:
            print i
            getList(i)
        except:
            print 'time-out', i
