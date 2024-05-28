import numpy as np
import cv2
import tritonclient.grpc as grpcclient
import sys
import argparse
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import json

def send_gmail(image_name, mail_to, mail_subject, mail_body):

    settings_file = open('settings.json','r')
    settings_data = json.load(settings_file)
    gmail_addr = settings_data['gmail_addr']
    app_passwd = settings_data['app_passwd']

    msg = MIMEMultipart()
    msg['Subject'] = mail_subject
    msg['From'] = gmail_addr
    msg['To'] = mail_to
    msg.attach(MIMEText(mail_body, "plain", "utf-8"))

    path = os.environ['HOME'] + f'/Pictures/{image_name}'
    with open(path, 'rb') as f:
        img_data = f.read()
    image = MIMEImage(img_data, name=os.path.basename(path))
    msg.attach(image)

    try:
        smtpobj = smtplib.SMTP('smtp.gmail.com', 587)  
        smtpobj.ehlo()                                 
        smtpobj.starttls()                             
        smtpobj.login(gmail_addr, app_passwd)          

        smtpobj.sendmail(gmail_addr, mail_to, msg.as_string())

        smtpobj.quit()

    except Exception as e:
        print(e)
    
    return "The email was sent successfully."

def get_triton_client(url: str = 'localhost:8001'):
    try:
        keepalive_options = grpcclient.KeepAliveOptions(
            keepalive_time_ms=2**31 - 1,
            keepalive_timeout_ms=20000,
            keepalive_permit_without_calls=False,
            http2_max_pings_without_data=2
        )
        triton_client = grpcclient.InferenceServerClient(
            url=url,
            verbose=False,
            keepalive_options=keepalive_options)
    except Exception as e:
        print("channel creation failed: " + str(e))
        sys.exit()
    return triton_client


def draw_bounding_box(img, class_id, confidence, x, y, x_plus_w, y_plus_h):
    label = f'({class_id}: {confidence:.2f})'
    color = (255, 0, )
    cv2.rectangle(img, (x, y), (x_plus_w, y_plus_h), color, 2)
    cv2.putText(img, label, (x - 10, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)


def read_image(original_image, expected_image_shape) -> np.ndarray:
    expected_width = expected_image_shape[0]
    expected_height = expected_image_shape[1]
    expected_length = min((expected_height, expected_width))
    [height, width, _] = original_image.shape
    length = max((height, width))
    image = np.zeros((length, length, 3), np.uint8)
    image[0:height, 0:width] = original_image
    scale = length / expected_length

    input_image = cv2.resize(image, (expected_width, expected_height))
    input_image = (input_image / 255.0).astype(np.float32)

    # Channel first
    input_image = input_image.transpose(2, 0, 1)

    # Expand dimensions
    input_image = np.expand_dims(input_image, axis=0)
    return original_image, input_image, scale


def run_inference(model_name: str, input_image: np.ndarray,
                  triton_client: grpcclient.InferenceServerClient):
    inputs = []
    outputs = []
    inputs.append(grpcclient.InferInput('images', input_image.shape, "FP32"))

    inputs[0].set_data_from_numpy(input_image)

    outputs.append(grpcclient.InferRequestedOutput('num_detections'))
    outputs.append(grpcclient.InferRequestedOutput('detection_boxes'))
    outputs.append(grpcclient.InferRequestedOutput('detection_scores'))
    outputs.append(grpcclient.InferRequestedOutput('detection_classes'))

    results = triton_client.infer(model_name=model_name,
                                  inputs=inputs,
                                  outputs=outputs)

    num_detections = results.as_numpy('num_detections')
    detection_boxes = results.as_numpy('detection_boxes')
    detection_scores = results.as_numpy('detection_scores')
    detection_classes = results.as_numpy('detection_classes')
    return num_detections, detection_boxes, detection_scores, detection_classes


def main(model_name, url):
    triton_client = get_triton_client(url)
    expected_image_shape = triton_client.get_model_metadata(model_name).inputs[0].shape[-2:]

    cap = cv2.VideoCapture(0)

    while(True):
        ret, frame = cap.read()
        original_image, input_image, scale = read_image(frame, expected_image_shape)
        num_detections, detection_boxes, detection_scores, detection_classes = run_inference(
            model_name, input_image, triton_client)

        for index in range(num_detections):
            if(detection_classes[index] == 0):
                box = detection_boxes[index]
                draw_bounding_box(original_image,
                                  detection_classes[index],
                                  detection_scores[index],
                                  round(box[0] * scale),
                                  round(box[1] * scale),
                                  round((box[0] + box[2]) * scale),
                                  round((box[1] + box[3]) * scale))
            
                mail_to = "leandra345@sqyieldvd.com"
                mail_subject = "Person is detected" 
                mail_body = "Attention! Somebody has entered a restricted area!" 

                image_name = 'person.jpg'
                cv2.imwrite(os.environ['HOME'] + f'/Pictures/{image_name}', original_image)
                result = send_gmail(image_name, mail_to, mail_subject, mail_body)
                print(result)


        cv2.imshow('camera' , original_image)
        key =cv2.waitKey(10)
        if key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_name', type=str, default='yolov9_ensemble')
    parser.add_argument('--url', type=str, default='119.134.23.56:8001')
    args = parser.parse_args()
    main(args.model_name, args.url)
