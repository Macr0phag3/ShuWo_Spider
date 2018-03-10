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

        login_json = requests.post(self.host+'/api/user/loginByPhone.html', data=loginPayload).json()   #��¼
        
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
        List_json = requests.post(self.host+'/api/userLibrary/getList.html', data=ListPayload).json()  #ѧ����Ϣ
        studentName = List_json['data'][0]['cardusername']
        print studentName, '���'

    def getBorrowList(self):
        self.books = {}
        page = '1' 
        BorrowPayload = {
            'userId': self.userId,
            'libraryId': self.libraryId,
            'token': self.token,
            'page': page
            }
        Borrow_json = requests.post(self.host+'/api/borrow/getList.html', data=BorrowPayload).json()  #�ڽ�ͼ��
        for book in Borrow_json['data']:
            print '-' * 20
            print '����:', book['name']
            print '��������', book['loan_DATE']
            print '���뻹�黹��', book['surplus_DAYS'], '��'
            
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
            RenewSome_json = requests.post(self.host+'/api/borrow/continue.html', data=RenewSomePayload).json()  #����
            #print '-' * 20
            #print '����:', book
            #print '������:', RenewSome_json['msg']
            

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
                RenewAll_json = requests.post(self.host+'/api/borrow/continue.html', data=RenewAllPayload).json()  #����
                #print '-' * 20
                #print '����:', book
                #print '������:', RenewAll_json['msg']

                content += '-' * 20 + '\n����: ' + book + '\n������: ' + RenewAll_json['msg'] + '\n'
                
            else:
                content += '-' * 20 + '\n����: ' + book + '\n������: ' + '�����Զ����軹��' + self.books[book][1] + '��' + '\n'
                
        return '��һ������ ' + str(len(self.books)) + '����\n' + content
            
    def autoRenewAll(self):
        while 1:
            sw.Login() #��ֹtokenʧЧ
            content = self.RenewAll()
            print '-' * 20
            print content
            self.Email(content.encode('utf8'))
            time.sleep(86400) #һ��
            os.system('cls')
        
    def Email(self, content):
        yag = yagmail.SMTP(user = '���ͷ�����', password = '���ͷ���������', host = '����host', port = '25') #��139����host��smtp.139.com
        yag.send(to = "���շ�����", subject = "Troy's Sw_Spider", contents = content) 
        print 'Email successfully!'


username = '***********'    #�˺�
password = '*********'      #����
#BookList = ['Ӧ��MATLABʵ��������', 'PHP��MySQL��JavaScriptѧϰ�ֲ�']

#BookList = [book.decode('gbk') for book in BookList] #�ǵý��б���
sw = Sw(username, password)
sw.Login()                 #��¼
#sw.getStuInfo()            #��ȡѧ����Ϣ
#sw.getBorrowList()         
#sw.RenewSome(BookList)
#sw.RenewAll()
#sw.autoRenewAll()