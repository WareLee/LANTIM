# 业务逻辑： 用户登陆验证
import pickle
import os
from model.entry.userhabit import *


def auto_login_status():
    """返回用户之前关于登陆的设置信息user_habit"""
    file = None
    user_habit = None
    p = os.path.split(os.path.realpath(__file__))[0]
    try:
        file = open(os.path.join(p,'user_habit.pickle'), 'rb')
        user_habit = pickle.load(file)
    except (FileNotFoundError, Exception):
        print('没有之前相关登陆信息,或文件打开失败')
    finally:
        if file:
            file.close()

    return user_habit


def login(username, password, record=False, remember=False, autologin=False):
    """验证用户密码:
    record: 是否记录本次登陆到本地文件（如果成功的话）
    当record==True时,应提供remember和autologin的值
    成功： 返回 user_info
    失败： 返回 None
    """
    p = os.path.split(os.path.realpath(__file__))[0]
    files = [f for f in os.listdir(p) if f.endswith('.pickle')]
    for f in files:
        if f.startswith(username):
            with open(os.path.join(p, f), 'rb') as ff:
                user_info = pickle.load(ff)
            if user_info.password == password:
                if record:
                    _recordhabit(remember, autologin, username, password)
                return user_info

    return None


def clearhabit(user_habit):
    """清理用户的本地登陆信息：只保留其账户名称,其余全放空"""
    user_habit.password = ''
    user_habit.autologin = False
    user_habit.remember = False
    user_habit.id = ''

    p = os.path.split(os.path.realpath(__file__))[0]
    with open(os.path.join(p, 'user_habit.pickle'), 'wb') as f:
        pickle.dump(user_habit, f)


def _recordhabit(remember, autologin, username, password):
    user_habit = UserHabit()
    user_habit.remember = remember
    user_habit.autologin = autologin
    user_habit.username = username
    user_habit.password = password

    p = os.path.split(os.path.realpath(__file__))[0]
    with open(os.path.join(p,'user_habit.pickle'), 'wb') as f:
        pickle.dump(user_habit, f)
