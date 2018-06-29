#!usr/bin/env
# -*- encoding:utf -8-*-
# control层：检查用户是否设置了自动登陆
#       否：启动登陆窗口EnterWindow,验证用户信息成功后启动主界面窗口UserWindow
#       是：直接启动主界面窗口
from model import login
from view import frame
from model.entry import userhabit
import pickle
from model.entry.userinfo import UserInfo


def sample_userinfo(userinfo):
    if not userinfo:
        userinfo = UserInfo()
        userinfo.id = 'abc'
        userinfo.username = 'lee'
        userinfo.password = '55558888'
        userinfo.friends = ['abc', 'def', 'ghi']
        userinfo.groups = {'group-a': ['abc', 'def', 'ghi']}

    with open('../model/{}:{}.pickle'.format(userinfo.username, userinfo.id), 'wb') as f:
        pickle.dump(userinfo, f)


if __name__ == '__main__':
    """检查是否设置了自动登陆：
        是： 直接尝试登陆:
            成功：获取user_info并传递给主窗口UserWindow用于展示
            失败：清理本地信息,并将清理后的信息user_habit传递给登陆窗口EnterWindow
        否： 获取之前登陆时留下的信息user_haibit,传递给登陆窗口EnterWindow
    
    """
    sample_userinfo(None)   # 手动添加用户数据信息

    user_habit = login.auto_login_status()

    if user_habit:
        if user_habit.autologin:
            user_info = login.login(user_habit.username, user_habit.password)
            if user_info:
                frame.UserWindow(user_info)
            else:
                login.clearhabit(user_habit)
        else:
            frame.EnterWindow(user_habit)
    else:
        frame.EnterWindow(userhabit.UserHabit())
