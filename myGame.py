import cv2
import pyautogui
from myPose import myPose
from time import sleep

class myGame():
    def __init__(self):
        self.pose = myPose()
        self.game_started = False
        self.x_position = 1 #0: vai trai, 1: giua  ,2: bên phải
        self.y_position = 1 #0: dow, 1: Stand<<dunsg> , 2:Jump
        self.clap_duration =0# số lượng frame mà người dùng vỗ tau ,, có nghĩa là vỗ tay để nguyên 10s mới tính

    #tạo hàm duy chuyển LRC bằng nút tự động ..
    def move_LRC(self,LRC):
        if LRC =="L":
            #for _ in range(self.x_position): # có nghĩ duyệt và bấm đến khi tới vị trí left nhất thì gán lại bằng 0.. 0->x_postion<<2>>
            pyautogui.keyDown('left')
            self.x_position = 0
        elif LRC =="R":
            #for _ in range(2,self.x_position,-1):
            pyautogui.keyDown('right')
            self.x_position =2
        else:
            if self.x_position == 0:
                pyautogui.press('right')
            elif self.x_position ==2:
                pyautogui.press('left')
            self.x_position =1
        return
    #tạo hàm nút chuyển dộng lên xuống
    def move_JSD(self, JSD):
        if (JSD=="J") and (self.y_position == 1):
            pyautogui.press('up') #nhay
            self.y_position = 2
        elif (JSD=="D") and (self.y_position==1):
            pyautogui.press('down')
            self.y_position = 0
        elif (JSD=="S") and (self.y_position != 1):
            self.y_position =1 # dung
        return

    # hàm xử xử lý và ảnh đầu vào

    def play(self):
        cap = cv2.VideoCapture(0)
        cap.set(3, 500) # thiết lập đầu vào 1280x960
        cap.set(4, 400)
        while(True):
            ret,image = cap.read()
            if ret:
                image = cv2.flip(image,1)
                image_heght, image_width, _ = image.shape
                image, results =self.pose.dectect_pose(image)
                if results.pose_landmarks:
                    #kieerm tra xem game bat dau chua
                    #neesu co
                    if self.game_started:
                        #kiem tra trai,phai
                        image,LRC = self.pose.checkPose_LRC(image,results)
                        self.move_LRC(LRC)

                        #kiem tra len xuong
                        image,JSD = self.pose.checkPose_JSD(image,results)
                        self.move_JSD(JSD)

                    else:
                        cv2.putText(image, "Clap your hand to start!", (5, image_heght-10), cv2.FONT_HERSHEY_PLAIN, 2, (192,192,192), 3)
                        #print("sss")
                        #print(image_heght)
                    #kiem tra xem co vo tay hay koo
                    image,CLAP = self.pose.checkPose_Clap(image, results)
                    if CLAP =="C":
                        self.clap_duration +=1

                        if self.clap_duration ==1:  # 10 fram thi se bat dau game(giu 10s)
                            # th1: dang choi bat dau lai.. reset
                            if self.game_started:
                                self.x_position =1
                                self.y_position =1
                                self.pose.save_shoulder_line_y(image,results)#khi game bat dau luu lai vi tri 2 vai
                                pyautogui.press('space')
                            else: # choi moi chua bat dau bao gio
                                self.game_started = True
                                self.pose.save_shoulder_line_y(image, results)  # khi game bat dau luu lai vi tri 2 vai
                                pyautogui.click(x=720,y=560, button = "left")
                            #self.clap_duration =0
                    else:
                        self.clap_duration =0




                cv2.imshow("game",image)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        cap.release()
        cv2.destroyAllWindows()

myGame=myGame()
myGame.play()









