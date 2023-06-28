output_dir = dist
ifeq ($(OS),Windows_NT)
	rm_path := $(shell python -c "import distutils.spawn; print(distutils.spawn.find_executable('rm'))")
    ifeq ($(rm_path),None)
        RM := rmdir /S /Q
    else
	    RM := $(rm_path) -rf
    endif
	TARGET = dist/umapi.exe
else
    RM := rm -rf
	TARGET = dist/umapi
endif

$(TARGET): pyproject.toml poetry.lock umapi.spec umapi_cli/*.py
	-$(RM) $(output_dir)
	poetry install
	poetry run pyinstaller --clean --noconfirm umapi.spec
