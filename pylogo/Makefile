.PHONY: all run

all: pack.tar.uploaded
run: all
	ssh root@Robot.local 'tar xf pack.tar && python repl.py carre.logo'

pack.tar: logo.py repl.py zumoturtle.py carre.logo
	tar c $^ > $@

%.uploaded: %
	scp $< root@Robot.local: && touch $@
