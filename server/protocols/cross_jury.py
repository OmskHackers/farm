import subprocess, random, time

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
        # специально для волга кызыф 
        # time.sleep(random.randint(0,3))

        # тут надо поменять curl

             #'''curl http://10.0.0.2/api/flag/v1/submit -H "Content-Type: text/plain" -d "{}"'''.format(item.flag) волга цтф

        cmd = '''curl -s -H 'X-Team-Token: <your_secret_token>' -X PUT --data ["{}"] https://REDACTED/flags'''.format(item.flag)

        output = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,shell=True, universal_newlines=True)
        message = output.stdout.read()
        output.terminate()
        
        unknown_responses = set()
        response_lower = message.lower()
        for status, substrings in RESPONSES.items():
            if any(s in response_lower for s in substrings):
                found_status = status
                break
        else:
            found_status = FlagStatus.QUEUED
            if message not in unknown_responses:
                unknown_responses.add(message)
                app.logger.warning('Unknown checksystem response (flag will be resent): %s', message)

        yield SubmitResult(item['flag'], found_status, message)

        
