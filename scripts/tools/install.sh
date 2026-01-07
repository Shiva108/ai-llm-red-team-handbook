#!/bin/bash
#
# AI LLM Red Team Handbook - Installation Script
# 
# This script sets up the environment for running the handbook's practical scripts.
# It creates a virtual environment, installs dependencies, and configures the tools.
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$PARENT_DIR/venv"

# Print functions
print_header() {
    echo -e "${BLUE}=========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}=========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Main installation process
main() {
    print_header "AI LLM Red Team Handbook - Installation"
    
    echo ""
    print_info "Installation directory: $SCRIPT_DIR"
    echo ""
    
    # Step 1: Check Python installation
    print_header "Step 1: Checking Python Installation"
    
    if ! command_exists python3; then
        print_error "Python 3 is not installed!"
        echo "Please install Python 3.8 or higher and try again."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python 3 found: $PYTHON_VERSION"
    
    # Check if Python version is 3.8+
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
        print_error "Python 3.8+ is required (found $PYTHON_VERSION)"
        exit 1
    fi
    
    # Step 2: Create virtual environment
    print_header "Step 2: Creating Virtual Environment"
    
    if [ -d "$VENV_DIR" ]; then
        print_warning "Virtual environment already exists at: $VENV_DIR"
        read -p "Do you want to recreate it? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "Removing existing virtual environment..."
            rm -rf "$VENV_DIR"
        else
            print_info "Using existing virtual environment"
        fi
    fi
    
    if [ ! -d "$VENV_DIR" ]; then
        print_info "Creating virtual environment in: $VENV_DIR"
        python3 -m venv "$VENV_DIR"
        print_success "Virtual environment created"
    fi
    
    # Step 3: Activate virtual environment
    print_header "Step 3: Activating Virtual Environment"
    
    source "$VENV_DIR/bin/activate"
    print_success "Virtual environment activated"
    
    # Upgrade pip
    print_info "Upgrading pip..."
    pip install --quiet --upgrade pip
    print_success "pip upgraded"
    
    # Step 4: Install Python dependencies
    print_header "Step 4: Installing Python Dependencies"
    
    if [ -f "$PARENT_DIR/config/requirements.txt" ]; then
        print_info "Installing packages from requirements.txt..."
        pip install --quiet -r "$PARENT_DIR/config/requirements.txt"
        print_success "Python dependencies installed"
    else
        print_warning "requirements.txt not found, skipping dependency installation"
    fi
    
    # Step 5: Make scripts executable
    print_header "Step 5: Making Scripts Executable"
    
    print_info "Setting executable permissions on scripts..."
    
    # Make all Python scripts executable
    find "$PARENT_DIR" -type f -name "*.py" -exec chmod +x {} \;
    
    # Make all shell scripts executable
    find "$PARENT_DIR" -type f -name "*.sh" -exec chmod +x {} \;
    
    print_success "Scripts are now executable"
    
    # Step 6: Verify installation
    print_header "Step 6: Verifying Installation"
    
    # Check if key packages are installed
    PACKAGES=("transformers" "tiktoken" "requests")
    ALL_INSTALLED=true
    
    for pkg in "${PACKAGES[@]}"; do
        if python -c "import $pkg" 2>/dev/null; then
            print_success "$pkg installed"
        else
            print_warning "$pkg not installed (optional)"
            ALL_INSTALLED=false
        fi
    done
    
    # Step 7: Create activation helper script
    print_header "Step 7: Creating Helper Scripts"
    
    # Create activate script
    cat > "$SCRIPT_DIR/activate.sh" << 'EOF'
#!/bin/bash
# Activate the virtual environment for AI LLM Red Team scripts

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$SCRIPT_DIR/venv/bin/activate"

echo "Virtual environment activated!"
echo "You can now run scripts from: $SCRIPT_DIR"
echo ""
echo "Examples:"
echo "  python3 workflows/full_assessment.py --help"
echo "  python3 prompt_injection/chapter_14_prompt_injection_01_prompt_injection.py"
echo ""
echo "To deactivate, run: deactivate"
EOF
    chmod +x "$SCRIPT_DIR/activate.sh"
    print_success "Created activate.sh helper script"
    
    # Create quick test script
    cat > "$SCRIPT_DIR/test_install.py" << 'EOF'
#!/usr/bin/env python3
"""Quick installation test script."""

import sys

def test_imports():
    """Test if key packages can be imported."""
    packages = {
        'argparse': 'Standard library',
        'json': 'Standard library',
        'pathlib': 'Standard library',
    }
    
    optional_packages = {
        'transformers': 'HuggingFace Transformers',
        'tiktoken': 'OpenAI Tokenization',
        'requests': 'HTTP library',
    }
    
    print("Testing required imports...")
    for pkg, desc in packages.items():
        try:
            __import__(pkg)
            print(f"✓ {pkg:20s} - {desc}")
        except ImportError:
            print(f"✗ {pkg:20s} - MISSING!")
            return False
    
    print("\nTesting optional imports...")
    for pkg, desc in optional_packages.items():
        try:
            __import__(pkg)
            print(f"✓ {pkg:20s} - {desc}")
        except ImportError:
            print(f"⚠ {pkg:20s} - Not installed (optional)")
    
    return True

if __name__ == '__main__':
    print("AI LLM Red Team Handbook - Installation Test\n")
    
    if test_imports():
        print("\n✓ Installation test passed!")
        sys.exit(0)
    else:
        print("\n✗ Installation test failed!")
        sys.exit(1)
EOF
    chmod +x "$SCRIPT_DIR/test_install.py"
    print_success "Created test_install.py verification script"
    
    # Step 8: Final summary
    print_header "Installation Complete!"
    
    echo ""
    print_success "All components installed successfully!"
    echo ""
    print_info "Next steps:"
    echo "  1. Activate the virtual environment:"
    echo "     ${BLUE}source $SCRIPT_DIR/activate.sh${NC}"
    echo ""
    echo "  2. Or manually activate:"
    echo "     ${BLUE}source $VENV_DIR/bin/activate${NC}"
    echo ""
    echo "  3. Test the installation:"
    echo "     ${BLUE}python3 test_install.py${NC}"
    echo ""
    echo "  4. Run a sample script:"
    echo "     ${BLUE}python3 workflows/full_assessment.py --help${NC}"
    echo ""
    echo "  5. Read the documentation:"
    echo "     ${BLUE}cat README.md${NC}"
    echo ""
    
    # Run quick test
    print_info "Running quick installation test..."
    if python3 "$SCRIPT_DIR/test_install.py"; then
        echo ""
        print_success "Environment is ready to use!"
    else
        echo ""
        print_warning "Some optional packages are missing, but core functionality works"
    fi
    
    echo ""
    print_header "Installation Log"
    echo "Python version: $PYTHON_VERSION"
    echo "Virtual env: $VENV_DIR"
    echo "Script count: $(find "$PARENT_DIR" -name "*.py" -type f | wc -l) Python scripts"
    echo "Script count: $(find "$PARENT_DIR" -name "*.sh" -type f | wc -l) Shell scripts"
    echo ""
    
    print_success "Setup complete! Happy red teaming! 🔴"
}

# Run main installation
main "$@"
