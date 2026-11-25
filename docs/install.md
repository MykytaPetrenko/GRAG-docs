# Installation

GRAG is a Blender extension for Blender 5.2 or newer.

## Install the extension

1. Download the GRAG ZIP and keep it zipped.
2. In Blender, open **Edit → Preferences → Get Extensions**.
3. Open the menu in the upper-right corner and choose **Install from Disk**.
4. Select the ZIP and confirm the installation.
5. If GRAG is disabled after installation, enable it in **Preferences → Add-ons**.

Open the sidebar with **N** in the 3D Viewport and select the **GRAG** tab. It holds three panels, **Door Generator**, **Window Generator** and **Stairs Generator**, closed until you open them.

[Blender Manual on installing extensions](https://docs.blender.org/manual/en/latest/editors/preferences/extensions.html#installing-extensions)

## Install the Godot add-on

1. Copy the `addons/grag` folder that comes with GRAG into the `addons` folder of your Godot project.
2. In Godot, enable **GRAG** in **Project → Project Settings → Plugins**.

See [Godot](godot.md) for how the add-on imports assets.

## Upgrading from the separate generators

GRAG replaces the separate GRAG Doors, GRAG Windows and GRAG Stairs extensions and the stair generator that used to be part of EasyGridAligner. Disable them before installing GRAG. Assets made by them are not supported.
