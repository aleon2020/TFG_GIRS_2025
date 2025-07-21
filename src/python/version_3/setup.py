from setuptools import setup, find_packages

# COMPILACIÓN, ENLAZADO Y EJECUCIÓN
# $ cd version_3/
# $ ls
# setup.py  version_3/
# $ pip install -e . --break-system-packages
# $ python3 -m version_3.cinematic_model_v3
# [ ejecución del programa ... ]
# $ pip uninstall version_3 --break-system-packages

setup(
    name="version_3",
    version="3.0.0",
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
            'run-version3=version_3.cinematic_model_v3:main',
        ],
    },
    python_requires='>=3.6',
)