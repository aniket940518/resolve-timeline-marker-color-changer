# DaVinci Resolve Timeline Marker Color Changer

A small, focused Python utility for DaVinci Resolve 21 that changes multiple
timeline markers from one color to another using a clean floating panel.

If you use marker colors to organize edits, revisions, selects, review notes,
or delivery tasks, this script saves you from manually changing markers one by
one.

## What It Does

The script opens a floating panel inside DaVinci Resolve where you can:

1. Choose the marker color you want to modify.
2. Choose the new color those markers should become.
3. Apply the change to all matching markers on the current timeline.

It preserves each marker's:

- Timeline frame position
- Name
- Note
- Duration
- Custom script data

## Why This Exists

DaVinci Resolve's scripting API does not currently provide a direct
`SetMarkerColor()` function for timeline markers. This script works around that
limitation carefully by reading matching markers, deleting them, and recreating
them at the same frame with the new color and original metadata.

In practice, it feels like batch color-changing markers from the timeline.

## Features

- Floating Resolve UI panel
- Works on the current active timeline
- Batch changes all markers of a selected color
- Counts matching markers before applying
- Keeps marker name, note, duration, frame position, and custom data
- Automatically refreshes marker counts
- Reopens cleanly if the panel is already running
- Uses only DaVinci Resolve's built-in Python scripting API

## Supported Marker Colors

The script supports the standard Resolve marker colors:

- Blue
- Cyan
- Green
- Yellow
- Red
- Pink
- Purple
- Fuchsia
- Rose
- Lavender
- Sky
- Mint
- Lemon
- Sand
- Cocoa
- Cream

## Requirements

- DaVinci Resolve 21
- Python scripting enabled in Resolve
- macOS, Windows, or Linux with Resolve scripting available

This script was created and tested with DaVinci Resolve 21 on macOS.

## Installation

Copy `change_timeline_marker_colors.py` into Resolve's Utility scripts folder.

### macOS

```text
~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility
```

### Windows

```text
%APPDATA%\Blackmagic Design\DaVinci Resolve\Fusion\Scripts\Utility
```

### Linux

```text
~/.local/share/DaVinciResolve/Fusion/Scripts/Utility
```

If the `Utility` folder does not exist, create it.

Restart DaVinci Resolve after copying the script.

## Usage

1. Open DaVinci Resolve.
2. Open a project and timeline with markers.
3. Go to:

```text
Workspace > Scripts > Utility > change_timeline_marker_colors
```

4. In the floating panel, choose the source marker color.
5. Choose the target marker color.
6. Click `Apply`.

The panel shows how many timeline markers match the selected source color before
you apply the change.

## Safety Notes

Because Resolve does not expose a direct marker color update function, the
script recreates matching markers. It attempts to preserve all marker fields
available through the public scripting API.

As with any timeline automation tool, it is a good idea to test on a duplicate
timeline first when using it in an important project.

## File

The main script is:

```text
change_timeline_marker_colors.py
```

## License

Choose any license you prefer before publishing. MIT is a simple option if you
want other editors and developers to freely use, modify, and share the script.

## Credits

Built for editors who use timeline markers as a real workflow system, not just
as little colored reminders.

