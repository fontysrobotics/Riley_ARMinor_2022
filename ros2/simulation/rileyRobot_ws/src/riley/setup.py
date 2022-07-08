from setuptools import setup
from glob import glob
import os

package_name = 'riley'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*.model')),
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*.sdf')),
        (os.path.join('share', package_name, 'Riley_URDF'), glob('Riley_URDF/*.urdf')),
        (os.path.join('share', package_name, 'Riley_URDF'), glob('Riley_URDF/*.urdf.xacro')),
        (os.path.join('share', package_name, 'config/slam'), glob('config/slam/*.yaml')),
        (os.path.join('share', package_name, 'config/nav2'), glob('config/nav2/*.yaml')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'rviz'), glob('rviz/*.rviz')),
        
        (os.path.join('share', package_name, 'models/riley'), glob('models/riley/*.sdf')),
        (os.path.join('share', package_name, 'models/rileyWorld'), glob('models/rileyWorld/*.sdf')),
        (os.path.join('share', package_name, 'models/riley/meshes'), glob('models/riley/meshes/*.STL')),
        (os.path.join('share', package_name, 'models/rileyWorld/meshes'), glob('models/rileyWorld/meshes/*.STL')),
        (os.path.join('share', package_name, 'models/riley'), glob('models/riley/*.config')),
        (os.path.join('share', package_name, 'models/rileyWorld'), glob('models/rileyWorld/*.config'))
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='student',
    maintainer_email='student@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        ],
    },
)
