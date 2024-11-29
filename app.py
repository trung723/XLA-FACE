import streamlit as st
import face_recognition
import cv2
import tempfile
import pickle
import os
import json

# Tải dữ liệu khuôn mặt đã lưu
with open("face_database.pkl", "rb") as f:
    face_db = pickle.load(f)

# Tải dữ liệu thông tin người dùng từ person_info.json
with open("person_info.json", "r") as f:
    person_info = json.load(f)

def recognize_face_from_frame(frame, id_encoding=None):
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)
    recognized_names = []

    for encoding in face_encodings:
        recognized = False
        for name, db_encoding in face_db.items():
            matches = face_recognition.compare_faces([db_encoding], encoding)
            if True in matches:
                if id_encoding is not None:
                    id_match = face_recognition.compare_faces([id_encoding], encoding)
                    if id_match[0]:
                        recognized_names.append(name)
                    else:
                        recognized_names.append("ID Mismatch")
                else:
                    recognized_names.append(name)
                recognized = True
                break

        if not recognized:
            recognized_names.append("Unknown")
    return recognized_names, face_locations

st.title("Xác thực Khuôn mặt")

# Tùy chọn xác thực
input_method = st.radio(
    "Chọn phương thức xác thực",
    ("Xác thực bằng video tải lên", "Xác thực bằng webcam", "Xác thực bằng ảnh ID qua webcam")
)

warning_displayed = False

if input_method == "Xác thực bằng video tải lên":
    uploaded_file = st.file_uploader("Tải lên video", type=["mp4", "mov", "avi"])

    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
            temp_video_file.write(uploaded_file.read())
            temp_video_path = temp_video_file.name

        cap = cv2.VideoCapture(temp_video_path)
        stframe = st.empty()

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            recognized_names, face_locations = recognize_face_from_frame(frame)


            for (top, right, bottom, left), name in zip(face_locations, recognized_names):
                if name in person_info:
                    # Lấy thông tin từ person_info
                    email = f"Email: {person_info[name]['email']}"
                    phone = f"Phone: {person_info[name]['phone']}"
                    address = f"Address: {person_info[name]['address']}"
                else:
                    email, phone, address = "Unknown", "", ""

                # Vẽ hình chữ nhật xung quanh khuôn mặt
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 1  # Tăng cỡ chữ
                color = (0, 0, 255)
                thickness = 2

                # Hiển thị từng dòng văn bản ở rìa bên phải của khung
                cv2.putText(frame, name, (right + 10, top - 50), font, 1.5, color, thickness)
                cv2.putText(frame, email, (right + 10, top - 20), font, font_scale, color, thickness)
                cv2.putText(frame, phone, (right + 10, top + 20), font, font_scale, color, thickness)
                cv2.putText(frame, address, (right + 10, top + 50), font, font_scale, color, thickness)


            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            stframe.image(frame)

        cap.release()
        os.remove(temp_video_path)

elif input_method == "Xác thực bằng webcam":
    cap = cv2.VideoCapture(1)
    stframe = st.empty()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        recognized_names, face_locations = recognize_face_from_frame(frame)

        for (top, right, bottom, left), name in zip(face_locations, recognized_names):
            if name in person_info:
                # Lấy thông tin từ person_info
                email = f"Email: {person_info[name]['email']}"
                phone = f"Phone: {person_info[name]['phone']}"
                address = f"Address: {person_info[name]['address']}"
            else:
                email, phone, address = "Unknown", "", ""

            # Vẽ hình chữ nhật xung quanh khuôn mặt
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 1  # Tăng cỡ chữ
            color = (0, 0, 255)
            thickness = 2

            # Hiển thị từng dòng văn bản ở rìa bên phải của khung
            cv2.putText(frame, name, (right + 10, top - 50), font, 1.5, color, thickness)
            cv2.putText(frame, email, (right + 10, top - 20), font, font_scale, color, thickness)
            cv2.putText(frame, phone, (right + 10, top + 20), font, font_scale, color, thickness)
            cv2.putText(frame, address, (right + 10, top + 50), font, font_scale, color, thickness)


        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        stframe.image(frame)

    cap.release()

elif input_method == "Xác thực bằng ảnh ID qua webcam":
    cap = cv2.VideoCapture(1)
    stframe = st.empty()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)

        if len(face_encodings) >= 2:
            face_areas = [(bottom - top) * (right - left) for (top, right, bottom, left) in face_locations]
            main_face_index = face_areas.index(max(face_areas))
            main_face_encoding = face_encodings[main_face_index]

            for i, (face_encoding, (top, right, bottom, left)) in enumerate(zip(face_encodings, face_locations)):
                if i == main_face_index:
                    label = "Nguoi dung"
                    color = (0, 255, 0)
                else:
                    match = face_recognition.compare_faces([main_face_encoding], face_encoding)
                    label = "Khop voi nguoi dung" if match[0] else "khong khop"
                    color = (0, 255, 0) if match[0] else (0, 0, 255)

                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(frame, label, (left, top - 10), font, 0.7, color, 2)

            warning_displayed = False

        else:
            if not warning_displayed:
                st.warning("Vui lòng cầm ảnh khuôn mặt của bạn trước webcam để xác thực.")
                warning_displayed = True

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        stframe.image(frame)

    cap.release()
