^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Changelog for package std_skills
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1.1.0 (2025-02-13)
------------------
* clarify the semantic of the priority and expose 3 priority constants
* Contributors: Séverin Lemaignan

1.0.0 (2025-01-15)
------------------
* add README
* inhibit -Wfloat-equal that causes warnings on PAL CI/CD pipeline
* use ament_auto_cmake + licensing
* add dep on action_msgs in CMakeLists
* add std action-based 'Empty' skill definition
* add std service-based skills definitions
* add std message-based skills
* initial impl of Meta.msg, Result.msg, Feedback.msg based on PAPS-013
* Contributors: Séverin Lemaignan
