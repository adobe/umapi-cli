output_dir = dist
ifeq ($(OS),Windows_NT)
	rm_path := $(shell python -c "import distutils.spawn; print(distutils.spawn.find_executable('rm'))")
    ifeq ($(rm_path),None)
        RM := rmdir /S /Q
    else
	    RM := $(rm_path) -rf
    endif
	EXEC = dist/umapi.exe
else
    RM := rm -rf
	EXEC = dist/umapi
endif

VERSION := $(shell poetry version | cut -f2 -d' ')
BDIST := dist/umapi_cli-$(VERSION)-py3-none-any.whl

.PHONY: all
all: $(EXEC) $(BDIST)

$(EXEC): pyproject.toml poetry.lock umapi.spec umapi_cli/*.py
	-$(RM) $(output_dir)
	poetry install
	poetry run pyinstaller --clean --noconfirm umapi.spec

$(BDIST): $(EXEC)
	poetry build
