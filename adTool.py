import configparser
from time import sleep
from pathlib import Path

from .psbinding import PowerShellPipe
from .exchTool import Exchange
from .helpers import password, translit

config_defaults = {'domain':'contoso.com',
                   'ad_path':'OU=Users,DC=contoso,DC=com'}
adTool_config_path = 'adTool.ini'
config = configparser.ConfigParser(defaults = config_defaults)
if not Path(adTool_config_path).is_file():
    open(adTool_config_path,'w').close()
config.read(adTool_config_path)
try:
    cfg_password = config['DEFAULT']['password']
except KeyError:
    cfg_password = password()
    print(f"'password' value in section 'DEFAULT' from {adTool_config_path} not found. Using '{cfg_password}'.")
with open(adTool_config_path, 'w') as f:
    config.write(f)

class User():
    def __init__(self,company='',name='',sername='',fullname='',otchestvo = '',subunit='',post='',pswd='',tel=''):
        self.name = name
        self.sername = sername
        self.fullname = fullname
        self.otchestvo = otchestvo
        self.subunit = subunit
        self.post = post
        self.pswd = pswd
        self.tel = tel
        self.company = company
    
    @property    
    def check(self):
        return all([self.sername])#,self.name,self.account,self.password,self.fullname,self.otchestvo])
    
    @property
    def account(self):
        initials = translit(self.name[0])[0] if self.name else ''
        initials += translit(self.otchestvo[0])[0] if self.otchestvo else ''
        account = translit(self.sername)
        account += '.'+initials if initials else ''
        return account 
    
    @property
    def password(self):
        if self.pswd:
            return self.pswd
        else:
            return cfg_password
    
    @property
    def sAMAccountName(self):
        if len(self.sername + ' ' + self.name) > 20:
            return self.sername + ' ' + self.name[0].upper() + self.otchestvo[0].upper()
        else:
            return self.sername + ' ' + self.name if self.name else self.sername
    
    def __str__(self):
        return str(vars(self))
        
class AD():
    def __init__(self):
        self.ps = PowerShellPipe()
        self.__connect()

    def __connect(self):
        self.ps.send(f'''import-module ActiveDirectory''')
        return self.ps.read(10)
        
    def get_user(self,account):
        self.ps.send(f"Get-ADUser -F {{SamAccountName -eq '{account}'}}")
        return self.ps.read(10)
        
    def new_user(self,user):
        self.ps.send(f'''New-ADUser -sAMAccountName '{user.sAMAccountName}' -Name '{user.sername} {user.name} {user.otchestvo}' -GivenName '{user.name}' -Surname '{user.sername}' -DisplayName '{user.fullname}' -Description '{user.post}' -Title '{user.post}' -Company '{user.company}' -Department '{user.subunit}' -UserPrincipalName '{user.account}@{config['DEFAULT']['domain']}' -Enabled $True -OfficePhone '{user.tel}' -Path '{config['DEFAULT']['ad_path']}' -AccountPassword (ConvertTo-SecureString -AsPlainText {user.password} -force)''')
        return self.ps.read(10)