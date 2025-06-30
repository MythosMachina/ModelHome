# Contributing to MyLora

Thank you for your interest in contributing to **MyLora** – a modular and powerful plugin system designed to simplify LoRA workflows and enhance your AI training experience. We welcome contributions of all kinds, including bug fixes, new features, plugins, documentation improvements, and more!

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Plugin Development Guidelines](#plugin-development-guidelines)
- [Code Style](#code-style)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Need Help?](#need-help)

---

## 🧭 Code of Conduct

All contributors are expected to follow our [Code of Conduct](./CODE_OF_CONDUCT.md) to ensure a welcoming and inclusive environment.

---

## 🚀 Getting Started

1. **Fork** this repository
2. **Clone** your fork locally:
```bash
   git clone https://github.com/your-username/MyLora.git
   cd MyLora
```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your development environment** (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows
   ```

---

## 🛠️ How to Contribute

There are several ways to contribute:

* Reporting bugs or issues
* Suggesting new features
* Improving documentation
* Adding new plugins
* Optimizing or refactoring existing code

Before opening a pull request, **please create an issue** first to discuss your proposal, unless it's a minor fix.

---

## 🔌 Plugin Development Guidelines

MyLora is designed with modularity in mind. To contribute a new plugin:

* Create a new folder under `plugins/your_plugin_name/`
* Include a `plugin.py` entry point with a `register()` function
* Follow the template provided in `plugins/template_plugin/`
* Add a `README.md` inside your plugin folder to explain its purpose and usage
* Avoid hardcoded paths or assumptions – plugins should remain portable and sandbox-friendly

---

## 🧹 Code Style

* Follow [PEP8](https://pep8.org/) style guidelines.
* Use `black` for code formatting:

  ```bash
  black .
  ```
* Use `isort` for import sorting:

  ```bash
  isort .
  ```
* All new functions and classes should include docstrings.

---

## 🧪 Testing

* Make sure your plugin or change doesn’t break existing functionality.
* If applicable, add unit tests under `tests/` using `pytest`.
* To run tests:

  ```bash
  pytest
  ```

---

## 🔄 Pull Request Process

1. Fork and branch from `main`
2. Keep changes focused and minimal
3. Make sure your code is linted and tested
4. Include a clear and descriptive commit message
5. Open a pull request and link any related issues

---

## 🧭 Need Help?

If you have questions, ideas, or need feedback:

* Open an issue
* Join the discussion section
* Or tag `@AsaTyr` in the issue or PR!

Thank you for contributing and making MyLora better! 🧠⚙️
