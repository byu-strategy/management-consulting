#!/bin/bash
# Combines all individual firm JSON files into a single array
# Run automatically by Quarto pre-render or manually after adding firms

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
FIRMS_DIR="$PROJECT_DIR/data/firms"
OUTPUT_FILE="$PROJECT_DIR/data/firms-combined.json"

# Check if firms directory exists
if [ ! -d "$FIRMS_DIR" ]; then
    echo "Creating firms directory..."
    mkdir -p "$FIRMS_DIR"
fi

# Count JSON files (excluding audit files)
JSON_COUNT=$(find "$FIRMS_DIR" -name "*.json" ! -name "*.audit.json" 2>/dev/null | wc -l | tr -d ' ')

if [ "$JSON_COUNT" -eq 0 ]; then
    echo "No firm JSON files found in $FIRMS_DIR"
    echo "[]" > "$OUTPUT_FILE"
    exit 0
fi

echo "Combining $JSON_COUNT firm files..."

# Combine all non-audit JSON files into a single array
# Using a simple approach that works without jq
echo "[" > "$OUTPUT_FILE"

first=true
for file in "$FIRMS_DIR"/*.json; do
    # Skip audit files
    if [[ "$file" == *.audit.json ]]; then
        continue
    fi

    if [ -f "$file" ]; then
        if [ "$first" = true ]; then
            first=false
        else
            echo "," >> "$OUTPUT_FILE"
        fi
        cat "$file" >> "$OUTPUT_FILE"
    fi
done

echo "]" >> "$OUTPUT_FILE"

echo "Created $OUTPUT_FILE with $JSON_COUNT firms"
