// Endvos stage 1. Replacement is enabled only by the backed-up installer.
(function () {
    var profile = "endvos-dark-top-v1";
    var slots = [
        ["start", "menu.11.next"],
        ["tasks", "org.kde.plasma.icontasks"],
        ["title", "org.endvos.paneltitle"],
        ["tray", "org.kde.plasma.systemtray"],
        ["clock", "org.kde.plasma.digitalclock"]
    ];
    if (!/^6\.7\./.test(applicationVersion)) {
        throw new Error("Endvos currently targets Plasma 6.7.x.");
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
    var owned = panels().filter(function (panel) { return marker(panel, "Profile") === profile; });
    if (owned.length > 1) {
        throw new Error("Multiple Endvos top panels found. Review them before reapplying.");
    }
    var panel = owned.length ? owned[0] : null;
    var widgets = {};
    if (panel) {
        panel.widgets().forEach(function (widget) {
            var role = marker(widget, "Role");
            var slot = slots.filter(function (entry) { return entry[0] === role; })[0];
            if (!slot || slot[1] !== widget.type || widgets[role]) {
                throw new Error("Endvos top panel was customized; no layout was changed.");
            }
            widgets[role] = widget;
        });
    } else {
        panel = new Panel;
        panel.currentConfigGroup = ["Endvos"];
        panel.writeConfig("Profile", profile);
    }
    var previousPanels = [];
    if (typeof endvosReplacePanels !== "undefined" && endvosReplacePanels) {
        previousPanels = panels().filter(function (candidate) {
            return candidate.id !== panel.id && candidate.screen === panel.screen &&
                (candidate.location === "bottom" || candidate.location === "top");
        });
    }
    panel.location = "top";
    panel.lengthMode = "fill";
    panel.alignment = "center";
    panel.height = 36;
    panel.hiding = "none";
    panel.floating = false;
    panel.offset = 0;
    slots.forEach(function (slot, index) {
        var fresh = !widgets[slot[0]];
        var widget = widgets[slot[0]] || panel.addWidget(slot[1]);
        if (!widget || widget.type !== slot[1]) {
            throw new Error("Could not create " + slot[1] + ". Original panels were retained.");
        }
        widget.currentConfigGroup = ["Endvos"];
        widget.writeConfig("Role", slot[0]);
        widgets[slot[0]] = widget;
        widget.index = index;
        widget.currentConfigGroup = ["General"];
        if (slot[0] === "start") {
            widget.writeConfig("displayPosition", 0); // Follow the top panel, not bottom/center.
            widget.writeConfig("showAtCenter", false);
            widget.writeConfig("showWeather", false);
            widget.writeConfig("showRecentDocs", false);
            widget.writeConfig("showRecentApps", false);
            widget.writeConfig("allAppsViewMode", 0);
            widget.writeConfig("numberColumns", 3);
            widget.writeConfig("numberRows", 2);
            if (fresh && typeof endvosLaunchers !== "undefined" && endvosLaunchers.length) {
                widget.writeConfig("favoriteApps", endvosLaunchers);
            }
        } else if (slot[0] === "tasks") {
            widget.writeConfig("fill", false);
            if (fresh && typeof endvosLaunchers !== "undefined" && endvosLaunchers.length) {
                widget.writeConfig("launchers", endvosLaunchers.map(function (name) {
                    return "applications:" + name;
                }));
            }
        } else if (slot[0] === "clock") {
            widget.currentConfigGroup = ["Appearance"];
            widget.writeConfig("showDate", true);
            widget.writeConfig("dateDisplayFormat", 1); // Date beside time.
        }
        widget.currentConfigGroup = [];
    });
    panel.currentConfigGroup = [];
    panel.reloadConfig();
    previousPanels.forEach(function (candidate) { candidate.remove(); });
    widgets.start.globalShortcut = "Alt+F1";
    print("ENDVOS_TOP_PANEL_OK: " + panel.id);
}());
