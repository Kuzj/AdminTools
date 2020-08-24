from random import choice
from functools import wraps

def translit(text):
    text = text.lower()
    alpha_dict = {'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'e',
      'ж':'zh','з':'z','и':'i','й':'i','к':'k','л':'l','м':'m','н':'n',
      'о':'o','п':'p','р':'r','с':'s','т':'t','у':'u','ф':'f','х':'kh',
      'ц':'ts','ч':'ch','ш':'sh','щ':'shch','ъ':'','ы':'y','ь':'','э':'e',
      'ю':'yu','я':'ya'}
    for letter in (l for l in text if l in alpha_dict.keys()):
        text = text.replace(letter, alpha_dict[letter])
    return text
    
def password(size = 8,cfg_upper_letter=1,cfg_digit=1):
    vowels = 'aeiouy'
    consonants = 'bcdfghjklmnpqrstvwxz'
    digits = '0123456789'

    def v():
        return choice(vowels)
    
    def V():
        return choice(vowels).upper()
    
    def c():
        return choice(consonants)
    
    def C():
        return choice(consonants).upper()
        
    def d():
        return choice(digits)
    
    mapping = {'c':c,'C':C,'v':v,'V':V,'d':d}

    def letters_map():
        if cfg_upper_letter > 0:
            map = choice('cCvV')
        else:
            map = choice('cv')
        while len(map)< size:
            template = ''
            if map[-1] not in 'Cc': template += 'Cc'
            if len(map) > 1:
                if not(map[-1] in 'Vv' and map[-2] in 'Vv'):
                    template += 'Vv'
            else:
                template += 'Vv'
            if len([l for l in map if l in 'CV']) >= cfg_upper_letter:
                template = template.replace('C','').replace('V','')
            if len([l for l in map if l in 'd']) < cfg_digit:
                template += 'd'
            if len(map)+cfg_digit+cfg_upper_letter > size and cfg_digit > 0 and map.count('d')<cfg_digit:
                template = 'd'
            if len(map)+cfg_digit+cfg_upper_letter > size and cfg_upper_letter > 0 and len([l for l in map if l in 'CV'])<cfg_upper_letter:
                template = 'CV'
            map += choice(template)
        return map
    return ''.join([mapping[x]() for x in letters_map()])
    
def repeat(n):
    def wrap(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            for _ in range(n):
                f(*args, **kwargs)
        return wrapper
    return wrap