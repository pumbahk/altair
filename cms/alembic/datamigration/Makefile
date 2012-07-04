INIFILE ?= "../../development.ini"
SCRIPTS = 152b9d4cf2a4_insert_initial_roles.py\
		45e4046d6963_insert_site_client_d.py\
		a47ddbeb352_insert_default_layou.py\
		1dce352cb9f3_insert_category_top_.py

upgrade_base:
	@echo -------------------------migration upgrade-------------------
	python ./run.py --action=upgrade ${INIFILE} ${SCRIPTS}

downgrade_base:
	@echo -------------------------migration downgrade-------------------
	python ./run.py --action=downgrade ${INIFILE} $(shell echo "${SCRIPTS}" | sed 's/[ \t][ \t]*/\n/g' | tac)


