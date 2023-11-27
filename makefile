VERSION		:= $(shell python versioninfo.py)
OUTPUT_DIR	:= WP-TT-v$(VERSION)
OUTPUT_FILE	:= WP-TT-v$(VERSION).exe

TKINTER_FLAGS 	:= --enable-plugin=tk-inter --nofollow-import-to=unittest --disable-console
OUTPUT_FLAGS	:= -o $(OUTPUT_FILE) --output-dir=$(OUTPUT_DIR)

all:
	python -m nuitka --standalone $(TKINTER_FLAGS) WP-TT.py $(OUTPUT_FLAGS) --onefile