from launch import LaunchDescription
from launch.actions import EmitEvent, RegisterEventHandler
from launch.events import matches_action
from launch_ros.actions import LifecycleNode
from launch_ros.events.lifecycle import ChangeState
from launch_ros.event_handlers import OnStateTransition
from lifecycle_msgs.msg import Transition
from launch_pal import get_pal_configuration
from launch.event_handlers import OnProcessStart
from launch.actions import TimerAction


def generate_launch_description():
    pkg = 'ljs'
    node = 'ljs'
    ld = LaunchDescription()

    config = get_pal_configuration(pkg=pkg, node=node, ld=ld)

    node = LifecycleNode(
        package=pkg,
        executable='start_skill',
        namespace='',
        name=node,
        parameters=config["parameters"],
        remappings=config["remappings"],
        arguments=config["arguments"],
        output='both', emulate_tty=True,
        )

    ld.add_action(node)


    delayed_configure_event = TimerAction(
        period=5.0,
        actions=[EmitEvent(event=ChangeState(
            lifecycle_node_matcher=matches_action(node),
            transition_id=Transition.TRANSITION_CONFIGURE))]
    )

    ld.add_action(RegisterEventHandler(
        OnProcessStart(
            target_action=node,
            on_start=[delayed_configure_event]
        )
    ))

    activate_event = RegisterEventHandler(OnStateTransition(
        target_lifecycle_node=node, goal_state='inactive',
        entities=[EmitEvent(event=ChangeState(
            lifecycle_node_matcher=matches_action(node),
            transition_id=Transition.TRANSITION_ACTIVATE))],
        handle_once=True))

    ld.add_action(activate_event)

    return ld
