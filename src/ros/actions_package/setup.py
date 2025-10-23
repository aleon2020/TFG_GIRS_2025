from setuptools import find_packages, setup

package_name = 'actions_package'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
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
            "count_until_server = actions_package.count_until_server:main",
            "count_until_client = actions_package.count_until_client:main"
        ],
    },
)
