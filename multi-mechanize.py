#!/usr/bin/env python
#  Copyright (c) 2010 Corey Goldberg (corey@goldb.org)
#  License: GNU GPLv3
#  
#  This file is part of Multi-Mechanize:
#       Multi-Process, Multi-Threaded, Web Load Generator, with python-mechanize agents
#
#  requires Python 2.6+



import ConfigParser
import multiprocessing
import os
import Queue
import sys
import threading
import time

config = ConfigParser.ConfigParser()
config.read('config.cfg')
script_dir = config.get('global', 'script_directory')
exec 'from %s import *' % script_dir            
            
            

def main():
    run_time, rampup, user_group_configs = configure()
    
    # this queue is shared between all processes/threads
    queue = multiprocessing.Queue()
    r = Results(queue)
    r.daemon = True
    r.start()
    
    user_groups = [] 
    for ug_config in user_group_configs:
        ug = UserGroup(queue, ug_config.name, ug_config.num_threads, ug_config.script_file, run_time, rampup)
        user_groups.append(ug)    
    [user_group.start() for user_group in user_groups]
    
    start_time = time.time() 
    
    print '\n  user_groups:  %i' % len(user_groups)
    print '  threads: %i\n' % (ug_config.num_threads * len(user_groups))
    p = ProgressBar(run_time)
    elapsed = 0
    while [user_group for user_group in user_groups if user_group.is_alive()] != []:
        p.update_time(elapsed)
        if sys.platform.startswith('win'):
            print p, '\r',
        else:
            print p
            sys.stdout.write(chr(27) + '[A' )
        time.sleep(1)
        elapsed = time.time() - start_time
    print p
    if not sys.platform.startswith('win'):
        print
        
        
        
        
        
        
        

def configure():
    user_group_configs = []
    config = ConfigParser.ConfigParser()
    config.read('config.cfg')
    for section in config.sections():
        if section == 'global':
            run_time = int(config.get(section, 'run_time'))
            rampup = int(config.get(section, 'rampup'))
        else:
            threads = int(config.get(section, 'threads'))
            script = config.get(section, 'script')
            user_group_name = section
            ug_config = UserGroupConfig(threads, user_group_name, script)
            user_group_configs.append(ug_config)
    
    return (run_time, rampup, user_group_configs)
        


class UserGroupConfig(object):
    def __init__(self, num_threads, name, script_file):
        self.num_threads = num_threads
        self.name = name
        self.script_file = script_file
    
    
    
class UserGroup(multiprocessing.Process):
    def __init__(self, queue, user_group_name, num_threads, script_file, run_time, rampup):
        multiprocessing.Process.__init__(self)
        self.queue = queue
        self.user_group_name = user_group_name
        self.num_threads = num_threads
        self.script_file = script_file
        self.run_time = run_time
        self.rampup = rampup
        self.start_time = time.time()
        
    def run(self):
        self.running = True
        threads = []
        for i in range(self.num_threads):
            spacing = float(self.rampup) / float(self.num_threads)
            if i > 0:
                time.sleep(spacing)
            agent_thread = Agent(self.queue, self.start_time, self.run_time, self.user_group_name, self.script_file)
            agent_thread.daemon = True
            threads.append(agent_thread)
            agent_thread.start()            
        for agent_thread in threads:
            agent_thread.join()
        


class Agent(threading.Thread):
    def __init__(self, queue, start_time, run_time, user_group_name, script_file):
        threading.Thread.__init__(self)
        self.queue = queue
        self.start_time = start_time
        self.run_time = run_time
        self.user_group_name = user_group_name
        self.script_file = script_file
        
        # choose timer to use
        if sys.platform.startswith('win'):
            self.default_timer = time.clock
        else:
            self.default_timer = time.time
            
    def run(self):
        elapsed = 0
        error = ''
        while elapsed < self.run_time:
            module_name = self.script_file.replace('.py', '')
            trans = eval(module_name + '.Transaction()')
            
            start = self.default_timer()  
            
            try:
                trans.run()
                status = 'PASS'
            except Exception, e:
                status = 'FAIL'
                error = str(e)

            finish = self.default_timer()
            
            scriptrun_time = finish - start
            elapsed = time.time() - self.start_time 
            fields = (elapsed, self.user_group_name, scriptrun_time, status, trans.bytes_received, trans.custom_timers, error)
            self.queue.put(fields)
            


class Results(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.trans_count = 0
    
    def run(self):
        with open('results.csv', 'w') as f:     
            while True:
                try:
                    elapsed, self.user_group_name, scriptrun_time, status, bytes_received, custom_timers, error = self.queue.get(False)
                    self.trans_count += 1
                    f.write('%i,%.3f,%s,%.3f,%s,%i,%s,%s\n' % (self.trans_count, elapsed, self.user_group_name, scriptrun_time, status, bytes_received, repr(custom_timers), repr(error)))
                    f.flush()
                    #print '%i, %.3f, %s, %.3f, %s, %i, %s, %s' % (self.trans_count, elapsed, self.user_group_name, scriptrun_time, status, bytes_received, repr(custom_timers), repr(error))
                except Queue.Empty:
                    time.sleep(.1)



class ProgressBar:
    def __init__(self, duration):
        self.duration = duration
        self.prog_bar = '[]'
        self.fill_char = '='
        self.width = 40
        self.__update_amount(0)
    
    def __update_amount(self, new_amount):
        percent_done = int(round((new_amount / 100.0) * 100.0))
        all_full = self.width - 2
        num_hashes = int(round((percent_done / 100.0) * all_full))
        self.prog_bar = '[' + self.fill_char * num_hashes + ' ' * (all_full - num_hashes) + ']'
        pct_place = (len(self.prog_bar) / 2) - len(str(percent_done))
        pct_string = '%i%%' % percent_done
        self.prog_bar = self.prog_bar[0:pct_place] + \
            (pct_string + self.prog_bar[pct_place + len(pct_string):])
        
    def update_time(self, elapsed_secs):
        self.__update_amount((elapsed_secs / float(self.duration)) * 100.0)
        self.prog_bar += '  %ds/%ss' % (elapsed_secs, self.duration)
        
    def __str__(self):
        return str(self.prog_bar)
        


if __name__ == '__main__':
    main()
