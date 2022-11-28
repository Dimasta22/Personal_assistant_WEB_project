import re
from datetime import datetime

def contact_validation(first_name=None, last_name=None,birthday=None, email=None, address=None, phone=None):
    result = 'Warning: '
    flag = False
    if first_name != None:
        if first_name == '':
            flag = True
            result +='first name should be necessarily, '
    # if last_name != None:
    #     if last_name == '':
    #         flag = True
    #         result +='last name should be necessarily, '
    if birthday != None and birthday != '':
        if re.search('\d{2}.\d{2}.\d{4}', birthday) == None:
            if len(birthday) != 10:
                flag = True
                result +='you should write birthday: dd.mm.yyyy, '
        try:
            datetime.strptime(birthday, "%d.%m.%Y")
        except:
            flag = True
            result +=f'you wrote wrong date: {birthday}, '
    if email != None and email != '':
        if re.search('[a-zA-Z][a-zA-Z0-9_.]{1,}@\w+[.][a-z]{2,}', email) == None:
            flag = True
            result +='your email has incorrect form, '
    if phone != None and phone != '':
        phone = phone.replace(' ', '')
        if re.search('\+\d{12}', phone) != None:
            if len(phone) != 13:
                flag = True
                result +='your phone has incorrect form, '
        elif re.search('\d{12}', phone) != None:
            if len(phone) != 12:
                flag = True
                result +='your phone has incorrect form, '
        elif re.search('\d{12}', phone) != None:
            if len(phone) != 12:
                flag = True
                result +='your phone has incorrect form, '
        elif re.search('\d{10}', phone) != None:
            if len(phone) != 10:
                flag = True
                result +='your phone has incorrect form, '
        else:
            flag = True
            result +='your phone has incorrect form, '
    if flag == True:
        return result[:-1]