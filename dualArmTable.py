from pyrep import PyRep
from pyrep.robots.arms.panda import Panda
from pyrep.robots.end_effectors.panda_gripper import PandaGripper
from pyrep.const import PrimitiveShape
from pyrep.objects import Camera, Shape, VisionSensor
import numpy as np
from setupFuncs import setAonB, create_table, top_of
from wrappers import robotControl as rc

### SETUP CODE ###
pr = PyRep()
pr.launch("scenes/emptyVortex.ttt", headless=False, responsive_ui=True)

scene_view = Camera('DefaultCamera')
scene_view.set_position([3.45, 0.18, 2.0])
scene_view.set_orientation(np.array([180, -70, 90]) * np.pi / 180.0)

depth_cam = VisionSensor.create([256, 256], position=[0, 0, 2.0], orientation=np.array([0.0, 180.0, -90.0]) * np.pi / 180.0 )

# Import Robots
pr.import_model("models/Panda.ttm")
pr.import_model("models/Panda.ttm")


# Table Creation
table = create_table(pr, 1.2, 2.5, 0.8)

# Trays Creation
in_tray = pr.import_model("models/Tray.ttm")
setAonB(in_tray, table, 0.1, -0.4)

out_tray = pr.import_model("models/Tray.ttm")
setAonB(out_tray, table, 0.1, 0.4)

c1 = Shape.create(type=PrimitiveShape.CUBOID, color=[0.5, 0.0, 0.0], size=[0.05, 0.05, 0.05], visible_edges=True, mass=0.01)
print("Friction coeef: ", c1.get_bullet_friction())
setAonB(c1, in_tray, np.random.uniform(-0.05, 0.05), np.random.uniform(-0.05, 0.05))

pr.step_ui()

panda_1 = Panda(0)
gripper_1 = PandaGripper(0)

panda_2 = Panda(1)
gripper_2 = PandaGripper(1)

setAonB(panda_1, table, -0.5, -0.4)
setAonB(panda_2, table, -0.5, 0.4)


#############################################
pr.start()
pr.step()

### Robot Movement Code Goes Here ####

cube_pos_from_im = rc.location_from_depth_cam(pr, depth_cam, c1)
rc.move_to_pos(pr, panda_1, cube_pos_from_im, z_offset=-0.04)
rc.grasp(pr, gripper_1, True)
rc.move_to_pos(pr, panda_1, cube_pos_from_im, z_offset=0.1)


lift_pos = [np.random.uniform(-0.05, 0.05), np.random.uniform(-0.05, 0.05), top_of(table)[2] + 0.1]
rc.move_to_pos(pr, panda_1, lift_pos)
rc.grasp(pr, gripper_1, False)
lift_pos[1] -= 0.45
rc.move_to_pos(pr, panda_1, lift_pos)

cube_pos_from_im = rc.location_from_depth_cam(pr, depth_cam, c1)
rc.move_to_pos(pr, panda_2, cube_pos_from_im, z_offset=-0.02)
rc.grasp(pr, gripper_2, True)

rc.move_above_object(pr, panda_2, out_tray, z_offset=0.1)
rc.grasp(pr, gripper_2, False)

for i in range(400):
    pr.step()
    if i % 100 == 0:
        print(i)

#########################################

pr.stop()


pr.shutdown()

print("Phew! We got home nice and safe...")
