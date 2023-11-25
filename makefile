VERSION		:= $(shell python versioninfo.py)
OUTPUT_FILE	:= WP-TT-v$(VERSION).exe

TKINTER_OPTIONS := --enable-plugin=tk-inter --nofollow-import-to=unittest --disable-console

all:
	python -m nuitka --standalone --onefile $(TKINTER_OPTIONS) WP-TT.py -o $(OUTPUT_FILE)