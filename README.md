# ros-turtle-control
## 1. 사전 요구사항
- OS: Ubuntu 22.04 LTS (WSL2)
- ROS Version: ROS2 Humble
- Python 라이브러리 설치:
  pip install PyQt5 mysql-connector-python
- MySQL 서버 설치 및 구동:
  sudo apt install -y mysql-server
  sudo service mysql start

---

## 2. 데이터베이스 초기 설정
1. 스키마 및 테이블 생성
   루트의 schema.sql을 사용해 rosdb 데이터베이스 및 turtlepos 테이블을 생성
   mysql -u root -p < schema.sql

2. 접속 수정
   사용자 환경의 MySQL root 비밀번호에 맞춰 pyqt_app/main_window.py 상단의 DB_CONFIG를 변경
   DB_CONFIG = {
       \"host\": \"localhost\",
       \"user\": \"root\",
       \"password\": \"YOUR_PASSWORD\",
       \"database\": \"rosdb\"
   }

---

## 3. 빌드 및 통합 실행
작업 폴더의 루트에서 빌드 후 런치 파일 실행

1. 패키지 빌드
   colcon build --packages-select turtle_control
   or
   colcon build

2. 환경 설정 로드
   source install/setup.bash

3. 전체 시스템 실행
   ros2 launch turtle_control turtle_all.launch.py

---

## 4. 조작 안내
- GUI 버튼:
    - 방향키 버튼 (▲, ▼, ◀, ▶): 이동 제어
    - Reset Turtle: 초기화
    - Save Pose to DB: 현재 좌표(x, y, theta)를 DB에 기록
- 키보드 조작 (GUI 창 포커스 시):
    - W: 전진 / S: 후진 / A: 좌회전 / D: 우회전

---

## 5. DB 데이터 확인
터미널에서 아래 명령어로 저장된 데이터를 조회
mysql -u root -p -e "SELECT * FROM rosdb.turtlepos;"