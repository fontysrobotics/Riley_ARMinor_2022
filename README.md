# Riley_ARMinor_2022
Remote indoor Inspection with Low-cost robots (RILey)
## Github file structure
- `docs` : in-development website containing documentation for the RILey robot, as well as pictures of the robot and meta information. Ideally could be run through Github Pages (can be setup in repository settings) but can also be built and run locally through VSCode.
- `documentation` : All documentation created during the project. This includes the initial project information, the plan of approach (before project requirements shifted drastically), datasheets for some of the components, the technical documentation for setting up many aspects of the robot and server systems, plus additional video material.
- `electrical` : Documentation related to the electrical design of the RILey robot, including version 1 and 2 of the PCB design, notes regarding problems encountered in the PCB design and explanations/schematics for the global electrical connections.
- `ros2` : Code files needed to run the robot (physical and simulation) through ROS2-foxy. More info included in technical document. Included are:
  - `riley_ws` : Main ROS workspace containing all the packages and launch files for both robot and server side.
  - `simulation` : ROS workspace used for simulating the robot in a virtual environment (Gazebo).
  - `yolov5` : Separate directory used to store the YOLOv5 object recognition model.
- `solidworks` : Solidworks CAD files making up version 1 and 2 of the RILey robot, including imported assets. Additional folders for STL/DXF component exports also available, though not needed for the CAD assemblies.
