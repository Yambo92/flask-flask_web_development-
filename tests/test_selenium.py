#encoding=utf-8
from selenium import webdriver
from app import create_app, db
from ..app.models import User, Role, Post
import unittest, threading, re


class SeleniumTestCase(unittest.TestCase):
    client = None

    @classmethod
    def setUp(cls):
        # 啓動firefox
        try:
            cls.client = webdriver.Firefox()
        except:
            pass
        #如果無法啓動瀏覽器，跳過測試
        if cls.client:
            #創建程序
            cls.app = create_app('testing')
            cls.app_context = cls.app.app_context()
            cls.app_context.push()

        #禁止日志
        import logging
        logger = logging.getLogger('werkzeug')
        logger.setLevel('ERROR')

        #創建數據庫， 填充虛擬數據
        db.create_all()
        Role.insert_roles()
        User.generate_fake(10)
        Post.generate_fake(10)

        #添加管理員
        admin_role = Role.query.filter_by(permissions=0xff).first()
        admin = User(email='wangsir@example.com',
                     username='wangsir', password='wang',
                     role=admin_role, confirmed=True)
        db.session.add(admin)
        db.session.commit()

        #在一個縣城中啓動flask服務器
        threading.Thread(target=cls.app.run).start()

    def test_admin_home_page(self):
        #进入首页
        self.client.get('http://localhost:5000/')
        self.assertTrue(re.search('Hello,\s+Stranger!',
                                  self.client.page_source))

        #进入登录页面
        self.client.find_element_by_link_text('Log In').click()
        self.assertTrue('<h1>Login</h1>' in self.client.page_source)

        #登录
        self.client.find_element_by_name('email').\
            send_keys('wangsir@example.com')
        self.client.find_element_by_name('password').send_keys('wang')
        self.client.find_element_by_name('submit').click()
        self.assertTrue(re.search('Hello,\s+wangsir!', self.client.page_source))

        #进入用户个人资料页面
        self.client.find_element_by_link_text('Profile').click()
        self.assertTrue('<h1>wangsir</h1>' in self.client.page_source)





@classmethod
def tearDownClass(cls):
    if cls.client:
        #关闭flask服务器和浏览器
        cls.client.get('http://localhost:5000/shutdown')
        cls.client.close()

        #销毁数据库
        db.drop_all()
        db.session.remove()

        #删除程序上下文
        cls.app_context.pop()

def setUp(self):
    if not self.client:
        self.skipTest('web browser not available')

def tearDown(self):
    pass








































