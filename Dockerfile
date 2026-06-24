FROM eprosima/vulcanexus:jazzy-desktop-4.4.1 AS build
SHELL ["/bin/bash", "-c"]


COPY requirements.txt .
RUN #python3 -m pip install -r requirements.txt --break-system-packages
RUN pip3 install -r requirements.txt --break-system-packages

WORKDIR /app

COPY lib ./lib
RUN source /opt/vulcanexus/jazzy/setup.bash \
    && colcon build --packages-select launch_pal std_skills

COPY src ./src
RUN source /opt/vulcanexus/jazzy/setup.bash \
    && colcon build --packages-select ljs ljs_skill_msgs

FROM eprosima/vulcanexus:jazzy-desktop-4.4.1 AS prod


RUN apt install python3-pip -y
COPY requirements.txt .
RUN pip3 install -r requirements.txt --break-system-packages

WORKDIR /app
COPY --from=build /app/install ./install

COPY ./eureka_entrypoint.sh /
ENTRYPOINT ["/bin/bash", "/eureka_entrypoint.sh"]

CMD ["bash"]

