import configparser
from pathlib import Path

from .psbinding import PowerShellPipe

config_defaults = {'domain':'contoso.com',
                   'host':'mail'}
exchTool_config_path = 'exchTool.ini'
config = configparser.ConfigParser(defaults = config_defaults)
if not Path(exchTool_config_path).is_file():
    open(exchTool_config_path,'w').close()
config.read(exchTool_config_path)
cfg_host = ''.join([config['DEFAULT']['host'],'.',config['DEFAULT']['domain']])
with open(exchTool_config_path, 'w') as f:
    config.write(f)

'''
config = configparser.ConfigParser()
exchTool_config_path = 'exchTool.ini'
if Path(exchTool_config_path).is_file():
    config.read(exchTool_config_path)
    try:
        cfg_host = config['DEFAULT']['host']
    except KeyError:
        cfg_host = 'localhost'
        print(f"'host' value in section 'DEFAULT' from {exchTool_config_path} not found. Using '{cfg_host}'.")
else:
    cfg_host = 'localhost'
    print(f"{exchTool_config_path} not found. Using '{cfg_host}' for 'host' value.")
'''

class Exchange():
    def __init__(self,host=cfg_host):
        self.ps = PowerShellPipe()
        self.__host = host
        self.__connect()
        
    def __connect(self):
        self.ps.send(f'''$Session = New-PSSession -ConfigurationName Microsoft.Exchange -ConnectionUri http://{self.__host}/PowerShell/ -Authentication Kerberos; Import-PSSession $Session -DisableNameChecking;''')
        self.ps.read(20)

    def mdb_query(self):
        self.ps.send('''Get-MailboxDatabase -Status | select name,availablenewmailboxspace | ft -hidetableheaders''')
        mdb_raw_data = self.ps.read(10)
        #print(f'debug<<<raw mdb: {mdb_raw_data}>>>')
        return {base[0]:float(base[1]) for base in [line.split() for line in mdb_raw_data.decode().split('\r\n') if line]}
        
    def mdb_min_space(self):
        mdb_dict = self.mdb_query()
        return min(mdb_dict,key = mdb_dict.get)

    def mdb_max_space(self):
        mdb_dict = self.mdb_query()
        return max(mdb_dict,key = mdb_dict.get)
        
    def enable_mailbox(self,identity):
        self.ps.send(f'''Enable-Mailbox -Identity {identity}@{config['DEFAULT']['domain']} -Alias {identity} -Database {self.mdb_max_space()} | Select DistinguishedName, EmailAddresses, homeMDB''')
        return self.ps.read(10)