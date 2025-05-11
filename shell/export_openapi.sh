#!/bin/bash
PYTHON=".venv/bin/python"

mkdir -p tmp/datamodel
rm -f "tmp/datamodel/*.json"

$PYTHON - >tmp/datamodel/RSSItem.json <<EOF
from backend.models import RSSItem
import json
print(json.dumps(RSSItem.model_json_schema(indent=2)))
EOF