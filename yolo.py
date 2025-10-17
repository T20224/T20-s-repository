# yolo.py

'''
目前可以实现两个功能，预定文件夹中图片的内容识别，以及摄像头实时物体识别
整体代码思路是自己设计的，实操还得找deepseek嘻嘻嘻
python版本3.11.9，yolo用的是最轻量级的yolov8n.pt，防止电脑死机
图片识别好像有概率不成功，一定要有清晰的物体符合预定模型
实时识别可能会收到摄像头自带背景模糊和眼神追踪功能的影响
按照学姐的嘱咐加了一些个性化的输出
'''

from ultralytics import YOLO
import cv2
import os

def detect_local_images():     #检测本地图片

    model = YOLO('yolov8n.pt')
    
    # 创建输入和输出文件夹
    os.makedirs('input_images', exist_ok=True)
    os.makedirs('output_images', exist_ok=True)
    print("请将待检测的图片放入 'input_images' 文件夹，自个找在哪吧")
    input("按回车键一眼顶针")
    
    # 检查输入文件夹中的图片
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    image_files = []
    for file in os.listdir('input_images'):
        if any(file.lower().endswith(ext) for ext in image_extensions):
            image_files.append(file)
    if not image_files:
        print("文件夹里啥也没找着啊")
        return
    print(f"🔍 找到 {len(image_files)} 张图片进行检测")
    
    for i, image_file in enumerate(image_files):
        input_path = os.path.join('input_images', image_file)
        output_path = os.path.join('output_images', f'detected_{image_file}')
        print(f"处理图片 {i+1}/{len(image_files)}: {image_file}")
        
        # 进行检测
        results = model(input_path)
        
        # 保存结果图片
        for r in results:
            im_array = r.plot()
            cv2.imwrite(output_path, im_array)
            print(f"✅ 结果保存至: {output_path}")
            
            # 显示检测统计
            print("检测统计:")
            detected_objects = {}
            for box in r.boxes:
                class_id = int(box.cls[0])
                class_name = model.names[class_id]
                if class_name in detected_objects:
                    detected_objects[class_name] += 1
                else:
                    detected_objects[class_name] = 1
            for obj, count in detected_objects.items():
                print(f"  - {obj}: {count}个")

def yolo_webcam_detection():       #YOLO实时摄像头检测
    print("开眼！")
    model = YOLO('yolov8n.pt')
    
    # 打开摄像头
    cap = cv2.VideoCapture(0)
    print("摄像头已开启，按 'ESC' 退出")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        #YOLO检测
        results = model(frame)
        
        #绘制检测结果
        annotated_frame = results[0].plot()
        
        #帧率
        fps = cap.get(cv2.CAP_PROP_FPS)
        cv2.putText(annotated_frame, f'FPS: {fps:.1f}', 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        #画面
        cv2.imshow('YOLOT20', annotated_frame)
        
        #退出
        if cv2.waitKey(1) & 0xFF == 27:
            break
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    print("我是yolo，想让我看啥子")
    print("1. 图片检测")
    print("2. 实时摄像头检测")
    
    choice = input("请输入选择 (1或2):")
    
    if choice == '1':
        #yolo_image_detection()
        detect_local_images()
    elif choice == '2':
        yolo_webcam_detection()