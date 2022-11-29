python_requirements(name="reqs")

resources(
    name="res",
    sources=[
        "requirements.txt",
        "dul/**/requirements.txt",
        "dul/scripts/**/*.sh",
    ]
)

python_sources(
    name="lib",
    sources=["dul/**/*.py", "setup.py"],
    dependencies=[":res"],
)

python_tests(name="tests")

python_distribution(
    name="dist",
    dependencies=[":lib"],
    wheel=True,
    sdist=True,
    provides=python_artifact(name="dul"),
    generate_setup=False,
)
