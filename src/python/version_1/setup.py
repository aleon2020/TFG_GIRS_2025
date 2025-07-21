from setuptools import setup, find_packages

# COMPILACIÓN, ENLAZADO Y EJECUCIÓN
# $ cd version_1/
# $ ls
# setup.py  version_1/
# $ pip install -e . --break-system-packages
# $ python3 -m version_1.cinematic_model_v1
# [ ejecución del programa ... ]
# $ pip uninstall version_1 --break-system-packages

setup(
    name="version_1",
    version="1.0.0",
    author="Alberto León Luengo",
    author_email="a.leon.2020@alumnos.urjc.es",
    description="Implementación de un robot por cables para el control de un efector final en diversas tareas.",
    packages=find_packages(),
    install_requires=[
        'numpy>=1.21.0',
        'matplotlib>=3.5.0',
    ],
    entry_points={
        'console_scripts': [
            'run-version1=version_1.cinematic_model_v1:main',
        ],
    },
    python_requires='>=3.6',
)