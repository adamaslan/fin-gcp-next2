#!/bin/bash

# MCP Finance Development Setup Script
# This script automates the complete development environment setup

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

print_header() {
    echo -e "\n${BLUE}===================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}===================================${NC}\n"
}

# Parse command line arguments
SKIP_INSTALL=false
SKIP_DB=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-install)
            SKIP_INSTALL=true
            shift
            ;;
        --skip-db)
            SKIP_DB=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--skip-install] [--skip-db] [--verbose]"
            exit 1
            ;;
    esac
done

# Main setup function
main() {
    print_header "🚀 MCP Finance Development Setup"

    # Check prerequisites
    check_prerequisites

    # Install dependencies
    if [ "$SKIP_INSTALL" = false ]; then
        install_dependencies
    else
        print_info "Skipping dependency installation"
    fi

    # Setup environment files
    setup_environment_files

    # Setup database
    if [ "$SKIP_DB" = false ]; then
        setup_database
    else
        print_info "Skipping database setup"
    fi

    # Final verification
    verify_setup

    print_header "✅ Setup Complete!"
    show_next_steps
}

# Check if required tools are installed
check_prerequisites() {
    print_header "Checking Prerequisites"

    # Check Node.js
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_success "Node.js installed: $NODE_VERSION"
    else
        print_error "Node.js is not installed"
        print_info "Please install Node.js 18+ from https://nodejs.org/"
        exit 1
    fi

    # Check npm
    if command -v npm &> /dev/null; then
        NPM_VERSION=$(npm --version)
        print_success "npm installed: $NPM_VERSION"
    else
        print_error "npm is not installed"
        exit 1
    fi

    # Check Python (optional but recommended)
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        print_success "Python installed: $PYTHON_VERSION"
    else
        print_warning "Python 3 is not installed - some features may not work"
    fi

    # Check PostgreSQL (optional but recommended)
    if command -v psql &> /dev/null || command -v pg_isready &> /dev/null; then
        print_success "PostgreSQL tools found"
    else
        print_warning "PostgreSQL is not installed - database features will not work"
        print_info "Install PostgreSQL from https://www.postgresql.org/download/"
    fi

    # Check git
    if command -v git &> /dev/null; then
        GIT_VERSION=$(git --version)
        print_success "Git installed: $GIT_VERSION"
    else
        print_warning "Git is not installed"
    fi
}

# Install project dependencies
install_dependencies() {
    print_header "Installing Dependencies"

    # Frontend dependencies
    if [ -d "nextjs-mcp-finance" ]; then
        print_info "Installing frontend dependencies..."
        cd nextjs-mcp-finance
        if [ "$VERBOSE" = true ]; then
            npm install
        else
            npm install --silent > /dev/null 2>&1
        fi
        print_success "Frontend dependencies installed"
        cd ..
    else
        print_warning "Frontend directory not found"
    fi

    # Backend dependencies
    if [ -d "mcp-finance1/cloud-run" ] && [ -f "mcp-finance1/cloud-run/requirements.txt" ]; then
        print_info "Installing backend dependencies..."
        if [ "$VERBOSE" = true ]; then
            pip3 install -r mcp-finance1/cloud-run/requirements.txt
        else
            pip3 install -q -r mcp-finance1/cloud-run/requirements.txt > /dev/null 2>&1
        fi
        print_success "Backend dependencies installed"
    else
        print_warning "Backend requirements.txt not found"
    fi

    # Install Playwright browsers
    if [ -d "nextjs-mcp-finance" ]; then
        print_info "Installing Playwright browsers..."
        cd nextjs-mcp-finance
        if [ "$VERBOSE" = true ]; then
            npx playwright install chromium
        else
            npx playwright install chromium > /dev/null 2>&1
        fi
        print_success "Playwright browsers installed"
        cd ..
    fi
}

# Setup environment configuration files
setup_environment_files() {
    print_header "Setting Up Environment Files"

    # Frontend .env.local
    if [ -d "nextjs-mcp-finance" ]; then
        cd nextjs-mcp-finance
        if [ ! -f ".env.local" ] && [ -f ".env.example" ]; then
            cp .env.example .env.local
            print_success "Created nextjs-mcp-finance/.env.local"
            print_warning "Please update .env.local with your actual configuration"
        elif [ -f ".env.local" ]; then
            print_info ".env.local already exists"
        else
            print_warning ".env.example not found in nextjs-mcp-finance"
        fi
        cd ..
    fi

    # Backend .env
    if [ -d "mcp-finance1" ]; then
        cd mcp-finance1
        if [ ! -f ".env" ] && [ -f ".env.example" ]; then
            cp .env.example .env
            print_success "Created mcp-finance1/.env"
            print_warning "Please update .env with your actual configuration"
        elif [ -f ".env" ]; then
            print_info ".env already exists"
        else
            print_warning ".env.example not found in mcp-finance1"
        fi
        cd ..
    fi

    # Show required environment variables
    print_info "\nRequired Environment Variables:"
    echo "  • DATABASE_URL - PostgreSQL connection string"
    echo "  • NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY - Clerk public key"
    echo "  • CLERK_SECRET_KEY - Clerk secret key"
    echo "  • STRIPE_SECRET_KEY - Stripe secret key"
    echo "  • STRIPE_PUBLISHABLE_KEY - Stripe public key"
}

# Setup and verify database
setup_database() {
    print_header "Setting Up Database"

    # Check if DATABASE_URL is set
    if [ -z "$DATABASE_URL" ]; then
        # Try to load from .env.local
        if [ -f "nextjs-mcp-finance/.env.local" ]; then
            export $(grep -v '^#' nextjs-mcp-finance/.env.local | grep DATABASE_URL | xargs)
        fi
    fi

    if [ -z "$DATABASE_URL" ]; then
        print_warning "DATABASE_URL not set - skipping database setup"
        print_info "Set DATABASE_URL in nextjs-mcp-finance/.env.local to enable database features"
        return
    fi

    # Test database connection
    print_info "Testing database connection..."
    if command -v psql &> /dev/null; then
        if psql "$DATABASE_URL" -c "SELECT 1;" > /dev/null 2>&1; then
            print_success "Database connection successful"
        else
            print_warning "Could not connect to database"
            print_info "Make sure PostgreSQL is running and DATABASE_URL is correct"
            return
        fi
    else
        print_info "PostgreSQL client not found - skipping connection test"
    fi

    # Run migrations (if available)
    if [ -d "nextjs-mcp-finance" ]; then
        cd nextjs-mcp-finance
        print_info "Running database migrations..."

        if npm run db:push > /dev/null 2>&1; then
            print_success "Database migrations completed"
        elif npx drizzle-kit push > /dev/null 2>&1; then
            print_success "Database migrations completed"
        else
            print_warning "Migration command not found or failed"
            print_info "You may need to run migrations manually"
        fi
        cd ..
    fi
}

# Verify the setup is complete and working
verify_setup() {
    print_header "Verifying Setup"

    # Check if frontend can be built (quick check)
    if [ -d "nextjs-mcp-finance" ]; then
        cd nextjs-mcp-finance
        if [ -f "package.json" ]; then
            print_success "Frontend project structure verified"
        fi
        cd ..
    fi

    # Check if backend files exist
    if [ -d "mcp-finance1/cloud-run" ]; then
        print_success "Backend project structure verified"
    fi

    # Check if environment files exist
    ENV_FILES_OK=true
    if [ ! -f "nextjs-mcp-finance/.env.local" ]; then
        print_warning "nextjs-mcp-finance/.env.local not found"
        ENV_FILES_OK=false
    fi
    if [ ! -f "mcp-finance1/.env" ]; then
        print_warning "mcp-finance1/.env not found"
        ENV_FILES_OK=false
    fi

    if [ "$ENV_FILES_OK" = true ]; then
        print_success "Environment files configured"
    fi
}

# Show next steps for the user
show_next_steps() {
    echo ""
    echo "📋 Next Steps:"
    echo ""
    echo "1. Configure your environment variables:"
    echo "   • Edit nextjs-mcp-finance/.env.local"
    echo "   • Edit mcp-finance1/.env"
    echo ""
    echo "2. Start the development servers:"
    echo "   • Frontend: cd nextjs-mcp-finance && npm run dev"
    echo "   • Backend: cd mcp-finance1/cloud-run && python3 main.py"
    echo ""
    echo "3. Access the application:"
    echo "   • Frontend: http://localhost:3000"
    echo "   • Backend API: http://localhost:8000"
    echo ""
    echo "4. Run tests:"
    echo "   • E2E Tests: cd nextjs-mcp-finance && npm run test:e2e"
    echo "   • Or use: /test-all skill"
    echo ""
    echo "5. Useful skills:"
    echo "   • /health-check - Check system status"
    echo "   • /mcp-check - Verify MCP server"
    echo "   • /db-migrate - Run database migrations"
    echo "   • /test-all - Run all tests"
    echo ""
    echo "📚 Documentation:"
    echo "   • Full Guide: GUIDE-ENHANCED.md"
    echo "   • Skills Reference: SKILLS-REFERENCE.md"
    echo "   • Quick Reference: SKILLS-QUICK-REFERENCE.md"
    echo ""
}

# Run the main function
main
