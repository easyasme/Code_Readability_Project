import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="face_recognition_deepface",
    version="0.0.0",
    author="XYZ",
    author_email="loni@gmail.com",
    description="A Lightweight Face Recognition and Facial Attribute Analysis Framework (Age, Gender, Emotion, Race) for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    entry_points={
        "console_scripts":
        ["deepface = deepface.DeepFace:cli"],
    },
    package_data={'': ['age_model_weights.h5', 'face_recognition_sface_2021dec.onnx', 'facenet_weights.h5', 'facenet512_weights.h5', 'gender_model_weights.h5', 'vgg_face_weights.h5']},
    include_package_data=True,
    python_requires='>=3.5.5',
    install_requires=["numpy>=1.14.0", "pandas>=0.23.4", "Pillow>=5.2.0", "tqdm>=4.30.0", "opencv-python>=4.5.5.64", "tensorflow>=1.9.0", "keras>=2.2.0", "mtcnn>=0.1.0", "fire>=0.4.0"]
)
