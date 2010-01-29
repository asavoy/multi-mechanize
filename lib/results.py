#!/usr/bin/env python
#  Copyright (c) 2010 Corey Goldberg (corey@goldb.org)
#  License: GNU LGPLv3
#  
#  This file is part of Multi-Mechanize


import time
from collections import defaultdict



def main():
    results = Results('results.csv')
    
    print 'test start: %s' % results.start_datetime
    print 'test finish: %s' % results.finish_datetime
    print ''
    print 'total transactions: %i' % results.total_transactions
    print 'error transactions: %i' % results.total_errors
    print ''
    
    
    
    # aggregate transaction times
    trans_timer_points = []  # [elapsed, timervalue]
    for resp_stats in results.resp_stats_list:
        t = (resp_stats.elapsed_time, resp_stats.trans_time)
        trans_timer_points.append(t)
    #print trans_timer_points
    
    throughputs = []  # [intervalnumber, numberofrequests]
    splat_series = split_series(trans_timer_points, 1)
    for i, bucket in enumerate(splat_series):
        t = (i, len(bucket))
        throughputs.append(t)
    #print throughputs
                
                
               
    # user group times
    for user_group_name in sorted(results.uniq_user_group_names):
        ug_timer_vals = []
        for resp_stats in results.resp_stats_list:
            if resp_stats.user_group_name == user_group_name: 
                ug_timer_vals.append(resp_stats.trans_time)
        print user_group_name
        print 'min: %.3f' % min(ug_timer_vals)
        print 'avg: %.3f' % avg(ug_timer_vals)
        print '80pct: %.3f' % percentile(ug_timer_vals, 80)
        print '90pct: %.3f' % percentile(ug_timer_vals, 90)
        print '95pct: %.3f' % percentile(ug_timer_vals, 95)
        print 'max: %.3f' % max(ug_timer_vals)
        print ''        
            
    # custom timers
    for timer_name in sorted(results.uniq_timer_names):
        custom_timer_vals = []
        for resp_stats in results.resp_stats_list:
            custom_timer_vals.append(resp_stats.custom_timers[timer_name])
        print timer_name
        print 'min: %.3f' % min(custom_timer_vals)
        print 'avg: %.3f' % avg(custom_timer_vals)
        print '80pct: %.3f' % percentile(custom_timer_vals, 80)
        print '90pct: %.3f' % percentile(custom_timer_vals, 90)
        print '95pct: %.3f' % percentile(custom_timer_vals, 95)
        print 'max: %.3f' % max(custom_timer_vals)
        print ''



class Results(object):
    def __init__(self, results_file_name):
        self.results_file_name = results_file_name
        self.total_transactions = 0
        self.total_errors = 0
        self.uniq_timer_names = set()
        self.uniq_user_group_names = set()
        
        self.resp_stats_list = self.__parse_file()
        
        self.epoch_start = self.resp_stats_list[0].epoch_secs
        self.epoch_finish = self.resp_stats_list[-1].epoch_secs
        self.start_datetime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.epoch_start))
        self.finish_datetime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.epoch_finish))
        
        
        
    def __parse_file(self):
        f = open(self.results_file_name, 'rb')
        resp_stats_list = []
        for line in f:
            fields = line.strip().split(',')
            
            request_num = int(fields[0])
            elapsed_time = float(fields[1])
            epoch_secs = int(fields[2])
            user_group_name = fields[3]
            trans_time = float(fields[4])
            status = fields[5]
            bytes_received = int(fields[6])
            error = fields[7]
            
            self.uniq_user_group_names.add(user_group_name)
            
            custom_timers = {}
            timers_string = ''.join(fields[8:]).replace('{', '').replace('}', '')
            splat = timers_string.split("'")[1:]
            timers = []
            vals = []
            for x in splat:
                if ':' in x:
                    x = float(x.replace(': ', ''))
                    vals.append(x)
                else:
                    timers.append(x)
                    self.uniq_timer_names.add(x)
            for timer, val in zip(timers, vals):
                custom_timers[timer] = val
            
            r = ResponseStats(request_num, elapsed_time, epoch_secs, user_group_name, trans_time, status, bytes_received, error, custom_timers)
            resp_stats_list.append(r)
            
            if error != "''":
                self.total_errors += 1
            self.total_transactions += 1
            
        return resp_stats_list    
   


class ResponseStats(object):
    def __init__(self, request_num, elapsed_time, epoch_secs, user_group_name, trans_time, status, bytes_received, error, custom_timers):
        self.request_num = request_num
        self.elapsed_time = elapsed_time
        self.epoch_secs = epoch_secs
        self.user_group_name = user_group_name
        self.trans_time = trans_time
        self.status = status
        self.bytes_received = bytes_received
        self.error = error
        self.custom_timers = custom_timers
        


def split_series(points, interval):
    offset = points[0][0]
    maxval = int((points[-1][0] - offset) // interval)
    vals = defaultdict(list)
    for key, value in points:
        vals[(key - offset) // interval].append(value)
    series = [vals[i] for i in xrange(maxval + 1)]
    return series



def avg(seq):
    return float(sum(seq) / len(seq)) 



def percentile(seq, percentile):
    i = int(len(seq) * (percentile / 100.0))
    seq.sort()
    return seq[i]



if __name__ == '__main__':
    main()
