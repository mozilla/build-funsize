ZIP_FILE = /tmp/funsize-$(shell date -u "+%Y-%m-%d-%H-%M").zip

eb:
	-rm -f $(ZIP_FILE)
	zip -r $(ZIP_FILE) --exclude=.git* --exclude=.tox* --exclude=.rope*  --exclude=tests* .
	@echo $(ZIP_FILE) created
