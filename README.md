# 🧪 Robot Framework Project Generator

This is a CLI tool to auto-generate a complete Robot Framework test suite with optional support for custom Python libraries and resource files.

It’s ideal for quickly scaffolding example suites for experimentation, learning, demos, or automation pipelines.

## 📦 Features

- Creates a directory with:
  - A sample `.robot` test suite
  - Optional Python keyword library
  - Optional `.robot` resource file
- Includes example test cases using:
  - Local keywords
  - Python-based custom library keywords
  - Resource file keywords (including embedded arguments)
- CLI flags for customization
- Can optionally run the suite and open the result log

---

## 🚀 Installation

Make sure you have Python 3.7+ and [Robot Framework](https://robotframework.org/) 6.0+ installed. Unit tests are implemented with pytest.

```bash
pip install robotframework click pytest
````

Clone this repo:

```bash
git clone https://github.com/tjpaakkunainen/robot-project-generator.git
cd robot-project-generator
```

---

## ⚙️ Usage

```bash
python robot_generator.py [OPTIONS]
```

### Options

| Option            | Description                                                           |
| ----------------- | --------------------------------------------------------------------- |
| `--project-dir`   | Output directory for the generated project (default: `robot_project`) |
| `--suite-name`    | Name of the test suite file (default: `MySuite.robot`)                |
| `--run`           | Run the test suite after generation                                   |
| `--open-log`      | Automatically open the log after running                              |
| `--dry-run`       | Do not write any files — just show what would happen                  |
| `--with-lib`      | Include a custom Python library (`libraries/MyLibrary.py`)            |
| `--with-resource` | Include a `.robot` resource file (`resources/MyResource.robot`)       |

---

## 🧰 Example

Create a full project with both a library and resource, and run it:

```bash
python robot_generator.py --with-lib --with-resource --run --open-log
```

---

## 📁 Project Structure

If you include both library and resource, and run the test suite, the generated layout will look like this:

```
robot_project/
├── tests/
│   └── MySuite.robot
├── libraries/
│   └── MyLibrary.py
├── resources/
│   └── MyResource.robot
└── results/
    ├── log.html
    ├── output.xml
    └── report.html
```

---

## 🧪 Dependencies

* [Robot Framework](https://robotframework.org/)
* [Click](https://click.palletsprojects.com/)
* [Pytest](https://pytest.org)

---
