import re
import pandas as pd


def preprocess(data):
    flag = False
    pattern = "\d{2}/\d{2}/\d{2,4},\s\d{1,2}:\d{2}\s[ap]m\s-\s"
    messages = re.split(pattern, data)[1:]
    if len(messages) is 0:
        pattern = "\d{2}/\d{2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s"
        messages = re.split(pattern, data)[1:]
        flag = True
    dates = re.findall(pattern, data)
    for i in range(len(dates)):
        dates[i] = dates[i].replace("\u202f", " ")
    if not flag:
        for i in range(len(dates)):
            x = dates[i].split()
            if len(x[0]) > 9:
                x[0] = x[0][0:6] + x[0][8:]
            hour, minute = x[1].strip().split(':')
            if x[2] == 'pm' and int(hour) != 12:
                hour = str(int(hour) + 12)
            elif x[2] == 'am':
                if int(hour) == 12:
                    hour = '00'
                elif int(hour) < 10:
                    hour = '0' + hour

            x[1] = ':'.join([hour, minute])
            x.pop(2)
            dates[i] = ' '.join(x)
    if flag:
        li=[]
        for i in dates:
            li.append(i[:-1])
        dates = li

    df = pd.DataFrame({'user_message': messages, 'message_date': dates})
    df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%y, %H:%M -')
    df.rename(columns={'message_date': 'date'}, inplace=True)
    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split(':\s', message)
        if len(entry) > 1:
            users.append(entry[0])
            messages.append(': '.join(entry[1:]))
        else:
            users.append('group_notifications')
            messages.append(entry[0])

    df['user'] = users
    df['messages'] = messages
    df.drop(columns=['user_message'], inplace=True)
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month_name()
    df['month_num'] = df['date'].dt.month
    df['modified_date'] = df['date'].dt.date
    df['day_name'] = df['date'].dt.day_name()
    df['day'] = df['date'].dt.day
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df['period'] = period

    return df
