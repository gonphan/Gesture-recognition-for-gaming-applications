import mediapipe as mp
import cv2
import math

class myPose():

    def __init__(self): #khởi tạo pose
        # mp.solutions.pose la module trong thư viện MediaPipe của Google,
        # cung cấp một API để xác định các keypoint (điểm nổi bật)
        # trên cơ thể trong hình ảnh hoặc video
        self.mp_pose = mp.solutions.pose # Khởi tạo module pose
        self.pose = self.mp_pose.Pose()# Khởi tạo đối tượng pose
        #vex treen anh, hiễn thị các key_pose
        self.mp_drawing = mp.solutions.drawing_utils

        self.shoudler_line_y = 0 #luu lai vị trí 2 vai nguười dùng khi vỗ tay bắt đầu game

    def dectect_pose(self,image):
        #chuyen qua anh rgb
        image_RGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        #xac dinh cac pose tren anh
        results = self.pose.process(image_RGB)

        """results.pose_landmarks Đối tượng này chứa thông tin về tọa độ(x,y,z) các keypoint nỗi bật trên cơ thể."""
        #nếu như nhận dạng được pose
        if results.pose_landmarks:
            # Thì sẽ vẽ các điểm trên các đường nối nhận được
            # self.mp_drawing.draw_landmarks(image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
            self.mp_drawing.draw_landmarks(image, landmark_list=results.pose_landmarks,
                                           connections=self.mp_pose.POSE_CONNECTIONS,
                                           landmark_drawing_spec=self.mp_drawing.DrawingSpec(color=(255, 225, 255),
                                                                                             thickness=3,
                                                                                             circle_radius=3),#điểm
                                           connection_drawing_spec=self.mp_drawing.DrawingSpec(color=(0, 0, 255),
                                                                                               thickness=2)) #đường viền xanh <<xem lai>>
        return image,results
    # hàm tính trái phải

    def checkPose_LRC(self, image, results): #
        # lay kich thuoc anh
        image_heght, image_width, _ = image.shape
        image_mid_width = image_width//2

        #thuật toán tính xác định trai,phai
        leftShoulder_x = int(results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_SHOULDER].x * image_width)
        rightShoulder_x = int(results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_SHOULDER].x *image_width)

        #đặt điều kiện nếu như vai trai,phải sang trái => trai
        if (leftShoulder_x < image_mid_width) and (rightShoulder_x < image_mid_width):
            LRC = "L"
        elif (leftShoulder_x > image_mid_width) and (rightShoulder_x > image_mid_width):
            LRC = "R"
        else:
            LRC = "C" #giữa

        #hiễn thị chữ lên đó
        cv2.putText(image, LRC, (5, image_heght - 10), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 3) #chữ RLC< trang>
        cv2.line(image, (image_mid_width, 0), (image_mid_width, image_heght), (255, 255, 255), 2) #phân chia khung màn hình
        return image,LRC

    #hàm tính lên xuống
    def checkPose_JSD(self, image, results):
        image_heght, image_width, _ = image.shape
        leftShoulder_y = int(results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_SHOULDER].y * image_heght)
        rightShoulder_y = int(results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_SHOULDER].y * image_heght)

        #tính toán vị tri y giữa để so sánh vz y ban đầu của vai
        #centerShoulder_y = abs(leftShoulder_x,rightShoulder_x) // 2
        centerShoulder_y = abs(leftShoulder_y + rightShoulder_y) // 2

        #độ lệch
        jump_threshold = 30
        down_threshold = 15

        if (centerShoulder_y < self.shoudler_line_y - jump_threshold):
            JSD = "J" # Nhảy
        elif (centerShoulder_y > self.shoudler_line_y +down_threshold):
            JSD = "D" #ngồi
        else:
            JSD = "S" # Đứng
        cv2.putText(image, JSD, (5, image_heght - 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 255), 3)
        cv2.line(image, (0, self.shoudler_line_y), (image_width, self.shoudler_line_y), (0, 255, 255), 2)

        return image , JSD

    #hàm vỗ tay
    def checkPose_Clap(self, image, results):
        image_heght, image_width, _ = image.shape

        left_hand = (results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_WRIST].x * image_width,
                     results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_WRIST].y * image_heght)

        right_hand = (results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_WRIST].x * image_width,
                      results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_WRIST].y * image_heght)

        #tính khoảng cách của 2 tay.. tọa độ (x,y) khoảng cách (x2-x1,y2-y1)
        distance = int(math.hypot(left_hand[0] - right_hand[0], left_hand[1] - right_hand[1]))

        #đặt ngưỡng
        clap_threshold = 100
        if distance < clap_threshold:
            CLAP = "C"
        else:
            CLAP = "N"
        cv2.putText(image, CLAP, (10, 30), cv2.FONT_HERSHEY_PLAIN, 2,(255, 255, 0), 3)
        return image,CLAP

    # lưu lại điểm giữa khi người dùng vỗ 2 tay
    def save_shoulder_line_y(self, image, results):
        image_heght, image_width, _ = image.shape

        leftShoulder_y = int(results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_SHOULDER].y * image_heght)
        rightShoulder_y = int(results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_SHOULDER].y * image_heght)

        self.shoudler_line_y = abs(leftShoulder_y + rightShoulder_y) // 2
        return






