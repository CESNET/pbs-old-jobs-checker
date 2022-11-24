#!/usr/bin/env python3

from datetime import datetime, date
import time
import sys
import getopt

f = int(time.time()) - 13132800  # 5 months
t = int(time.time())

REMOVE, USER, MAIL, DATE, FROM, TO, STATE = range(7)
OPTIONS = {FROM:{str(f)}, TO: {str(t)}}

try:
    import pbs_ifl
except:
    sys.path.insert(1, "/opt/pbs/lib/python3-pbs_ifl")
    import pbs_ifl

c = pbs_ifl.pbs_connect("localhost")

#print(pbs_ifl.pbs_statjob(c, None, None, None))

""" OPTIONS
    -r --remove => withouth argument -> for removing everything
                => argument -> ID job

    -m --mail   => argument -> one or more e-mail adresses
                               separates with :: (double colon)

    -u --user   => argument -> one or more users separates with ::

    -f --from   => argument -> date 'YYYY-MM-DD'
                            -> number of months from now

    -t --to     => argument like -f

    -s --state  => argument -> job state (Q, R, F)
"""

def get_timestamp(date, count):
    #print(str(date - count * 2678400))
    return {str(int(date) - count * 2678400)}  # 2678400 31 days in seconds


def get_options(entry):
    # fce getopt()
    opts, args = getopt.getopt(entry, "hr:m:u:d:f:t:s:",
                               ['remove', 'mail',
                                'user', 'from', 'to', 'state'])
    for o, a in opts:
        if o in ('-r', '--remove'):
            OPTIONS[REMOVE] = set(a.split("::"))
        elif o in ('-m', '--mail'):
            OPTIONS[MAIL] = set(a.split("::"))
        elif o in ('-u', '--user'):
            OPTIONS[USER] = set(a.split("::"))
        elif o in ('-f', '--from'):
            if a.isdecimal():
                OPTIONS[FROM] = get_timestamp(time.time(), int(a))
            else:
                OPTIONS[FROM] = get_timestamp(int(a), 0)
        elif o in ('-t', '--to'):
            if a.isdecimal():
                OPTIONS[TO] = get_timestamp(time.time(), int(a))
            else:
                OPTIONS[TO] = get_timestamp(int(a), 0)
        elif o in ('-s', '--state'):
            OPTIONS[STATE] = set(a.split("::"))
        else:
            assert False


def add_to_filtered(job, filtered):
    owner = job["Job_Owner"]
    id_job = job["id"]
    time = int(job["ctime"])
    filtered.append((time, owner, id_job))


def get_suitable_job(job, filtered):
    suitable = True
    for opt, val in OPTIONS.items():
        if opt == REMOVE or opt == USER:
            if job["Job_Owner"] not in val:
                suitable = False
                break
        #elif opt = USER:

        elif opt == FROM:
            time = max(val)
            if int(job["ctime"]) <= int(time):
                suitable = False
                break
        elif opt == TO:
            time = max(val)
            if int(job["ctime"]) >= int(time):
                suitable = False
                break
        #elif opt == STATE:

    if suitable:
        add_to_filtered(job, filtered)


def delete():
    # delete job/s get in argumet
    pass


def send_mail():
    pass


pbs = pbs_ifl.pbs_statjob(c, None, None, None) # list of dictionaryies
#one = out[0]
#print(one["ctime"])
#print(datetime.fromtimestamp(int(one["ctime"])))

options = {}
get_options(sys.argv[1:]) # get options

# searching old jobs
filtered = []  # List of Tuples (UTC, job owner, job id)

for job in pbs:
    get_suitable_job(job, filtered)

"""for job in pbs:
    if date_t < int(job["ctime"]):
        continue
    old.append((job["id"], job["Job_Owner"]))"""
filtered.sort()
print(filtered)
print(len(filtered))
print(len(pbs))

pbs_ifl.pbs_disconnect(c)