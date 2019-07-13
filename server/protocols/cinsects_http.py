import requests
import json

from server import app
from server.models import FlagStatus, SubmitResult



RESPONSES = {
    FlagStatus.QUEUED: ['error'],
    FlagStatus.ACCEPTED: ['ok'],
    FlagStatus.REJECTED: ['old','invalid','own'],
}

TIMEOUT = 5



def submit_flags(flags, config):
    flags_list = []
    for item in flags:
        flags_list.append(item.flag)

    flags_dict = {'flags':flags_list}

    headers = {'Content-Type': 'application/json',
            'Authorization':'Basic T21hdmlhdDpyQzNrYk5iRFYzUTg='
           }

    r = requests.post('https://scoreboard.ctf.cinsects.de/ctf/submit_flag/',headers=headers,json=flags_dict)

    unknown_responses = set()
    json_answer = json.loads(r.text)

    for item in json_answer:
        for in_item in json_answer[item]:
            response = item
            for status, substrings in RESPONSES.items():
                if any(s in response for s in substrings):
                    found_status = status
                    break
            else:
                found_status = FlagStatus.QUEUED
                if response not in unknown_responses:
                    unknown_responses.add(response)
                    app.logger.warning('Unknown checksystem response (flag will be resent): %s', response)
            yield SubmitResult(in_item, found_status, response)
