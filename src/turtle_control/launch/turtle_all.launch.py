import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess, RegisterEventHandler, Shutdown
from launch.event_handlers import OnProcessExit

def generate_launch_description():
	turtlesim_node = Node(
		package='turtlesim',
		executable='turtlesim_node',
		name='turtlesim'
	)

	controller_node = Node(
		package='turtle_control',
		executable='turtle_controller',
		name='turtle_controller',
		output='screen'
	)

	pyqt_process = ExecuteProcess(
		cmd=['python3', os.path.expanduser('~/turtle_control/pyqt_app/main_window.py')],
		output='screen'
	)

	shutdown_handler = RegisterEventHandler(
		OnProcessExit(
			target_action=pyqt_process,
			on_exit=[Shutdown()]
		)
	)

	return LaunchDescription([
		turtlesim_node,
		controller_node,
		pyqt_process,
		shutdown_handler
	])