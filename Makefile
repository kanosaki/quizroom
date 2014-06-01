MANAGE = ./manage.py


.PHONY: run
run:
	bin/startserver.sh

.PHONY: bower_update
bower_update:
	$(MANAGE) bower update
	$(MANAGE) collectstatic

.PHONY: write_requirements
write_requirements:
	pip freeze > etc/requirements.txt

.PHONY: resetdb
resetdb:
	$(MANAGE) dumpdata auth.User --indent 4 > etc/users.json
	rm db.sqlite3
	$(MANAGE) syncdb
	$(MANAGE) loaddata etc/users.json
