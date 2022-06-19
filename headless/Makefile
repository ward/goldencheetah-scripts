# Python files that create an html file of the same name
python_files = 5mm.py diary.py distance-histogram.py distancepertime.py rolling-total.py training-log.py
output_files = $(python_files:%.py=output/%.html)

all: $(output_files)

rideDB.json: ~/.goldencheetah/Ward\ Muylaert/cache/rideDB.json
	cp ~/.goldencheetah/Ward\ Muylaert/cache/rideDB.json .

# TODO How to make diary.css a dependency for the diary.py one?

output/%.html: %.py rideDB.json
	python $<

sync: all
	rsync --progress output/*.html vps:/var/www/run.wxm.be/graphs/

clean:
	rm rideDB.json
	rm -r output/
