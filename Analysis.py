#! /usr/bin/env python
#coding=utf-8
import json
import datetime


# 按行读取数据，并进行处理
def ReadFile(bound=0.5, C=1):
    i = 0
    count = 0
    with open('result.txt', 'r') as f:
        while 1:
            line = f.readline()
            if not line:
                break
            list_items = line.split(':', 1)
            items = json.loads(list_items[1])
            # if list_items[1].strip('\n') != "null":
            if len(items) > 1:
                i += 1
                # print list_items[0]
                # print len(items)
                c = handling(items, C)
                """
                if c == 0:
                    print list_items[0]
                else:
                    count += c
                """
                if c is None:
                    i -= 1
                elif c >= bound:
                    count += 1
    # print count, i
    return float(count)/i



# 比较两个时间 2015-10-01 和 2015-09-10, 只具体到月，如果a<b输出1 a>b输出-1，等于为0
def compare(a, b):
    a = a.split('T')[0]
    b = b.split('T')[0]
    a_list = a.split('-')
    b_list = b.split('-')
    for i in range(len(a_list)):
        if int(a_list[i]) < int(b_list[i]):
            return 1
        elif int(a_list[i]) > int(b_list[i]):
            return -1
    return 0


# 根据当前时间返回下一个月（有可能跨年） 2015-12-01的下个月为2016-01-01
def nextTime(now):
    now_list = now.split('-')
    if int(now_list[1]) < 12:
        if(int(now_list[1]) + 1 < 10):
            now_list[1] = '0' + str(int(now_list[1]) + 1)
        else:
            now_list[1] = str(int(now_list[1]) + 1)

    else:
        now_list[1] = str('01')
        now_list[0] = str(int(now_list[0]) + 1)
    return '-'.join(now_list)


# 处理某个人的历史任务数据：1、只保留任务起止时间信息 2、将任务按照起始时间排序
# 3、计算有没有重叠的工人
def handling(inputData, C=1):
    items = []
    all_time_point = []
    for it in inputData:
        dict_item = {}
        dict_item['startedOn'] = it['startedOn']
        dict_item['endedOn'] = it['endedOn']
        if dict_item['endedOn'] is None:
            print 'Error'
            dict_item['endedOn'] = it['startedOn']  # nextTime(it['startedOn'])
        # sort
        if len(items) == 0:
            items.append(dict_item)
        else:
            index = -1
            for i in range(len(items)):
                if compare(items[i]['startedOn'], dict_item['startedOn']) == -1:
                    index = i
                    break
            if index == -1:
                items.append(dict_item)
            else:
                items.insert(index, dict_item)

    # add time point by order
    for dict_item in items:
        # 1 start time point
        if len(all_time_point) == 0:
            all_time_point.append(dict_item['startedOn'])
            if compare(all_time_point[0], dict_item['startedOn']) == 1:
                all_time_point.append(dict_item['endedOn'])
        else:
            index = -1
            for i in range(len(all_time_point)):
                if compare(all_time_point[i], dict_item['startedOn']) == -1:
                    index = i
                    break
                elif compare(all_time_point[i], dict_item['startedOn']) == 0:
                    index = -2
                    break
            if index == -1:
                all_time_point.append(dict_item['startedOn'])
            elif index != -2:
                all_time_point.insert(index, dict_item['startedOn'])
            # 2 start end point
            index = -1
            for i in range(len(all_time_point)):
                if compare(all_time_point[i], dict_item['endedOn']) == -1:
                    index = i
                    break
                elif compare(all_time_point[i], dict_item['endedOn']) == 0:
                    index = -2
                    break

            if index == -1:
                all_time_point.append(dict_item['endedOn'])
            elif index != -2:
                all_time_point.insert(index, dict_item['endedOn'])
    # print items
    # print '---'
    # print all_time_point
    """
    for i in range(1, len(items)):
        if compare(items[i-1]['endedOn'], items[i]['startedOn']) == -1:
            print items
            return 0
    print items
    """
    # print items
    return handlingRadio(items, all_time_point, C)
    # return 1


def calGap(a, b):
    a = a.split('T')[0]
    b = b.split('T')[0]
    a = a.split('-')
    b = b.split('-')
    d1 = datetime.date(int(a[0]), int(a[1]), int(a[2]))
    d2 = datetime.date(int(b[0]), int(b[1]), int(b[2]))
    gap = d2 - d1
    return gap.days


def handlingRadio(items, all_time_point, C=1):
    count = 0
    start = None
    days1 = 0
    s0 = None
    days0 = 0
    for now in all_time_point:
        for it in items:
            if compare(now, it['endedOn']) == 0:
                count -= 1
        for it in items:
            if compare(now, it['startedOn']) == 0:
                count += 1
        if count == C:
            if start is None:
                start = now
        else:
            end = now
            if start is not None:
                # print start, ' to ', end
                days1 += calGap(start, end)
                start = None

        if count == 0:
            s0 = now
        else:
            e0 = now
            if s0 is not None:
                days0 += calGap(s0, e0)
                s0 = None
    if start != None and count == C:
        days1 += calGap(start, all_time_point[-1])
    if s0 != None and count == 0:
        days0 += calGap(s0, all_time_point[-1])
    all_days = calGap(all_time_point[0], all_time_point[-1])

    # print all_days, days0, days1
    # if days1 == 0 and (all_days - days0) != 0:
        # print "T_T"
    # print float(days1)
    if all_days - days0 != 0:
        return float(days1) / (all_days - days0)
    else:
        return None


if __name__ == "__main__":
    b = 0.1
    while b < 1:
        radio = ReadFile(b, 3)
        print b, radio*100
        b += 0.1
