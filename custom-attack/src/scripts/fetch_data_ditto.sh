#!/bin/sh
curl -s administrator:secret@%s/api/2/search/things | curl -X POST -H 'Content-Type: application/json' -d @- %s:%s/data_ditto