#!/usr/bin/env python
#  Copyright (c) 2010 Corey Goldberg (corey@goldb.org)
#  License: GNU GPLv3
#  
#  This file is part of MultiMechanize:
#       Multi-Process, Multi-Threaded, Web Load Generator, with python-mechanize agents
#
#  requires Python 2.6+



from test_scripts import wikipedia_search




import multiprocessing
import os
import Queue
import sys
import threading
import time



PROCESSES = 2
PROCESS_THREADS = 2
RUN_TIME = 10  # secs
RAMPUP = 0  # secs



def main():
    q = multiprocessing.Queue()
    rw = ResultWriter(q)
    rw.setDaemon(True)
    rw.start()
    
    start_time = time.time() 
    
    managers = [] 
    for i in range(PROCESSES):
        manager = MultiMechanize(q, start_time, i, PROCESS_THREADS, RUN_TIME, RAMPUP)
        managers.append(manager)
    for manager in managers:
        manager.start()
    
    

class MultiMechanize(multiprocessing.Process):
    def __init__(self, queue, start_time, process_num, num_threads=1, run_time=10, rampup=0):
        multiprocessing.Process.__init__(self)
        self.q = queue
        self.start_time = start_time
        self.process_num = process_num
        self.num_threads = num_threads
        self.run_time = run_time
        self.rampup = rampup
        
    def run(self):
        self.running = True
        thread_refs = []
        for i in range(self.num_threads):
            spacing = float(self.rampup) / float(self.num_threads)
            if i > 0:
                time.sleep(spacing)
            agent_thread = MechanizeAgent(self.q, self.start_time, self.run_time)
            agent_thread.daemon = True
            thread_refs.append(agent_thread)
            #print 'starting process %i, thread %i' % (self.process_num + 1, i + 1)
            agent_thread.start()            
        for agent_thread in thread_refs:
            agent_thread.join()
        


class MechanizeAgent(threading.Thread):
    def __init__(self, queue, start_time, run_time):
        threading.Thread.__init__(self)
        self.q = queue
        self.start_time = start_time
        self.run_time = run_time
        
        # choose timer to use
        if sys.platform.startswith('win'):
            self.default_timer = time.clock
        else:
            self.default_timer = time.time
            
    def run(self):
        elapsed = 0
        while elapsed < self.run_time:
            start = self.default_timer()               
            

            try:
                foo = 'wikipedia_search'
                bytes_received, customer_timers, errors = eval(foo + '.MechTransaction().run()')
                status = 'PASS'
            except AssertionError:
                status = 'FAIL'
                

            
            finish = self.default_timer()
            scriptrun_time = finish - start
            elapsed = time.time() - self.start_time 
            self.q.put((elapsed, scriptrun_time, status, bytes_received))
            


class ResultWriter(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
    
    def run(self):
        with open('results.csv', 'w') as f:     
            while True:
                try:
                    elapsed, scriptrun_time, status, bytes_received = self.queue.get(False)
                    f.write('%.3f,%.3f,%s,%i\n' % (elapsed, scriptrun_time, status, bytes_received))
                    f.flush()
                    #print '%.3f' % latency
                except Queue.Empty:
                    time.sleep(.1)


        
        
if __name__ == '__main__':
    main()
