python-alertaclient
===================


ALERTA_CONF_FILE=
ALERTA_DEFAULT_URL=
ALERTA_DEFAULT_PROFILE=production
ALERTA_DEFAULT_OUTPUT=text

0. set defaults
1. read in env vars
2. use CONF_FILE env var to read in config file
3. use DEF_PROFILE env var to get settings
4. override defaults with DEFAULTs if no profile
5. override settings with command-line options

ENV VAR
ALERTA_CONF_FILE
ALERTA_DEFAULT_PROFILE
ALERTA_DEFAULT_ENDPOINT
CLICOLOR

ConfigFile
[profile development]
debug = yes
endpoint = http://sldfja
output = json
color = yes
timezone = Australia/Sydney

Options
--debug
--endpoint-url
--output
--json
--profile
--color


