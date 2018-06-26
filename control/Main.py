#!usr/bin/env
# -*- encoding:utf -8-*-
# control层：检查用户是否设置了自动登陆
#       否：启动登陆窗口EnterWindow,验证用户信息成功后启动主界面窗口UserWindow
#       是：直接启动主界面窗口
from model import login
from view import frame

if __name__ == '__main__':
    """检查是否设置了自动登陆：
        是： 直接尝试登陆:
            成功：获取user_info并传递给主窗口UserWindow用于展示
            失败：清理本地信息,并将清理后的信息user_habit传递给登陆窗口EnterWindow
        否： 获取之前登陆时留下的信息user_haibit,传递给登陆窗口EnterWindow
    
    """
    user_habit = login.auto_login_status()
    if user_habit.autologin:
        user_info = login.login(user_habit.username, user_habit.password)
        if user_info:
            # TODO 基本完成,还需要细节
            frame.UserWindow(user_info)
        else:
            # TODO
            login.clearhabit(user_habit)
    frame.EnterWindow(user_habit)
