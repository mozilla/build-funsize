ZIP_FILE = funsize-$(shell date -u "+%Y-%m-%d-%H-%M").zip

eb:
	-rm -f $(ZIP_FILE)
	git archive --format=zip HEAD > $(ZIP_FILE)
	@echo $(ZIP_FILE) created
