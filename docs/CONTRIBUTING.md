# Contributing to Wealth

Thank you for your interest in contributing to Wealth! This document provides guidelines and instructions for contributing to this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

**Encouraged Behavior**:
- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable Behavior**:
- The use of sexualized language or imagery and unwelcome sexual attention or advances
- Trolling, insulting/derogatory comments, and personal or political attacks
- Public or private harassment
- Publishing others' private information without explicit permission
- Other conduct which could reasonably be considered inappropriate in a professional setting

### Our Responsibilities

Project maintainers are responsible for clarifying the standards of acceptable behavior and are expected to take appropriate and fair corrective action in response to any instances of unacceptable behavior.

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.10 or higher
- Node.js 18 or higher
- Git

### Fork the Repository

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/wealth.git
   cd wealth
   ```

3. Add the original repository as upstream:
   ```bash
   git remote add upstream https://github.com/badhope/wealth.git
   ```

## Development Setup

### Backend Setup

```bash
cd wealth

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import wealth; print('Wealth installed successfully')"
```

### Frontend Setup

```bash
cd wealth/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Running Tests

```bash
# Backend tests
cd wealth/scripts
python simulation_test.py

# Frontend build test
cd wealth/frontend
npm run build
```

## Making Changes

### Branch Naming Convention

Use the following prefixes for your branches:

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions/changes
- `hotfix/` - Urgent fixes

**Examples**:
```
feature/add-new-strategy
fix/resolving-rate-limit-issue
docs/update-api-documentation
refactor/improve-data-validation
```

### Coding Standards

#### Python (Backend)

- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Write docstrings for all public functions and classes
- Keep functions focused and small (ideally under 50 lines)

```python
def calculate_indicators(symbol: str, period: str) -> Dict[str, Any]:
    """
    Calculate technical indicators for a given symbol.

    Args:
        symbol: Stock symbol to analyze
        period: Time period for calculation

    Returns:
        Dictionary containing calculated indicators
    """
    pass
```

#### JavaScript/Vue (Frontend)

- Use ES6+ features
- Follow Vue 3 Composition API patterns
- Use `<script setup>` syntax for Vue components
- Prop validation with type checking

```javascript
const props = defineProps({
  title: {
    type: String,
    required: true
  },
  count: {
    type: Number,
    default: 0
  }
})
```

#### CSS/Sass

- Use CSS custom properties (variables) from the design system
- Follow BEM naming convention for custom styles
- Keep styles modular and scoped

### Commit Message Guidelines

Follow the Conventional Commits specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests
- `chore`: Changes to the build process or auxiliary tools

**Examples**:
```
feat(api): add new prediction endpoint
fix(ui): resolve chart rendering issue
docs(readme): update installation instructions
refactor(engine): improve backtest performance
```

## Submitting Changes

### Pull Request Process

1. **Update Documentation**
   - Update relevant documentation for any changed functionality
   - Add comments for complex code sections

2. **Run Tests**
   - Ensure all tests pass locally
   - Add tests for new functionality

3. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat(scope): description of changes"
   ```

4. **Sync with Upstream**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

5. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create Pull Request**
   - Go to the original repository on GitHub
   - Click "New Pull Request"
   - Select your branch
   - Fill in the PR template:
     - Description of changes
     - Related issue number (if applicable)
     - Testing performed
     - Screenshots (for UI changes)

### PR Template

```markdown
## Description
<!-- Briefly describe the changes made -->

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Code refactor

## Related Issues
<!-- Link any related issues using 'Fixes #issue_number' -->

## Testing
<!-- Describe testing performed -->

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests pass
```

## Reporting Issues

### Issue Template

```markdown
**Description**
<!-- A clear description of the issue -->

**Steps to Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
<!-- What you expected to happen -->

**Actual Behavior**
<!-- What actually happened -->

**Environment**
- OS: [e.g., Windows 11]
- Python version: [e.g., 3.10.0]
- Browser: [e.g., Chrome]

**Additional Context**
<!-- Any other context about the problem -->
```

### Security Issues

For security vulnerabilities, please email directly instead of posting publicly. Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

## Questions?

Feel free to:
- Open an issue for questions
- Join project discussions
- Contact maintainers directly

Thank you for contributing to Wealth!
