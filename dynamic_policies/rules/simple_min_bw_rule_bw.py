from pyactive.controller import init_host, serve_forever, start_controller, interval, sleep
from pyactive.exception import TimeoutError, PyactiveError
import requests
import operator
import json
import redis
import pika
import logging
import syslog
import ConfigParser

class SimpleMinBandwidthPerTenant(AbstractEnforcementAlgorithm):

    def compute_algorithm(self, info):
        """
        return exception unnimplemented method
        """
        assign = dict()
        bw_a = dict()
        bw = self.get_redis_bw()


        for account in info:
            assign[account] = dict()
            bw_a[account] = dict()
            for ip in info[account]:
                for policy in info[account][ip]:
		    for device in info[account][ip][policy]:
                    	if not policy in assign[account]:
                            assign[account][policy] = dict()
			if not device in assign[account][policy]:
			    assign[account][policy][device] = dict()
                    	if not 'requests' in assign[account][policy][device]:
                            assign[account][policy][device]['requests'] = 1
                    	else:
                            assign[account][policy][device]['requests'] += 1
                    	if not 'ips' in assign[account][policy][device]:
                            assign[account][policy][device]['ips'] = set()
                        assign[account][policy][device]['ips'].add(ip)
	    
            for policy in assign[account]:
		for device in assign[account][policy]:
                    for ip in assign[account][policy][device]['ips']:
                        try:
                            bw_a[account][ip+"-"+policy+"-"+device] = int(bw[account][policy])/assign[account][policy][device]['requests']
                        except Exception as e:
			    print "ERROR: "+str(e)
                            #ibw_a[account][ip+"-"+policy+"-"+device] = -1

        return bw_a


