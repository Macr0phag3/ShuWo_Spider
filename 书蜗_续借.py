# -*- coding:gbk -*- 
import requests
import pprint
import time,os
import yagmail

class Sw():
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.host = 'http://t1.beijingzhangtu.com'


    def Login(self):
        loginPayload = {
            'phone': self.username,
            'pass': self.password
            }

        login_json = requests.post(self.host+'/api/user/loginByPhone.html', data=loginPayload).json()   #登录
        
        assert int(login_json['code']), login_json['msg']
        print login_json['msg']
        
        self.userId = login_json['data']['id']
        self.libraryId = login_json['data']['libraries'][0]['id']
        self.token = login_json['data']['token']
        
    def getStuInfo(self):
        page = '1' 
        ListPayload = {
            'page': page,
            'userId': self.userId,
            'libraryId': self.libraryId,
            'token': self.token
            }
        List_json = requests.post(self.host+'/api/userLibrary/getList.html', data=ListPayload).json()  #学生信息
        studentName = List_json['data'][0]['cardusername']
        print studentName, '你好'

    def getBorrowList(self):
        self.books = {}
        page = '1' 
        BorrowPayload = {
            'userId': self.userId,
            'libraryId': self.libraryId,
            'token': self.token,
            'page': page
            }
        Borrow_json = requests.post(self.host+'/api/borrow/getList.html', data=BorrowPayload).json()  #在借图书
        for book in Borrow_json['data']:
            print '-' * 20
            print '书名:', book['name']
            print '借书日期', book['loan_DATE']
            print '距离还书还有', book['surplus_DAYS'], '天'
            
            self.books[book['name']] = [book['bar_NUMBER'], book['surplus_DAYS']]
            
        #pprint.pprint(self.books)

    def RenewSome(self, BookList):
        self.getBorrowList()
        
        for book in BookList:
            RenewSomePayload = {
                'bookName': book,
                'barNumber': self.books[book][0],
                'libraryId': self.libraryId,
                'userId': self.userId,
                'token': self.token,
                }
            RenewSome_json = requests.post(self.host+'/api/borrow/continue.html', data=RenewSomePayload).json()  #续借
            #print '-' * 20
            #print '书名:', book
            #print '续借结果:', RenewSome_json['msg']
            

    def RenewAll(self):
        self.getBorrowList()
        content = ''
        for book in self.books:
            if self.books[book][1] == '0':
                RenewAllPayload = {
                    'bookName': book,
                    'barNumber': self.books[book][0],
                    'libraryId': self.libraryId,
                    'userId': self.userId,
                    'token': self.token,
                    }
                RenewAll_json = requests.post(self.host+'/api/borrow/continue.html', data=RenewAllPayload).json()  #续借
                #print '-' * 20
                #print '书名:', book
                #print '续借结果:', RenewAll_json['msg']

                content += '-' * 20 + '\n书名: ' + book + '\n续借结果: ' + RenewAll_json['msg'] + '\n'
                
            else:
                content += '-' * 20 + '\n书名: ' + book + '\n续借结果: ' + '距离自动续借还有' + self.books[book][1] + '天' + '\n'
                
        return '你一共借了 ' + str(len(self.books)) + '本书\n' + content
            
    def autoRenewAll(self):
        while 1:
            sw.Login() #防止token失效
            content = self.RenewAll()
            print '-' * 20
            print content
            self.Email(content.encode('utf8'))
            time.sleep(86400) #一天
            os.system('cls')
        
    def Email(self, content):
        yag = yagmail.SMTP(user = '发送方邮箱', password = '发送方邮箱密码', host = '邮箱host', port = '25') #如139邮箱host是smtp.139.com
        yag.send(to = "接收方邮箱", subject = "Troy's Sw_Spider", contents = content) 
        print 'Email successfully!'


username = '***********'    #账号
password = '*********'      #密码
#BookList = ['应用MATLAB实现神经网络', 'PHP、MySQL与JavaScript学习手册']

#BookList = [book.decode('gbk') for book in BookList] #记得进行编码
sw = Sw(username, password)
sw.Login()                 #登录
#sw.getStuInfo()            #获取学生信息
#sw.getBorrowList()         
#sw.RenewSome(BookList)
#sw.RenewAll()
#sw.autoRenewAll()