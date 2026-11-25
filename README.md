<div align=center>
  <img src="assets/images/banner.png" alt="EverSmooth Optimized Banner" width="100%">

  <br>

  # EverSmooth Optimized

  ### A smoother Minecraft experience.

  A performance-focused Minecraft modpack designed to improve game performance, enhance visual presentation, and provide useful quality-of-life improvements while preserving the familiar Minecraft experience.

  <br>

  [![Support and Contribute][img-sac]](CONTRIBUTING.md)
  [![Read the Wiki][img-rtw]](https://eversmooth-optimized-wiki.vercel.app)

  <br>

  [![Mod List][img-mods]](content/mods.md)
  [![Resource Packs][img-rp]](content/resourcepacks.md)
  [![Shaders][img-shaders]](content/shaders.md)

  <br>

  [![GitHub][img-github]](https://github.com/reysokree/eversmooth-optimized)
  [![Installation Guide][img-installation]](https://eversmooth-optimized-wiki.vercel.app)

  <br>
</div>

---

## Table of Contents

- [Overview](#overview)
- [Project Information](#project-information)
- [Features](#features)
- [Performance and Experience](#performance-and-experience)
- [Included Content](#included-content)
- [Compatibility](#compatibility)
- [Downloads](#downloads)
- [Installation](#installation)
- [Manual Installation](#manual-installation)
- [Building from Source](#building-from-source)
- [Project Tools](#project-tools)
- [Release Management](#release-management)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [Credits and Acknowledgements](#credits-and-acknowledgements)
- [License](#license)

---

## Overview

**EverSmooth Optimized** is a Minecraft modpack focused on improving the overall gameplay experience through carefully selected performance modifications, quality-of-life enhancements, and visual improvements.

The project aims to provide a smoother and more convenient Minecraft experience without unnecessarily changing the familiar gameplay mechanics.

Beyond the modpack itself, EverSmooth Optimized also maintains an organized development environment built around **Packwiz** and custom **Python automation tools**.

These tools help manage project metadata, maintain release information, validate configurations, generate reports, compare releases, and automate various development tasks.

Whether you're looking for a smoother Minecraft experience or exploring how the modpack is maintained, EverSmooth Optimized provides an organized and maintainable project.

## Project Information

| Information | Details |
|:---|:---|
| **Project Name** | EverSmooth Optimized |
| **Project Type** | Minecraft Modpack |
| **Minecraft Version** | 1.16.5 |
| **Mod Loader** | Fabric |
| **Current Release** | `0.1.0-alpha.1` |
| **Pack Management** | Packwiz |
| **Automation** | Python |
| **Maintainer** | [ReysoKree](https://github.com/ReysoKree) |
| **Documentation** | [EverSmooth Optimized Wiki](https://eversmooth-optimized-wiki.vercel.app) |
| **License** | [Custom License (ARR)](LICENSE) |

## Features

EverSmooth Optimized combines several aspects of Minecraft modpack development and gameplay enhancement.

### Gameplay and Performance

- Performance-focused modifications.
- Quality-of-life enhancements.
- Carefully selected resource packs.
- Optional shader configurations.
- Organized modpack content.
- A familiar Minecraft gameplay experience.

### Project Management

- Packwiz-based modpack management.
- Structured source files and metadata.
- Python-based project management and automation.
- Release metadata validation and synchronization.
- Release comparison and information generation.
- Automated reports and changelog generation.
- Project backup management.
- Multiple distribution and installation options.

## Performance and Experience

EverSmooth Optimized aims to improve the Minecraft experience through a carefully selected collection of modifications.

The project focuses on three main areas:

| Area | Purpose |
|:---|:---|
| **Performance** | Improve game performance through selected optimization modifications. |
| **Quality of Life** | Introduce useful gameplay improvements and conveniences. |
| **Visual Experience** | Provide optional visual enhancements through resource packs and shaders. |

The included modifications and visual content are documented separately to make the pack easier to explore and maintain.

## Included Content

Explore the content included in EverSmooth Optimized.

| Category | Description | Documentation |
|:---|:---|:---|
| **Mods** | Performance and quality-of-life modifications. | [View Mods](content/mods.md) |
| **Resource Packs** | Selected resource packs for visual enhancements. | [View Resource Packs](content/resourcepacks.md) |
| **Shaders** | Optional shader configurations. | [View Shaders](content/shaders.md) |

Each documentation file provides information about its respective content.

## Compatibility

EverSmooth Optimized is developed for the following Minecraft environment:

| Component | Version |
|:---|:---|
| Minecraft | `1.16.5` |
| Mod Loader | Fabric |
| Pack Management | Packwiz |

**Important:** Use a compatible Minecraft launcher and the required Fabric Loader configuration when installing the modpack.

Compatibility with other Minecraft versions or mod loaders should not be assumed unless explicitly supported by a published release.

## Downloads

EverSmooth Optimized supports multiple distribution methods.

### Available Distribution Platforms

| Platform | Description |
|:---|:---|
| **Modrinth** | Download the modpack through Modrinth. |
| **CurseForge** | Download the modpack through CurseForge. |
| **Handloom (Manual)** | Download the Handloom export for mual installation. |
| **GitHub Releases** | Access published release archives and release information. |

### Download Options

Choose the distribution method that works best for your Minecraft launcher.

- **Modrinth:** Recommended when using a compatible Modrinth-supported launcher.
- **CurseForge:** Use the CurseForge distribution with a compatible launcher.
- **Handloom (Manual):** Download the Handloom export for manual installation.
- **GitHub Releases:** Download the available release archive directly.
- **Source Repository:** Build a fresh modpack export using the included project files and automation tools.

---

## Installation

Follow the appropriate installation method for your chosen distribution.

### 1. Modrinth

1. Visit the EverSmooth Optimized Modrinth project page.
2. Select the release you want.
3. Download the modpack.
4. Import it into a compatible Minecraft launcher.
5. Launch the game.

### 2. CurseForge

1. Visit the EverSmooth Optimized CurseForge project page.
2. Download the available modpack release.
3. Import the downloaded profile into a compatible launcher.
4. Verify the Minecraft and Fabric Loader configuration.
5. Launch Minecraft.

### 3. GitHub Releases

1. Open the repository's Releases section.
2. Select the desired release.
3. Download the appropriate release archive.
4. Extract or import the archive according to its distribution format.
5. Follow the included installation information.

---

## Manual Installation

EverSmooth Optimized also provides a Handloom export for manual installation.

The export organizes the available content into its respective directories, including:

- `mods/` — Minecraft modifications.
- `resourcepacks/` — Resource packs.
- `shaders/` — Shaders.

To install manually:

1. Obtain the appropriate Handloom export.
2. Locate your Minecraft installation directory.
3. Place the exported files into their corresponding directories.
4. Verify that the required Minecraft version and Fabric Loader are configured.
5. Launch Minecraft.

Make sure you use the correct export for the intended Minecraft environment.

## Building from Source

EverSmooth Optimized uses **Packwiz** as its primary modpack management system.

The repository includes the source files required to maintain and export the modpack.

Developers who want to work with the project can:

1. Clone the repository.
2. Set up the required development environment.
3. Explore the Packwiz source files.
4. Review the project metadata.
5. Use the included automation scripts.
6. Generate a fresh modpack export.

### Requirements

| Requirement | Purpose |
|:---|:---|
| Python | Project automation and management tools. |
| Packwiz | Modpack source management and exporting. |
| Java | Minecraft development and runtime environment. |
| Git | Repository cloning and version control. |

The exact requirements can depend on the operation being performed.

---

## Project Tools

EverSmooth Optimized includes a collection of custom Python scripts designed to simplify project management and release maintenance.

Rather than manually performing every maintenance operation, developers can use the interactive project menu to access the available tools.

### Launching the Project Menu

Run the following command from the repository root:

```powershell
python scripts/menu.py
```

The interactive menu provides access to the available project, release, maintenance, and information utilities.

### Tool Capabilities

The project automation system covers several development tasks:

| Category | Capabilities |
|:---|:---|
| **Project Management** | Project inspection and maintenance. |
| **Validation** | Metadata and project structure validation. |
| **Modpack Export** | Generate modpack distribution archives. |
| **Release Management** | Manage and compare releases. |
| **Changelog** | Generate release changelogs. |
| **Reports** | Generate release and project reports. |
| **Backups** | Create project backup archives. |
| **Metadata** | Export and synchronize release information. |

These utilities help maintain consistency throughout the development and release process.

---

## Release Management

EverSmooth Optimized follows a structured release management approach.

Each release maintains its own version information and associated documentation.

### Release Information

Release metadata is maintained separately from the main project description.

The project uses versioned information to help organize:

- Minecraft version information.
- Mod Loader configuration.
- Modpack release versions.
- Release-specific metadata.
- Generated distribution archives.
- Release reports and changelogs.

### Release Naming Convention

Release archives follow the project's structured naming convention:

```text
ESO+<Minecraft-Version>+Fabric-<Fabric-Loader-Version>+<Modpack-Version>
```

Example:

```text
ESO+1.16.5+0.20.1+0.1.0-alpha.1
```

This naming format makes the Minecraft version, Fabric Loader version, and modpack release version identifiable directly from the archive name.

---

## Project Structure

The repository is organized to separate source files, project automation, distribution files, generated documentation, and release information.

```text
eversmooth-optimized/
│
├── assets/
│   └── images/              # Project branding and visual assets
│
├── backups/                 # Complete project backup archives
│
├── content/                 # Included modpack content
│   ├── mods.md
│   ├── resourcepacks.md
│   └── shaders.md
│
├── metadata-exports/        # Exported metadata documents
│
├── packwiz/                 # Packwiz source files
│
├── platforms/               # Platform-specific distributions
│
├── releases/                # Generated release archives
│
├── reports/                 # Generated release reports
│
├── scripts/                 # Python automation tools
│
├── versions/                # Release-specific information
│
├── .github/                 # GitHub configuration and workflows
│
├── .vscode/                 # VS Code configuration
│
├── CHANGELOG.md
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
└── modpack-info.json
```

*The structure above represents the main project organization.*

---

## Documentation

Additional project documentation is available through the following resources.

| Resource | Description |
|:---|:---|
| **Wiki** | Project information and documentation. |
| **Mod List** | Details of included modifications. |
| **Resource Packs** | Information about included resource packs. |
| **Shaders** | Details of optional shader configurations. |
| **Changelog** | Release history and project changes. |
| **Contributing Guide** | Guidelines for contributing to the project. |

- [EverSmooth Optimized Wiki](https://eversmooth-optimized-wiki.vercel.app)
- [Mod Documentation](content/mods.md)
- [Resource Pack Documentation](content/resourcepacks.md)
- [Shader Documentation](content/shaders.md)
- [Changelog](CHANGELOG.md)

---

## Contributing

Contributions, suggestions, improvements, and bug reports are welcome.

If you would like to contribute to EverSmooth Optimized:

1. Review the existing project documentation.
2. Read the contribution guidelines.
3. Follow the repository's contribution workflow.
4. Provide clear information about your proposed changes.

Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting contributions.

## Credits and Acknowledgements

EverSmooth Optimized is made possible by the developers and maintainers of the Minecraft modding ecosystem.

Special appreciation goes to:

- **Fabric** and its developers for the modding ecosystem.
- **Packwiz** for providing modpack management and export functionality.
- **Minecraft mod developers** for creating the modifications used in the project.
- **Resource pack creators** for their visual contributions.
- **Shader developers** for their work on visual enhancements.
- **Open-source contributors** who build and maintain useful development tools.

All third-party modifications, resource packs, shaders, and other included resources remain subject to their respective licenses and distribution terms.

## License

EverSmooth Optimized is distributed under its custom project license.

Please review the [LICENSE](LICENSE) file before using, modifying, or redistributing project materials.

Third-party modifications, resource packs, shaders, libraries, and other included resources remain subject to their respective licenses.

---

<div align="center">

<img src="assets/images/logo.png" alt="EverSmooth Optimized" width="64">

### EverSmooth Optimized

**A smoother Minecraft experience.**

Made with care for the Minecraft community.

<br>

[![Maintained by ReysoKree][img-maintainer]](https://github.com/ReysoKree)
![Minecraft][img-minecraft]
![Fabric][img-loader]

</div>


<!-- Metadata -->

[img-sac]: <https://img.shields.io/badge/Support_and_Contribute-181717?style=for-the-badge&logo=github&logoColor=white>
[img-rtw]: <https://img.shields.io/badge/Read_the_Wiki-5865F2?style=for-the-badge&logo=gitbook&logoColor=white>

[img-mods]:<https://img.shields.io/badge/Mod_list-darkgreen?style=for-the-badge&logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgLTk2MCA5NjAgOTYwIiB3aWR0aD0iMjQiPjxwYXRoIGQ9Ik0yODAtNjAwdi04MGg1NjB2ODBIMjgwWm0wIDE2MHYtODBoNTYwdjgwSDI4MFptMCAxNjB2LTgwaDU2MHY4MEgyODBaTTE2MC02MDBxLTE3IDAtMjguNS0xMS41VDEyMC02NDBxMC0xNyAxMS41LTI4LjVUMTYwLTY4MHExNyAwIDI4LjUgMTEuNVQyMDAtNjQwcTAgMTctMTEuNSAyOC41VDE2MC02MDBabTAgMTYwcS0xNyAwLTI4LjUtMTEuNVQxMjAtNDgwcTAtMTcgMTEuNS0yOC41VDE2MC01MjBxMTcgMCAyOC41IDExLjVUMjAwLTQ4MHEwIDE3LTExLjUgMjguNVQxNjAtNDQwWm0wIDE2MHEtMTcgMC0yOC41LTExLjVUMTIwLTMyMHEwLTE3IDExLjUtMjguNVQxNjAtMzYwcTE3IDAgMjguNSAxMS41VDIwMC0zMjBxMCAxNy0xMS41IDI4LjVUMTYwLTI4MFoiIGZpbGw9IiNmZmZmZmYiLz48L3N2Zz4%3D>
[img-rp]: <https://img.shields.io/badge/Resource_Packs-purple?style=for-the-badge&logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgLTk2MCA5NjAgOTYwIiB3aWR0aD0iMjQiPjxwYXRoIGQ9Im0zNTItNTIyIDg2LTg3LTU2LTU3LTQ0IDQ0LTU2LTU2IDQzLTQ0LTQ1LTQ1LTg3IDg3IDE1OSAxNThabTMyOCAzMjkgODctODctNDUtNDUtNDQgNDMtNTYtNTYgNDMtNDQtNTctNTYtODYgODYgMTU4IDE1OVptMjQtNTY3IDU3IDU3LTU3LTU3Wk0yOTAtMTIwSDEyMHYtMTcwbDE3NS0xNzVMODAtNjgwbDIwMC0yMDAgMjE2IDIxNiAxNTEtMTUycTEyLTEyIDI3LTE4dDMxLTZxMTYgMCAzMSA2dDI3IDE4bDUzIDU0cTEyIDEyIDE4IDI3dDYgMzFxMCAxNi02IDMwLjVUODE2LTY0N0w2NjUtNDk1bDIxNSAyMTVMNjgwLTgwIDQ2NS0yOTUgMjkwLTEyMFptLTkwLTgwaDU2bDM5Mi0zOTEtNTctNTctMzkxIDM5MnY1NlptNDIwLTQxOS0yOS0yOSA1NyA1Ny0yOC0yOFoiIGZpbGw9IiNmZmZmZmYiLz48L3N2Zz4%3D>
[img-shaders]: <https://img.shields.io/badge/Shaders-4361EE?style=for-the-badge&logo=opengl&logoColor=white>

[img-github]: <https://img.shields.io/github/stars/reysokree/eversmooth-optimized?style=for-the-badge&label=Stars&color=white&logoColor=white&labelColor=black&logo=github>
[img-installation]: <https://img.shields.io/badge/Installation_Guide-303030?style=for-the-badge&logo=readthedocs&logoColor=white>

[img-maintainer]: <https://img.shields.io/badge/Maintained%20by-ReysoKree-7B2CBF?style=flat-square>
[img-minecraft]: <https://img.shields.io/badge/Minecraft-1.16.5-3C8527?style=flat-square&logo=minecraft&logoColor=white>
[img-loader]: <https://img.shields.io/badge/Loader-Fabric-DBB58F?style=flat-square>
