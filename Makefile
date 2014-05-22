
.PHONY: run
run:
	bin/startserver.sh

.PHONY: bower_update
bower_update:
	./manage.py bower update
	./manage.py collectstatic

.PHONY: write_requirements
write_requirements:
	pip freeze > requirements.txt
