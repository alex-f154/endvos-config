// The installer backs up the desktop before explicitly enabling replacement.
// Direct execution retains existing panels unless replacement is requested.
(function () {
    var profile = "endvos-windows11-dark-v1";
    var slots = [
        ["left-space", "org.kde.plasma.panelspacer"],
        ["start", "menu.11.next"],
        ["tasks", "org.kde.plasma.icontasks"],
        ["right-space", "org.kde.plasma.panelspacer"],
        ["tray", "org.kde.plasma.systemtray"],
        ["clock", "org.kde.plasma.digitalclock"],
        ["desktop", "org.kde.plasma.showdesktop"]
    ];

    if (!/^6\.7\./.test(applicationVersion)) {
        throw new Error("This profile targets Plasma 6.7; check compatibility first.");
    }
    slots.forEach(function (slot) {
        if (knownWidgetTypes.indexOf(slot[1]) < 0) {
            throw new Error("Missing widget: " + slot[1] + ". No panel was changed.");
        }
    });

    function marker(applet, key) {
        var previous = applet.currentConfigGroup;
        applet.currentConfigGroup = ["Endvos"];
        var value = applet.readConfig(key, "");
        applet.currentConfigGroup = previous;
        return value;
    }

    var owned = panels().filter(function (candidate) {
        return marker(candidate, "Profile") === profile;
    });
    if (owned.length > 1) {
        throw new Error("Multiple Endvos panels found; resolve them manually first.");
    }

    var panel = owned.length ? owned[0] : null;
    var previousBottomPanels = [];
    var widgets = {};
    if (panel) {
        // Refuse to rearrange user-added or mismatched widgets.
        panel.widgets().forEach(function (widget) {
            var role = marker(widget, "Role");
            var slot = slots.filter(function (entry) { return entry[0] === role; })[0];
            if (!slot || slot[1] !== widget.type || widgets[role]) {
                throw new Error("Endvos panel was customized; review it before reapplying.");
            }
            widgets[role] = widget;
        });
    } else {
        panel = new Panel;
        panel.currentConfigGroup = ["Endvos"];
        panel.writeConfig("Profile", profile);
    }

    panel.location = "bottom";
    panel.lengthMode = "fill";
    panel.alignment = "center";
    panel.height = 48;
    panel.hiding = "none";
    panel.floating = false;
    panel.offset = 0;
    if (typeof endvosReplaceBottomPanels !== "undefined" && endvosReplaceBottomPanels) {
        previousBottomPanels = panels().filter(function (candidate) {
            return candidate.id !== panel.id && candidate.screen === panel.screen &&
                candidate.location === "bottom";
        });
    }

    slots.forEach(function (slot, index) {
        var widget = widgets[slot[0]] || panel.addWidget(slot[1]);
        if (!widget || widget.type !== slot[1]) {
            throw new Error("Could not create " + slot[1] + "; review the partial panel.");
        }
        widget.currentConfigGroup = ["Endvos"];
        widget.writeConfig("Role", slot[0]);
        widgets[slot[0]] = widget;
        widget.index = index;
        if (slot[0] === "start") {
            widget.currentConfigGroup = ["General"];
            widget.writeConfig("showAtCenter", true);
            widget.writeConfig("showWeather", false);
        }
        if (slot[0] === "tasks") {
            widget.currentConfigGroup = ["General"];
            widget.writeConfig("fill", false);
        }
        widget.currentConfigGroup = [];
    });
    panel.currentConfigGroup = [];
    panel.reloadConfig();
    // Keep the original panels until every replacement widget exists.
    previousBottomPanels.forEach(function (candidate) { candidate.remove(); });
    widgets.start.globalShortcut = "Alt+F1";
    print("ENDVOS_PANEL_OK: " + panel.id);
}());
