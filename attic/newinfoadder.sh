# this is a pure sh script which takes a json file, extracts two fields
# and puts them in a sqlite database

# it doesnt do the watching but is called by a watcher script
# which is triggered when a new file is added to the directory
# the watcher script is newinfohandler.sh

# this guy here knows how to add the info to the database

#!/bin/sh
#  the command we want to run   

#!/bin/sh

# Define the SQLite database file
DB_FILE="database.sqlite"

# Define the XML file to process
XML_FILE="$1"

# Extract fields from the XML file using xmllint
FIELD1=$(xmllint --xpath 'string(//field1)' "$XML_FILE")
FIELD2=$(xmllint --xpath 'string(//field2)' "$XML_FILE")

# Insert the extracted fields into the SQLite database
sqlite3 "$DB_FILE" <<EOF
INSERT INTO your_table_name (column1, column2)
VALUES ('$FIELD1', '$FIELD2');
EOF

echo "Record added to the database."

