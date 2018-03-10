# -*- coding: gbk -*- 
import requests
import pprint,re
import time,os
import yagmail

class Sw():
    def __init__(self, username, password, dayTime, seatid):
        self.username = username
        self.password = password
        self.dayTime = dayTime
        self.seatid = seatid
        self.host = 'http://t1.beijingzhangtu.com'
        self.appointmentStartTime = '08:00'
        self.appointmentEndTime = '22:00'
        
    def Login(self):
        loginPayload = {
            'phone': self.username,
            'pass': self.password
            }

        login_json = requests.post(self.host+'/api/user/loginByPhone.html', data=loginPayload).json()   #��¼
        
        assert int(login_json['code']), login_json['msg']
        print login_json['msg']
        
        self.userId = login_json['data']['id']
        #pprint.pprint(login_json)
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
        print studentName, u'���'

    def RoomInfo(self):
        SeatsPayload = {
            'roomid': '36', #��У��ֻ��B208
            'appointmentDay': self.dayTime,
            'libraryid': self.libraryId,
            }
        
        Seats_html = requests.get(self.host+'/library/seatview/seatList.html', params=SeatsPayload).text #��λ�б�
        SelectableList = re.findall(r"'([0-9][0-9][0-9][0-9])'", Seats_html)
        print u'��ѡ��λ��', len(SelectableList), u'��'

        return self.seatid in SelectableList


    def getAppointmentInfo(self):
        AppointmentPayload = {
                'libraryid': self.libraryId,
                'userid': self.userId,
                'token': self.token
                }
        Appointment_json = requests.post(self.host+'/api/YySeatAppointment/getUserAppointmentInfoes.html', data=AppointmentPayload).json() #ԤԼ��Ϣ
        
        if Appointment_json['msg']:
            print Appointment_json['msg']
            return 0
        else:
            self.seatAppointmentId = Appointment_json['data'][0]['keyid']
            return 1

        
    def AppointSeat(self, seatid):
        self.seatid = str(int(seatid) + 3935)
        #if self.RoomInfo():
        AppointSeatPayload = {
            'appointmentStartTime': self.appointmentStartTime,
            'appointmentEndTime': self.appointmentEndTime,
            'appointmentDay': self.dayTime, 
            'seatid': self.seatid, 
            'libraryid': self.libraryId,
            'userid': self.userId,
            'token': self.token
            }
        AppointSeat_json = requests.post(self.host+'/api/YySeatAppointment/addes.html', data=AppointSeatPayload).json() #����
        print AppointSeat_json['msg']
        if int(AppointSeat_json['code']):
            print u'ԤԼ����λ��Ϊ', AppointSeat_json['data']['num'], u', ������30min��ȥǩ��'
            return [1, u'ԤԼ����λ��Ϊ' + AppointSeat_json['data']['num'] + u', ������30min��ȥǩ��']
        else:
            return [0]
            
        #else:
            #print '��Ҫ����λ����ԤԼ��'
            #return [0]


    def RandomAppointment(self):
        RandomPayload = {
            'floorid': '9',
            'roomid': '36',
            'appointmentStartTime': self.appointmentStartTime,
            'appointmentEndTime': self.appointmentEndTime,
            'buildingid': '8',
            'appointmentDay': self.dayTime,
            'libraryid': self.libraryId,
            'userid': self.userId,
            'token': self.token
            }
        
        print RandomPayload
        Random_json = requests.post(self.host+'/api/YySeatAppointment/autoAppointmentes.html', data=RandomPayload).json() #���ԤԼ
        print Random_json['msg']
        if int(Random_json['code']):
            print u'���ԤԼ����λ��Ϊ', Random_json['data']['num'], u', ������30min��ȥǩ��'
            return [1, u'���ԤԼ����λ��Ϊ' + Random_json['data']['num'] + u', ������30min��ȥǩ��']
        else:
            return [0]

        
    def Cancle(self):
        if self.getAppointmentInfo():
            cancelPayload = {
                'seatAppointmentId': self.seatAppointmentId,
                'libraryId': self.libraryId,
                'userId': self.userId,
                'token': self.token
                }
            
            cancel_json = requests.post(self.host+'/api/YySeatAppointment/cancelAppointmentes.html', data=cancelPayload).json() #ȡ��ԤԼ
            print cancel_json['msg']

            
    def SpyOneSeat(self, seatid): #��������ָ����λ
        self.Login()
        while 1:
            try:
                Info = self.AppointSeat(seatid)
            except:
                self.Login() #token ʧЧ
                Info = self.AppointSeat(seatid)
                
            if Info[0]:
                print '-'*10, u'�ɹ�������λ', '-'*10
                content = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + u' �ɹ�������λ! ' + Info[1]
                self.Email(content.encode('utf8'))
                return 1
            
            time.sleep(2)
            os.system('clear')



    def SpyAllSeat(self): #��������������λ
        self.Login()

        while 1:
            try:
                Info = self.RandomAppointment()
            except:
                self.Login()
                Info = self.RandomAppointment()
                
            if Info[0]:
                print '-'*10, u'�ɹ�������λ', '-'*10
                content = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + u' �ɹ�������λ! ' + Info[1]
                self.Email(content.encode('utf8'))
                return 1
            
            time.sleep(60)
            os.system('clear')


    def affirmSeat(self, seatid):
        affirmPayload = {
            'libraryid': self.libraryId,
            'seatid': str(int(seatid) + 3935),
            'token': self.token,
            'userid': self.userId,
        }
        affirm_json = requests.post(self.host+'/api/YySeatAppointment/affirmSeat.html',data = affirmPayload).json()
        print affirm_json['msg']
        if u'�쳣' in affirm_json['msg']:
            return 0
        else:
            return 1
        
        
    def Release(self, seatid):
        sw.getAppointmentInfo()
        keyid = self.seatAppointmentId
        
        ReleasePayload = {
            'libraryid':self.libraryId,
            'seatAppointmentId': keyid,
            'token': self.token,
            'userid': self.userId,
        }      
        release_json = requests.post(self.host+'/api/YySeatAppointment/releaseBySelfes.html', data = ReleasePayload).json()
        print release_json['msg']
        if u'�쳣' in release_json['msg']:
            return 0
        else:
            return 1
        
        
    def SpyTime(self, Time, seatid): #ָ��ʱ������, ���ʹ��SpyOneSea(), Ҫ��Ӳ���seatid
        print u'�ȴ�ʱ�䵽', Time
        while 1:
            if time.strftime("%H:%M:%S", time.localtime()) == Time:
                print '-'*10, u'ʱ�䵽!', '-'*10
                #self.SpyAllSeat()
                #self.SpyOneSeat(seatid)
                break
                
    def Email(self, content):
        yag = yagmail.SMTP(user = '���ͷ�����', password = '���ͷ���������', host = '����host', port = '25') #��139����host��smtp.139.com
        yag.send(to = "���շ�����", subject = "Troy's Sw_Spider", contents = content) 
        print 'Email successfully!'


username = '***********'    #�˺�
password = '*********'      #����
dayTime  = '2017-08-09'     #ԤԼ����(��ʽҪ��)
seatid   = '160'            #ԤԼ��λ��
Time     = '10:12:05'       #ԤԼʱ��(��ʽҪ��)

sw = Sw(username, password, dayTime, seatid)
sw.Login()                 #��¼
#sw.RandomAppointment()     #���ѡ�����λ
sw.getStuInfo()            #��ȡѧ����Ϣ
sw.getAppointmentInfo()    #��ȡԤԼ��Ϣ
sw.RoomInfo()              #��ȡ��ϰ����Ϣ
#sw.AppointSeat(seatid)     #ԤԼָ����λ
#sw.affirmSeat(seatid)     #ȷ������
#sw.Release(seatid)         #�ͷ���λ
#sw.SpyOneSeat(seatid)      #����ָ����λ
#sw.SpyAllSeat()            #����������λ
#sw.SpyTime(Time, seatid)   #ָ��ʱ������
#sw.Cancle()                #ȡ��ԤԼ����λ