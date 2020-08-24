# runas admin C:\Windows\SysWOW64\WindowsPowerShell\v1.0\powershell.exe (C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe)
# Set-executionpolicy remotesigned
# Get-ExecutionPolicy

import subprocess
import threading
import re
from collections import deque
from time import sleep, monotonic
from .helpers import repeat

cmdPrompt = re.compile('^PS [A-Z]\:.+>')
cmdPromptEmpty = re.compile('^PS [A-Z]\:.+> \r\n')
class Error(Exception):
    """Base class for other exceptions"""
    pass

class ReadStdoutTimeout(Error):
    """Raised when the read of stdout timeout"""
    def __init__(self, message="Read of stdout timeout"):
        self.message = message
        super().__init__(self.message)

class PowerShellPipe():
    def __init__(self):
        self.__p = subprocess.Popen(["powershell.exe"],stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,shell=True)
        self.__waiting = True
        self.__out = deque()
        self.__read_thread = threading.Thread(target = self.__read_stdout)
        self.__read_thread.daemon = True
        self.__read_thread.start()
        self.__p.stdin.write(b''.join([b'\r\n']))
        self.__p.stdin.flush()
        self.read(10)

    def __read_stdout(self):
        while self.__waiting:
            self.__out.append(self.__p.stdout.readline())

    def send(self, cmd, clearBefore = True):
        #print(f'debug<<<send:{cmd}>>>')
        if clearBefore:
            self.__out.clear()
        self.__p.stdin.write(b''.join([cmd.encode('cp866'),b'\r\n']))
        self.__p.stdin.flush()
        self.send_enter()
 
    @repeat(2)
    def send_enter(self):
        self.__p.stdin.write(b''.join([b'\r\n']))
        self.__p.stdin.flush()
    
    def wait(self):
        while not self.__out:
            sleep(0.1)
    
    def clear(self):
        self.__out.clear()
    
    def read(self,timeout=1):
        wait = True
        now = monotonic()
        while wait:
            #print(f'debug<<<{self.__out}>>>')
            if len(self.__out) and cmdPromptEmpty.search(self.__out[-1].decode('cp866')):
                out=b''
                for line in self.__out:
                    line_decoded = line.decode('cp866')
                    if cmdPrompt.search(line_decoded):
                        print(f'{line_decoded}')
                    else:
                        out = out.join([b'',line])
                self.__out.clear()
                r = out.decode('cp866')
                #print(f'debug<<<out:{r}/out>>>')
                return out
            elif monotonic() - now > timeout:
                wait = False
            else:
                sleep(0.1)
        raise ReadStdoutTimeout                

    def close(self):
        self.__waiting = False
        self.__p.terminate()