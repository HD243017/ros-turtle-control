import sys
import subprocess
import threading
import rclpy as rp
import mysql.connector
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, 
    QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QMessageBox  # <- QHBoxLayout 추가
)

from turtle_control.turtle_controller import TurtleController

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'azsx1234',
    'database': 'rosdb'
}

class TurtleApp(QWidget):
    def __init__(self, node):
        super().__init__()
        self.node = node
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('ROS2 Turtle Controller')
        self.resize(320, 360)

        main_layout = QVBoxLayout()
        grid = QGridLayout()

        # assign arrow btn
        btn_up = QPushButton('▲')
        btn_down = QPushButton('▼')
        btn_left = QPushButton('◀')
        btn_right = QPushButton('▶')

        btn_up.clicked.connect(lambda: self.node.move_turtle(2.0, 0.0))
        btn_down.clicked.connect(lambda: self.node.move_turtle(-2.0, 0.0))
        btn_left.clicked.connect(lambda: self.node.move_turtle(0.0, 2.0))
        btn_right.clicked.connect(lambda: self.node.move_turtle(0.0, -2.0))

        grid.addWidget(btn_up, 0, 1)
        grid.addWidget(btn_left, 1, 0)
        grid.addWidget(btn_right, 1, 2)
        grid.addWidget(btn_down, 2, 1)
        main_layout.addLayout(grid)

        # reset btn
        btn_reset = QPushButton('Reset Turtle')
        btn_reset.clicked.connect(self.node.reset_turtle)
        main_layout.addWidget(btn_reset)

        # db save btn
        h_layout = QHBoxLayout()

        btn_save = QPushButton('Save Pose to DB')
        btn_save.clicked.connect(self.save_pose_to_db)
        h_layout.addWidget(btn_save)

        btn_load = QPushButton('Load DB')
        btn_load.clicked.connect(self.load_recent_db)
        h_layout.addWidget(btn_load)

        main_layout.addLayout(h_layout)

        # status label
        self.status_label = QLabel('Ready')
        self.status_label.setStyleSheet("font-family: monospace; font-size: 11px;")
        main_layout.addWidget(self.status_label)

        # Exit btn
        btn_shutdown = QPushButton('Exit')
        btn_shutdown.clicked.connect(self.safe_shutdown)
        main_layout.addWidget(btn_shutdown)

        self.setLayout(main_layout)

    def save_pose_to_db(self):
        pose = self.node.current_pose
        if pose is None:
            QMessageBox.warning(self, "warning", "Location not received.")
            return

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            query = "INSERT INTO turtlepos (x, y, theta) VALUES (%s, %s, %s)"
            cursor.execute(query, (pose.x, pose.y, pose.theta))
            conn.commit()
            cursor.close()
            conn.close()

            self.status_label.setText(f"saved: ({pose.x:.2f}, {pose.y:.2f}, {pose.theta:.2f})")
        except Exception as e:
            QMessageBox.critical(self, "DB ERROR", f"failed save: {str(e)}")

    def load_recent_db(self):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            query = "SELECT id, x, y, theta, time FROM turtlepos ORDER BY id DESC LIMIT 5"
            cursor.execute(query)
            rows = cursor.fetchall()
            cursor.close()
            conn.close()

            if not rows:
                self.status_label.setText("No data in DB.")
                return

            lines = ["id | x | y | theta | time"]
            for r in rows:
                t_str = str(r[4])
                lines.append(f"{r[0]} | {r[1]:.2f} | {r[2]:.2f} | {r[3]:.2f} | {t_str}")

            self.status_label.setText("\n".join(lines))

        except Exception as e:
            QMessageBox.critical(self, 'DB Error', f"failed : {str(e)}")

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_W:
            self.node.move_turtle(2.0, 0.0)
        elif key == Qt.Key_S:
            self.node.move_turtle(-2.0, 0.0)
        elif key == Qt.Key_A:
            self.node.move_turtle(0.0, 2.0)
        elif key == Qt.Key_D:
            self.node.move_turtle(0.0, -2.0)
        else:
            super().keyPressEvent(event)

    def safe_shutdown(self):
        self.node.move_turtle(0.0, 0.0)
        self.close()

def main():
    rp.init()
    node = TurtleController()

    # ROS2 Spin 백그라운드 스레드 실행
    spin_thread = threading.Thread(target=rp.spin, args=(node,), daemon=True)
    spin_thread.start()

    app = QApplication(sys.argv)
    window = TurtleApp(node)
    window.show()

    exit_code = app.exec_()

    node.destroy_node()
    if rp.ok():
        rp.shutdown()
    sys.exit(exit_code)

if __name__ == '__main__':
    main()