#!/usr/bin/env python3
"""
Change timeline marker colors in DaVinci Resolve 21.

Install location for menu use on macOS:
  ~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility

Resolve's marker API does not expose a direct "set color" call, so this script
preserves each matching marker's frame, name, note, duration, and customData,
then recreates it with the selected target color.
"""

from __future__ import annotations

import sys
from collections import Counter


SCRIPT_ID = "com.harpoon.resolve.ChangeTimelineMarkerColors"
WINDOW_TITLE = "Timeline Marker Color Changer"
PANEL_WIDTH = 540
PANEL_HEIGHT = 320
MIN_PANEL_WIDTH = 520
MIN_PANEL_HEIGHT = 300
BUTTON_SIZE = [112, 30]

MODULE_DIR = (
    "/Library/Application Support/Blackmagic Design/"
    "DaVinci Resolve/Developer/Scripting/Modules"
)

MARKER_COLORS = [
    "Blue",
    "Cyan",
    "Green",
    "Yellow",
    "Red",
    "Pink",
    "Purple",
    "Fuchsia",
    "Rose",
    "Lavender",
    "Sky",
    "Mint",
    "Lemon",
    "Sand",
    "Cocoa",
    "Cream",
]


def load_resolve():
    try:
        import DaVinciResolveScript as dvr_script
    except ImportError:
        if MODULE_DIR not in sys.path:
            sys.path.append(MODULE_DIR)
        import DaVinciResolveScript as dvr_script

    resolve_obj = globals().get("resolve") or dvr_script.scriptapp("Resolve")
    if not resolve_obj:
        raise RuntimeError("Could not connect to DaVinci Resolve.")

    return resolve_obj, dvr_script


def get_ui(resolve_obj, dvr_script):
    fusion_obj = globals().get("fusion") or resolve_obj.Fusion()
    if not fusion_obj:
        raise RuntimeError("Could not connect to Fusion UIManager.")

    ui_manager = getattr(fusion_obj, "UIManager", None)
    if not ui_manager:
        raise RuntimeError("Fusion UIManager is unavailable.")

    if callable(ui_manager) and not hasattr(ui_manager, "VGroup"):
        ui_manager = ui_manager()

    bmd_module = globals().get("bmd") or dvr_script
    dispatcher_factory = getattr(bmd_module, "UIDispatcher", None)
    if not dispatcher_factory:
        raise RuntimeError("Could not create Resolve UIDispatcher.")

    return fusion_obj, ui_manager, dispatcher_factory(ui_manager)


def current_timeline(resolve_obj):
    project_manager = resolve_obj.GetProjectManager()
    if not project_manager:
        return None, None

    project = project_manager.GetCurrentProject()
    if not project:
        return None, None

    return project, project.GetCurrentTimeline()


def normalize_frame(frame_id):
    return int(round(float(frame_id)))


def sorted_markers(markers):
    return sorted(markers.items(), key=lambda item: normalize_frame(item[0]))


def marker_color(marker):
    return str(marker.get("color") or "")


def count_marker_colors(markers):
    return Counter(marker_color(marker) for marker in markers.values())


def matching_markers(markers, source_color):
    return [
        (frame_id, marker)
        for frame_id, marker in sorted_markers(markers)
        if marker_color(marker) == source_color
    ]


def delete_marker(timeline, frame_id):
    candidates = [frame_id, normalize_frame(frame_id)]
    tried = set()
    for candidate in candidates:
        key = repr(candidate)
        if key in tried:
            continue
        tried.add(key)
        if timeline.DeleteMarkerAtFrame(candidate):
            return True
    return False


def add_marker(timeline, frame_id, color, marker):
    frame = normalize_frame(frame_id)
    name = str(marker.get("name") or "")
    note = str(marker.get("note") or "")
    duration = marker.get("duration", 1.0)
    custom_data = str(marker.get("customData") or "")
    return timeline.AddMarker(frame, color, name, note, duration, custom_data)


def change_marker_colors(timeline, source_color, target_color):
    markers = timeline.GetMarkers() or {}
    matches = matching_markers(markers, source_color)

    if source_color == target_color:
        return {
            "changed": 0,
            "matched": len(matches),
            "failed": [],
            "message": "Source and target colors are the same.",
        }

    changed = 0
    failed = []

    for frame_id, marker in matches:
        original_color = marker_color(marker)
        frame = normalize_frame(frame_id)

        if not delete_marker(timeline, frame_id):
            failed.append(f"Frame {frame}: could not delete original marker.")
            continue

        if add_marker(timeline, frame, target_color, marker):
            changed += 1
            continue

        if add_marker(timeline, frame, original_color, marker):
            failed.append(f"Frame {frame}: could not add new marker; original restored.")
        else:
            failed.append(f"Frame {frame}: could not add new marker or restore original.")

    return {
        "changed": changed,
        "matched": len(matches),
        "failed": failed,
        "message": "",
    }


def set_status(items, text):
    items["StatusLabel"].Text = text


def build_window(resolve_obj, ui, dispatcher):
    existing = ui.FindWindow(SCRIPT_ID)
    if existing:
        existing.Close()

    window = dispatcher.AddWindow(
        {
            "ID": SCRIPT_ID,
            "Geometry": [100, 100, PANEL_WIDTH, PANEL_HEIGHT],
            "MinimumSize": [MIN_PANEL_WIDTH, MIN_PANEL_HEIGHT],
            "WindowTitle": WINDOW_TITLE,
        },
        ui.VGroup(
            {"Spacing": 6, "Margin": 14},
            [
                ui.Label(
                    {
                        "ID": "HeaderLabel",
                        "Text": "Timeline Marker Color Changer",
                        "Font": ui.Font({"PixelSize": 18, "Bold": True}),
                        "Weight": 0,
                    }
                ),
                ui.Label({"ID": "TimelineLabel", "Text": "", "Weight": 0}),
                ui.HGroup(
                    {"Weight": 0, "Spacing": 8},
                    [
                        ui.Label({"Text": "Step 1: from color", "Weight": 0.32}),
                        ui.ComboBox({"ID": "SourceColor", "Weight": 0.68}),
                    ],
                ),
                ui.HGroup(
                    {"Weight": 0, "Spacing": 8},
                    [
                        ui.Label({"Text": "Step 2: to color", "Weight": 0.32}),
                        ui.ComboBox({"ID": "TargetColor", "Weight": 0.68}),
                    ],
                ),
                ui.Label({"ID": "CountLabel", "Text": "", "Weight": 0}),
                ui.Label({"ID": "StatusLabel", "Text": "", "WordWrap": True, "Weight": 0}),
                ui.HGroup(
                    {"Weight": 0, "Spacing": 8},
                    [
                        ui.Button(
                            {
                                "ID": "RefreshButton",
                                "Text": "Refresh",
                                "FixedSize": BUTTON_SIZE,
                                "Weight": 0,
                            }
                        ),
                        ui.Button(
                            {
                                "ID": "ApplyButton",
                                "Text": "Apply",
                                "FixedSize": BUTTON_SIZE,
                                "Weight": 0,
                            }
                        ),
                        ui.Button(
                            {
                                "ID": "CloseButton",
                                "Text": "Close",
                                "FixedSize": BUTTON_SIZE,
                                "Weight": 0,
                            }
                        ),
                        ui.HGap(0, 1),
                    ],
                ),
            ],
        ),
    )

    items = window.GetItems()
    items["SourceColor"].AddItems(MARKER_COLORS)
    items["TargetColor"].AddItems(MARKER_COLORS)
    items["TargetColor"].CurrentIndex = MARKER_COLORS.index("Red")

    state = {
        "project": None,
        "timeline": None,
        "markers": {},
        "counts": Counter(),
    }

    def selected_source():
        return str(items["SourceColor"].CurrentText or MARKER_COLORS[0])

    def selected_target():
        return str(items["TargetColor"].CurrentText or MARKER_COLORS[0])

    def update_count_label(ev=None):
        source = selected_source()
        target = selected_target()
        count = int(state["counts"].get(source, 0))
        total = len(state["markers"])

        if source == target:
            items["CountLabel"].Text = (
                f"{count} {source} marker(s) found. Pick a different target color."
            )
            items["ApplyButton"].Enabled = False
            return

        items["CountLabel"].Text = f"{count} / {total} marker(s): {source} -> {target}"
        items["ApplyButton"].Enabled = count > 0

    def refresh(ev=None):
        project, timeline = current_timeline(resolve_obj)
        state["project"] = project
        state["timeline"] = timeline

        if not project:
            state["markers"] = {}
            state["counts"] = Counter()
            items["TimelineLabel"].Text = "No project is open."
            set_status(items, "Open a project in DaVinci Resolve, then click Refresh.")
            update_count_label()
            return

        if not timeline:
            state["markers"] = {}
            state["counts"] = Counter()
            items["TimelineLabel"].Text = f"Project: {project.GetName()}"
            set_status(items, "No active timeline is open.")
            update_count_label()
            return

        markers = timeline.GetMarkers() or {}
        state["markers"] = markers
        state["counts"] = count_marker_colors(markers)

        timeline_name = timeline.GetName() if hasattr(timeline, "GetName") else "Current timeline"
        items["TimelineLabel"].Text = f"Timeline: {timeline_name}"
        set_status(items, "Ready.")
        update_count_label()

    def apply_change(ev):
        timeline = state["timeline"]
        source = selected_source()
        target = selected_target()

        if not timeline:
            refresh()
            timeline = state["timeline"]
            if not timeline:
                return

        result = change_marker_colors(timeline, source, target)
        refresh()

        changed = result["changed"]
        matched = result["matched"]
        failed = result["failed"]

        if result["message"]:
            set_status(items, result["message"])
        elif failed:
            set_status(
                items,
                f"Changed {changed} of {matched} marker(s). "
                + " ".join(failed[:3])
                + (" More failures occurred." if len(failed) > 3 else ""),
            )
        else:
            set_status(items, f"Changed {changed} marker(s): {source} -> {target}.")

    def close(ev):
        dispatcher.ExitLoop()

    window.On[SCRIPT_ID].Close = close
    window.On["CloseButton"].Clicked = close
    window.On["RefreshButton"].Clicked = refresh
    window.On["ApplyButton"].Clicked = apply_change
    window.On["SourceColor"].CurrentIndexChanged = update_count_label
    window.On["TargetColor"].CurrentIndexChanged = update_count_label

    refresh()
    return window


def main():
    try:
        resolve_obj, dvr_script = load_resolve()
        _fusion_obj, ui, dispatcher = get_ui(resolve_obj, dvr_script)
        window = build_window(resolve_obj, ui, dispatcher)
        window.Show()
        dispatcher.RunLoop()
    except Exception as exc:
        print(f"ERROR: {exc}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
