#!/bin/bash

# Script to create a new project directory with template structure

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if project name is provided
if [ $# -eq 0 ]; then
    echo -e "${RED}Error: No project name provided${NC}"
    echo "Usage: ./create-project.sh <project-name>"
    echo "Example: ./create-project.sh my-awesome-app"
    exit 1
fi

PROJECT_NAME="$1"
PROJECT_DIR="$(dirname "$0")/$PROJECT_NAME"

# Check if directory already exists
if [ -d "$PROJECT_DIR" ]; then
    echo -e "${RED}Error: Project directory '$PROJECT_NAME' already exists${NC}"
    exit 1
fi

# Create project directory structure
echo -e "${YELLOW}Creating project: $PROJECT_NAME${NC}"

mkdir -p "$PROJECT_DIR"/{src,docs,tests,scripts}

# Create project README
cat > "$PROJECT_DIR/README.md" << EOF
# $PROJECT_NAME

## Description
[Add project description here]

## Status
🚧 In Development

## Installation
\`\`\`bash
# Add installation instructions here
\`\`\`

## Usage
\`\`\`bash
# Add usage instructions here
\`\`\`

## Project Structure
\`\`\`
$PROJECT_NAME/
├── README.md       # This file
├── src/           # Source code
├── docs/          # Documentation
├── tests/         # Test files
└── scripts/       # Utility scripts
\`\`\`

## Dependencies
- [List dependencies here]

## TODO
- [ ] Initial setup
- [ ] Core functionality
- [ ] Testing
- [ ] Documentation

## Notes
[Add any additional notes here]

---
*Created: $(date +"%Y-%m-%d")*
EOF

# Create a basic .gitkeep in empty directories
touch "$PROJECT_DIR/src/.gitkeep"
touch "$PROJECT_DIR/docs/.gitkeep"  
touch "$PROJECT_DIR/tests/.gitkeep"
touch "$PROJECT_DIR/scripts/.gitkeep"

# Create project-specific .gitignore if needed
cat > "$PROJECT_DIR/.gitignore" << EOF
# Project-specific ignores for $PROJECT_NAME
# Add any project-specific patterns below

EOF

echo -e "${GREEN}✅ Project '$PROJECT_NAME' created successfully!${NC}"
echo -e "${GREEN}📁 Location: $PROJECT_DIR${NC}"
echo ""
echo "Next steps:"
echo "1. cd $PROJECT_NAME"
echo "2. Update the README.md with project details"
echo "3. Start coding in the src/ directory"
echo "4. Update the main repository README to include this project"