import tkinter as tk
from tkinter import messagebox
import functools
from model import login
from model.entry import userinfo
from model import request


class EnterWindow(object):
    """用于登陆的单窗口
    关键字参数可以包含autologin,id,username,password,remember
    """

    def __init__(self, user_habit):
        # 窗口基本设置
        self.window = tk.Tk()
        self.window.title('登陆')
        self.window.geometry('500x300')

        self.username = tk.StringVar(self.window)
        if not user_habit.username:
            user_habit.username = '用户名'
        self.username.set(user_habit.username)
        self.password = tk.StringVar(self.window)
        if not user_habit.password:
            user_habit.password = '密码'
        self.password.set(user_habit.password)
        self.autologin = tk.IntVar(self.window, value=0)
        if user_habit.autologin:
            self.autologin.set(1)
        self.remember = tk.IntVar(self.window, value=0)
        if user_habit.remember:
            self.remember.set(1)

        # 顶层区域 Label
        img = tk.PhotoImage(file='../images/loginbg.png', width=500, height=120)
        tk.Label(self.window, image=img).pack()

        # 头像headimg
        himg = tk.PhotoImage(file='../images/logo.png', width=100, height=100)
        tk.Label(self.window, image=himg).place(x=50, y=150)

        # 帐号输入框Entry
        tk.Entry(self.window, textvariable=self.username, width=30).place(x=180, y=160)

        # 密码输入框Entry
        tk.Entry(self.window, textvariable=self.password, width=30, show='*').place(x=180, y=190)

        # checkbutton 记住密码
        tk.Checkbutton(self.window, text='记住密码', variable=self.remember, onvalue=1, offvalue=0).place(x=175, y=220)

        # checkbutton 自动登陆就意味着默认记住密码
        tk.Checkbutton(self.window, text='自动登陆', variable=self.autologin, onvalue=1, offvalue=0,
                       command=functools.partial(lambda remmber: self.remember.set(1), self.remember)).place(x=280,
                                                                                                             y=220)

        # Button 登陆按钮
        tk.Button(self.window, width=25, height=1, bg='#008CEE', text='登陆', command=self._login).place(x=185, y=250)

        tk.mainloop()

    def _produceWindow(self, known):
        """根据已知信息,生成完整登陆窗口"""
        pass

    def _login(self):
        if self.username.get().strip() and self.password.get().strip():
            user_info = login.login(self.username.get(), self.password.get(), record=True, remember=self.remember.get(),
                                    autologin=self.autologin.get())
            if user_info:
                print('登陆成功。')
                self.window.destroy()
                UserWindow(user_info)
            else:
                messagebox.showinfo(title='错误', message='用户名或密码错误')
        else:
            messagebox.showinfo(title='提示', message='请完整填写用户名和密码')


# TODO
class UserWindow():
    """用户的主界面"""

    def __init__(self, user_info):
        self.headimgs = []  # 好友头像列表
        self.headlebs = []  # 放头像的label
        self.friendsit = []  # 好友项列表

        # 窗口基本设置
        self.window = tk.Tk()
        self.window.title('LanTim')
        self.window.geometry('1000x700')

        # 主frame
        mainframe = tk.Frame(self.window).pack()
        self.mainframe = mainframe

        # 最左frame
        lframe = tk.Frame(self.mainframe, width=50, height=700, bg='#E5E9F4').place(x=0, y=0)
        self.lframe = lframe

        # 中间frame
        mframe = tk.Frame(self.mainframe, width=200, height=700, bg='#F5F8FF').place(x=50, y=0)
        self.mframe = mframe

        # 最右frame
        rframe = tk.Frame(self.mainframe, width=750, height=700, bg='#F7FAFF').place(x=252, y=0)
        self.rframe = rframe

        # 设置最左frame
        img = tk.PhotoImage(file='../images/head.png', width=40, height=40)
        tk.Label(self.lframe, image=img).place(x=5, y=10)

        messageimg = tk.PhotoImage(file='../images/mess.png', width=40, height=40)
        tk.Button(self.lframe, image=messageimg, bd=0,
                  command=functools.partial(self._showsessionli, user_info, self.headimgs, self.headlebs,
                                            self.friendsit)).place(x=5, y=70)

        friendsimg = tk.PhotoImage(file='../images/friends.png', width=40, height=40)
        tk.Button(self.lframe, image=friendsimg, bd=0,
                  command=functools.partial(self._showfriendsli, user_info, self.headimgs, self.headlebs,
                                            self.friendsit)).place(x=5,
                                                                   y=130)

        groupsimg = tk.PhotoImage(file='../images/groups.png', width=40, height=40)
        tk.Button(self.lframe, image=groupsimg, bd=0,
                  command=functools.partial(self._showfroupsli, user_info, self.headimgs, self.headlebs,
                                            self.friendsit)).place(x=5, y=190)

        # 设置mframe
        # ..TODO
        self._showfriendsli(user_info, self.headimgs, self.headlebs, self.friendsit)

        # 设置rframe
        self.talkingto = tk.StringVar(self.rframe)  # 当前正聊天的对象
        self.talkingto.set('  < 点击头像聊天')
        self.tite = tk.Label(self.rframe, textvariable=self.talkingto, width=106, height=2, bg='#F7FAFF', anchor='w')
        self.tite.place(x=252, y=0)

        self.chatbord = tk.Text(self.rframe, width=100, height=30, bg='#F7FAFF')
        self.chatbord.place(x=250, y=48)
        self.chatbord.config(state=tk.DISABLED)

        self.inputbord = tk.Text(self.rframe, width=100, height=10, bg='#F7FAFF')
        self.inputbord.place(x=250, y=540)

        tk.Button(self.rframe, text='发送', bd=0, command=self._sendmess).place(x=900, y=660)

        tk.mainloop()

    # TODO 请求服务器转发消息
    def _sendmess(self):
        data = self.inputbord.get(1.0, tk.END)
        data = '\n' + data + '\n'
        self.inputbord.delete(0.0, tk.END)
        self.chatbord.config(state=tk.NORMAL)
        self.chatbord.insert('end', data)
        self.chatbord.config(state=tk.DISABLED)

    # TODO  更新中间frame为会话列表
    def _showsessionli(self, user_info, headimgs, headlebs, friendsit):
        for i in range(len(headimgs)):
            headimgs.pop()
        for it in headlebs:
            it.destroy()
        for it in friendsit:
            it.destroy()

    # TODO  更新中间frame为好友列表
    def _showfriendsli(self, user_info, headimgs, headlebs, friendsit):
        if not user_info.friends:
            return

        yy = 40
        for it in user_info.friends:
            h = tk.PhotoImage(file='../images/head2.png', width=50, height=50)
            headimgs.append(h)

            btn = tk.Button(self.mframe, bitmap="info", text=it, width=171, height=50, bd=0, image=h, bg='#F2F6F9',
                            anchor='nw',
                            compound=tk.LEFT, command=functools.partial(self._talkto, it))
            friendsit.append(btn)
            btn.place(x=50, y=yy)

            yy += 50

    # TODO  更新中间frame为群列表
    def _showfroupsli(self, user_info, headimgs, headlebs, friendsit):
        for i in range(len(headimgs)):
            headimgs.pop()
        for it in headlebs:
            it.destroy()
        for it in friendsit:
            it.destroy()

        if not user_info.groups:
            return

        yy = 40
        for name in user_info.groups:
            h = tk.PhotoImage(file='../images/groups.png', width=50, height=50)
            headimgs.append(h)

            btn = tk.Button(self.mframe, bitmap="info", text=name, width=171, height=50, bd=0, image=h, anchor='nw',
                            bg='#F2F6F9',
                            compound=tk.LEFT, command=functools.partial(self._talkto, name))
            friendsit.append(btn)
            btn.place(x=50, y=yy)

            yy += 50

    # TODO
    def _talkto(self, name):
        self.talkingto.set("  < " + name)
        self.chatbord.config(state=tk.NORMAL)
        self.chatbord.delete(0.0, tk.END)
        self.chatbord.config(state=tk.DISABLED)


if __name__ == '__main__':
    # EnterWindow(autologin=False, id='')

    user_list = userinfo.UserInfo('ididi', 'lee', '5588', ['zhang', 'fei'], {'all': ['lee', 'fei']})
    UserWindow(user_list)

    # root = tk.Tk()
    # root.geometry('300x200')
    # img = tk.PhotoImage(file='../images/loginbg.png',width=300,height=100)
    # tk.Label(root,text='ddd', image=img).pack()
    # tk.mainloop()
