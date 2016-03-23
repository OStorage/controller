from abstract_metric import Metric
from metrics_parser import SwiftMetricsParse
import json
import redis
import requests

class BwGetInfo(Metric):
    _sync = {}
    _async = ['get_value', 'attach', 'detach', 'notify', 'start_consuming','stop_consuming', 'init_consum', \
            'stop_actor', 'parse_osinfo']
    _ref = ['attach', 'detach']
    _parallel = []

    def __init__(self, exchange, metric_id, routing_key, host):
        Metric.__init__(self)

        self.host = host
        self.queue = metric_id
        self.routing_key = routing_key
        self.name = metric_id
        self.exchange = exchange
        print 'Get_bw_info initialized'
        self.count = {}
        self.last_bw = {}

    def attach(self, observer, bw_obs):
        """
        Asyncronous method. This method allows to be called remotelly. It is called from
        observers in order to subscribe in this workload metric. This observer will be
        saved in a dictionary type structure where the key will be the tenant assigned in the observer,
        and the value will be the PyActive proxy to connect to the observer.

        :param observer: The PyActive proxy of the oberver rule that calls this method.
        :type observer: **any** PyActive Proxy type
        """
        if bw_obs:
            self.bw_observer = observer
        else:
            tenant, policy = observer.get_topic_subsribe()
            if not tenant in self._observers.keys():
                self._observers[tenant] = {}
                if not policy in self._observers[tenant].keys():
                    self._observers[tenant][policy] = set()
            if not observer in self._observers[tenant][policy]:
                self._observers[tenant][policy].add(observer)

    def notify(self, body):
        try:
            self.parse_osinfo(json.loads(body))
            self.bw_observer.update(self.name, self.count)
        except:
            print "Not bw_observer"

        for tenant in self._observers.keys():
            if tenant in self.count.keys():
                for policy, observers in self._observers[tenant].items():
                    if policy in self.count[tenant].keys()
                        for oberver in observers:
                            observer.update(self.name, self.count[tenant][policy]["bw"])


    def parse_osinfo(self, osinfo):
        for ip in osinfo:
            for account in self.count:
                self.count[account][ip] = {}
            for dev in osinfo[ip]:
                for account in osinfo[ip][dev]:
                    for policy in osinfo[ip][dev][account]:
                    if not account in self.count:
                        self.count[account] = {}
                    if not ip in self.count[account]:
                        self.count[account][ip] = {}
                    if not policy in self.count[account][ip]:
                            self.count[account][ip][policy] = osinfo[ip][dev][account][policy]
                        

    def get_value(self):
        return self.value
