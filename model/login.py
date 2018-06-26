# 业务逻辑： 用户登陆验证
import pickle
import os
from model.entry.userhabit import *


def auto_login_status():
    """返回用户之前关于登陆的设置信息user_habit"""
    try:
        file = open('user_habit.pickle', 'rb')
        user_habit = pickle.loads(file)
    except FileNotFoundError:
        print('没有之前相关登陆信息。')
    finally:
        file.close()

    return user_habit


def login(username, password):
    """验证用户密码:
    成功： 返回 user_info
    失败： 返回 None
    """
    files = [f for f in os.listdir('.') if f.endswith('.pickle')]
    for f in files:
        if f.startswith(username):
            with open(f, 'rb') as ff:
                user_info = pickle.loads(ff)
            if user_info.password == password:
                return user_info

    return None




def lookupuser_info(username, userid):
    """根据用户id,到数据库中查询用户信息
    user_info(str:id,str:username,str:password,list:friends,dict:groups)
    ==> user_info
    """
    try:
        file = open('{}:{}.pickle'.format(username, userid), 'rb')
        user_info = pickle.loads(file)
    except FileNotFoundError:
        print('The user #{} is not exists.'.format(userid))
    finally:
        file.close()

    return user_info





def _recordhabit(remember, autologin, username, password):
    user_habit = UserHabit()
    user_habit.remember = remember
    user_habit.autologin = autologin
    user_habit.username = username
    user_habit.password = password
    with open('user_habit.pickle','wb') as f:
        pickle.dump(user_habit,f)
