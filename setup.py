"""."""
from setuptools import setup


setup(
    name="celery-flask",
    version="0.0.1",
    py_modules=['tasks', 'root', 'views'],
    package_dir={'': 'src'}
)
