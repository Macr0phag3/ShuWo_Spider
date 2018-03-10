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

        login_json = requests.post(self.host+'/api/user/loginByPhone.html', data=loginPayload).json()   #登录
        
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
        List_json = requests.post(self.host+'/api/userLibrary/getList.html', data=ListPayload).json()  #学生信息
        studentName = List_json['data'][0]['cardusername']
        print studentName, u'你好'

    def RoomInfo(self):
        SeatsPayload = {
            'roomid': '36', #南校区只有B208
            'appointmentDay': self.dayTime,
            'libraryid': self.libraryId,
            }
        
        Seats_html = requests.get(self.host+'/library/seatview/seatList.html', params=SeatsPayload).text #座位列表
        SelectableList = re.findall(r"'([0-9][0-9][0-9][0-9])'", Seats_html)
        print u'可选座位有', len(SelectableList), u'个'

        return self.seatid in SelectableList


    def getAppointmentInfo(self):
        AppointmentPayload = {
                'libraryid': self.libraryId,
                'userid': self.userId,
                'token': self.token
                }
        Appointment_json = requests.post(self.host+'/api/YySeatAppointment/getUserAppointmentInfoes.html', data=AppointmentPayload).json() #预约信息
        
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
        AppointSeat_json = requests.post(self.host+'/api/YySeatAppointment/addes.html', data=AppointSeatPayload).json() #抢座
        print AppointSeat_json['msg']
        if int(AppointSeat_json['code']):
            print u'预约的座位号为', AppointSeat_json['data']['num'], u', 别忘了30min过去签到'
            return [1, u'预约的座位号为' + AppointSeat_json['data']['num'] + u', 别忘了30min过去签到']
        else:
            return [0]
            
        #else:
            #print '你要的座位有人预约了'
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
        Random_json = requests.post(self.host+'/api/YySeatAppointment/autoAppointmentes.html', data=RandomPayload).json() #随机预约
        print Random_json['msg']
        if int(Random_json['code']):
            print u'随机预约的座位号为', Random_json['data']['num'], u', 别忘了30min过去签到'
            return [1, u'随机预约的座位号为' + Random_json['data']['num'] + u', 别忘了30min过去签到']
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
            
            cancel_json = requests.post(self.host+'/api/YySeatAppointment/cancelAppointmentes.html', data=cancelPayload).json() #取消预约
            print cancel_json['msg']

            
    def SpyOneSeat(self, seatid): #持续监视指定座位
        self.Login()
        while 1:
            try:
                Info = self.AppointSeat(seatid)
            except:
                self.Login() #token 失效
                Info = self.AppointSeat(seatid)
                
            if Info[0]:
                print '-'*10, u'成功抢到座位', '-'*10
                content = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + u' 成功抢到座位! ' + Info[1]
                self.Email(content.encode('utf8'))
                return 1
            
            time.sleep(2)
            os.system('clear')



    def SpyAllSeat(self): #持续监视所有座位
        self.Login()

        while 1:
            try:
                Info = self.RandomAppointment()
            except:
                self.Login()
                Info = self.RandomAppointment()
                
            if Info[0]:
                print '-'*10, u'成功抢到座位', '-'*10
                content = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + u' 成功抢到座位! ' + Info[1]
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
        if u'异常' in affirm_json['msg']:
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
        if u'异常' in release_json['msg']:
            return 0
        else:
            return 1
        
        
    def SpyTime(self, Time, seatid): #指定时间抢座, 如果使用SpyOneSea(), 要添加参数seatid
        print u'等待时间到', Time
        while 1:
            if time.strftime("%H:%M:%S", time.localtime()) == Time:
                print '-'*10, u'时间到!', '-'*10
                #self.SpyAllSeat()
                #self.SpyOneSeat(seatid)
                break
                
    def Email(self, content):
        yag = yagmail.SMTP(user = '发送方邮箱', password = '发送方邮箱密码', host = '邮箱host', port = '25') #如139邮箱host是smtp.139.com
        yag.send(to = "接收方邮箱", subject = "Troy's Sw_Spider", contents = content) 
        print 'Email successfully!'


username = '***********'    #账号
password = '*********'      #密码
dayTime  = '2017-08-09'     #预约日期(格式要对)
seatid   = '160'            #预约座位号
Time     = '10:12:05'       #预约时间(格式要对)

sw = Sw(username, password, dayTime, seatid)
sw.Login()                 #登录
#sw.RandomAppointment()     #随机选择空座位
sw.getStuInfo()            #获取学生信息
sw.getAppointmentInfo()    #获取预约信息
sw.RoomInfo()              #获取自习室信息
#sw.AppointSeat(seatid)     #预约指定座位
#sw.affirmSeat(seatid)     #确认入座
#sw.Release(seatid)         #释放座位
#sw.SpyOneSeat(seatid)      #监视指定座位
#sw.SpyAllSeat()            #监视所有座位
#sw.SpyTime(Time, seatid)   #指定时间抢座
#sw.Cancle()                #取消预约的座位