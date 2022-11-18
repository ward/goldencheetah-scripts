# Python files that create an html file of the same name
python_files = 5mm.py diary.py distance-histogram.py distancepertime.py distanceandtypepertime.py rolling-total.py training-log.py
output_files = $(python_files:%.py=output/%.html)

all: $(output_files)

rideDB.pickle: rideDB.json
	python ridedb_to_pickle.py

rideDB.json: ~/.goldencheetah/Ward\ Muylaert/cache/rideDB.json
	cp ~/.goldencheetah/Ward\ Muylaert/cache/rideDB.json .

output/%.html: %.py rideDB.pickle
	python $<

# This ensures that if a css file with same name as python file exists, the
# python file is considered new and thus needs to be rerun to produce the
# corresponding output file.
%.py: %.css
	touch $@

sync: all
	rsync --progress output/*.html vps:/var/www/run.wxm.be/graphs/

clean:
	rm rideDB.json
	rm rideDB.pickle
	rm -r output/
