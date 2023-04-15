import random, time
import requests
from server import app
from server.models import FlagStatus, SubmitResult


RESPONSES = {
    FlagStatus.QUEUED: ['timeout', 'game not started', 'try again later', 'game over', 'is not up',
                        'no such flag'],
    FlagStatus.ACCEPTED: ['accepted', 'congrat'],
    FlagStatus.REJECTED: ['bad', 'wrong', 'expired', 'unknown', 'your own',
                          'too old', 'not in database', 'already submitted', 'invalid flag'],
}

def submit_flags(flags, config):
    for item in flags:
        headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        }

        json_data = {
        'flag': item.flag,
        'token': 'da8b38f9e9102be5',
        }

        response = requests.post('http://95.217.236.0:8080/flag', headers=headers, json=json_data)

        unknown_responses = set()
        message = response.text
        response_lower = message.lower()

        for status, substrings in RESPONSES.items():
            if any(s in response_lower for s in substrings):
                app.logger.warning('s %s', response_lower)
                found_status = status
                break
        else:
            found_status = FlagStatus.QUEUED
            if message not in unknown_responses:
                unknown_responses.add(message)
                app.logger.warning('Unknown checksystem response (flag will be resent): %s', message)

        yield SubmitResult(item.flag, found_status, message)
        
