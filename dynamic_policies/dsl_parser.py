from pyparsing import *
import redis
import json
from django.conf import settings

# By default, PyParsing treats \n as whitespace and ignores it
# In our grammer, \n is significant, so tell PyParsing not to ignore it
# ParserElement.setDefaultWhitespaceChars(" \t")
"""
rule ::= "FOR Tenant WHEN"+property +"[< > = <= >=]+X+"DO"+action

condition ::= property +"[< > = <= >=]+X
condition_list ::= condition
                    | condition_list AND condition
                    | condition_list OR condition
FOR Tenant WHEN"+ condition_list +"DO"+action

FOR Tenant WHEN"+ condition AND condition AND condition OR condition etc.+"DO"+action

TODO: Parse = TRUE or = False or condicion number. Check to convert to float or convert to boolean.
"""
#TODO: take this value from configuration
r = redis.StrictRedis(host="localhost", port=6379, db=0)

def get_redis_connection():
    return redis.Redis(connection_pool=settings.REDIS_CON_POOL)

def parse_group_tenants(tokens):
    data = r.lrange(tokens[0], 0, -1)
    return data


def parse(input_string):
    #TODO Raise an exception if not metrics or not action registred
    #TODO Raise an exception if group of tenants don't exists.
    #TODO Add transcient option

    #Support words to construct the grammar.
    word = Word(alphas)
    when = Suppress(Literal("WHEN"))
    literal_for = Suppress(Literal("FOR"))
    boolean_condition = oneOf("AND OR")

    #Condition part
    param = Word(alphanums+"_")+ Suppress(Literal("=")) + Word(alphanums+"_")
    metrics_workload = r.keys("metric:*")
    services = map(lambda x: "".join(x.split(":")[1]), metrics_workload)
    services_options = oneOf(services)
    operand =  oneOf("< > == != <= >=")
    number = Regex(r"[+-]?\d+(:?\.\d*)?(:?[eE][+-]?\d+)?")
    condition = Group(services_options + operand("operand") + number("limit_value"))
    condition_list = operatorPrecedence(condition,[
                                ("AND", 2, opAssoc.LEFT, ),
                                ("OR", 2, opAssoc.LEFT, ),
                                ])

    #For tenant or group of tenants
    group_id = Word(nums)
    container = Combine(Literal("CONTAINER:") + Word(alphanums) + Literal("/") + Word(alphanums+"_-"))
    obj = Combine(Literal("OBJECT:") + Word(alphanums)+Literal("/")+ Word(alphanums+"_-")+Literal("/")+ Word(alphanums+"_-."))
    tenant = Combine(Literal("TENANT:") + Word(alphanums))
    tenant_group = Combine(Literal("G:") + group_id)

    tenant_group_list = tenant_group + ZeroOrMore(Suppress("AND")+tenant_group)
    tenant_list = tenant + ZeroOrMore(Suppress("AND")+tenant)
    container_list = container + ZeroOrMore(Suppress("AND")+container)
    obj_list = obj + ZeroOrMore(Suppress("AND")+obj)
    target = Group(tenant_list ^ tenant_group_list ^ container_list ^ obj_list)

    #Action part
    action = oneOf("SET DELETE")
    sfilters_list = r.keys("filter:*")
    sfilter = map(lambda x: "".join(x.split(":")[1]), sfilters_list)

    with_params = Suppress(Literal("WITH"))
    do = Suppress(Literal("DO"))
    params_list = delimitedList(param)
    server_execution = oneOf("PROXY OBJECT")
    action = Group(action("action") + oneOf(sfilter)("filter") + Optional(with_params + params_list("params") + \
            Optional(Suppress("ON")+server_execution)))

    action_list = Group(delimitedList(action))

    #Object types
    operand_object =  oneOf("< > == = != <= >=")
    object_parameter = oneOf("OBJECT_TYPE OBJECT_SIZE")
    object_list = Group(object_parameter("object_parameter") + operand_object("operand") + Word(alphanums)("object_value"))
    to = Suppress("TO")

    #Functions post-parsed
    convertToDict = lambda tokens : dict(zip(*[iter(tokens)]*2))
    remove_repeted_elements = lambda tokens : [list(set(tokens[0]))]

    params_list.setParseAction(convertToDict)
    target.setParseAction(remove_repeted_elements)
    tenant_group.setParseAction(parse_group_tenants)


    #Final rule structure
    rule_parse = literal_for + target("target") + Optional(when +\
                condition_list("condition_list")) + do + action_list("action_list") + Optional(to + object_list("object_list"))

    #Parse the rule
    parsed_rule = rule_parse.parseString(input_string)

    #Pos-parsed validation
    has_condition_list = True
    if not parsed_rule.condition_list:
        has_condition_list = False

    if parsed_rule.action_list.params:
        filter_info = r.hgetall("filter:"+str(parsed_rule.action_list.filter))
        if "valid_parameters" in filter_info.keys():
            params = eval(filter_info["valid_parameters"])
            result = set(parsed_rule.action_list.params.keys()).intersection(params.keys())
            if len(result) == len(parsed_rule.action_list.params.keys()):
                #TODO Check params types.
                return has_condition_list, parsed_rule
            else:
                raise Exception
        else:
            raise Exception

    return has_condition_list, parsed_rule


# rules ="""FOR OBJECT:4f0279da74ef4584a29dc72c835fe2c9/pepito/pep.jpg DO SET compression WITH bw=2 ON OBJECT, SET uonetrace WITH bw=2 ON PROXY TO OBJECT_TYPE>2 """.splitlines()
# rules = """\
#     FOR 4f0279da74ef4584a29dc72c835fe2c9 WHEN througput < 3 OR slowdown == 1 AND througput == 5 OR througput == 6 DO SET compression WITH param1=2
#     FOR G:1 WHEN slowdown > 3 OR slowdown > 3 AND slowdown == 5 OR slowdown <= 6 DO SET compression WITH param1=2, param2=3
#     FOR G:4 AND G:4 WHEN slowdown > 3 AND slowdown > 50 DO SET compression WITH""".splitlines()
#
# for rule in rules:
#     _, parsed_rule = parse(rule)
#     print parsed_rule
#     print parsed_rule.action_list[0].params
#     print 'as_list', stats.asList()
#     print stats
#     print 'subject', stats.subject
#     print "group", stats.subject.tenant_group_list
#     try:
#         stats = parse(rule)
#     except:
#         print 'This rule ***'+rule+'  *** could not be parsed'
#     else:
#         print stats.asList()
