.PHONY: all run

all: pack.tar.uploaded
	ssh root@Robot.local 'tar xf pack.tar'

pack.tar: logo.py repl.py zumoturtle.py carre.logo
	tar c $^ > $@

%.uploaded: %
	scp $< root@Robot.local: && touch $@
