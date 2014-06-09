MANAGE = ./manage.py


.PHONY: run
run:
	$(MANAGE) runserver

.PHONY: bower_update
bower_update:
	$(MANAGE) bower update
	$(MANAGE) collectstatic

.PHONY: write_requirements
write_requirements:
	pip freeze > etc/requirements.txt

.PHONY: resetdb_test
resetdb_test:
	rm -f db/db.sqlite3
	rm -fr db/control.leveldb
	$(MANAGE) syncdb
	$(MANAGE) loaddata etc/users.json
	$(MANAGE) loaddata quiz/fixtures/init_fixture.json
