from setuptools import setup, find_packages

# COMPILACIÓN, ENLAZADO Y EJECUCIÓN
# $ cd version_2/
# $ ls
# setup.py  version_2/
# $ pip install -e . --break-system-packages
# $ python3 -m version_2.cinematic_model_v2
# [ ejecución del programa ... ]
# $ pip uninstall version_2 --break-system-packages

setup(
    name="version_2",
    version="2.0.0",
    description="Implementación de un robot por cables para el control de un efector final en diversas tareas.",
    author="Alberto León Luengo",
    author_email="a.leon.2020@alumnos.urjc.es",
    packages=find_packages(),
    install_requires=[
        'numpy>=1.21.0',
        'matplotlib>=3.5.0',
    ],
    entry_points={
        'console_scripts': [
            'run-version2=version_2.cinematic_model_v2:main',
        ],
    },
    python_requires='>=3.6',
)