from setuptools import find_packages, setup

package_name = 'nodes_package'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='aalbeerto-02',
    maintainer_email='a.leon.2020@alumnos.urjc.es',
    description='Implementación de un robot por cables para el control de un efector final en diversas tareas',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'version0_node = nodes_package.version0_node:main',
            'version0_publisher = nodes_package.version0_publisher:main',
            'version0_subscriber = nodes_package.version0_subscriber:main',
            'version1_node = nodes_package.version1_node:main',
            'version1_subscriber = nodes_package.version1_subscriber:main',
            'version2_node = nodes_package.version2_node:main',
            'version2_subscriber = nodes_package.version2_subscriber:main',
            'version3_node = nodes_package.version3_node:main',
            'version3_subscriber = nodes_package.version3_subscriber:main'
        ],
    },
)