// Run with Node, or pass layoutSource to runTests in an isolated JS engine.
function runTests(layoutSource) {
    function assert(condition, message) {
        if (!condition) { throw new Error(message); }
    }
    var required = ["org.kde.plasma.panelspacer", "menu.11.next", "org.kde.plasma.icontasks",
        "org.kde.plasma.systemtray", "org.kde.plasma.digitalclock", "org.kde.plasma.showdesktop"];
    var count = 0;
    function environment() {
        var nextId = 1;
        var state = { panels: [], known: required.slice(), createdWidgets: 0, failWidget: "" };
        function applet(type) {
            return {
                id: nextId++, type: type, currentConfigGroup: [], config: {},
                writeConfig: function (key, value) { this.config[this.currentConfigGroup.join("/") + "/" + key] = value; },
                readConfig: function (key, fallback) {
                    var value = this.config[this.currentConfigGroup.join("/") + "/" + key];
                    return typeof value === "undefined" ? fallback : value;
                }
            };
        }
        state.Panel = function () {
            var panel = applet("org.kde.panel");
            panel.screen = 4; // Simulate runtime monitor assignment, not screen zero.
            panel.location = "bottom";
            panel.children = [];
            panel.widgets = function () { return panel.children.slice(); };
            panel.addWidget = function (type) {
                if (state.failWidget === type) { return null; }
                var widget = applet(type);
                panel.children.push(widget);
                state.createdWidgets++;
                return widget;
            };
            panel.remove = function () { state.panels.splice(state.panels.indexOf(panel), 1); };
            panel.reloadConfig = function () {};
            state.panels.push(panel);
            return panel;
        };
        state.execute = function (replace) {
            var output = [];
            new Function("applicationVersion", "knownWidgetTypes", "panels", "Panel", "print",
                "endvosReplaceBottomPanels", layoutSource)("6.7.5", state.known,
                function () { return state.panels.slice(); }, state.Panel,
                function (message) { output.push(message); }, replace);
            assert(output.join("\n").indexOf("ENDVOS_PANEL_OK") >= 0, "missing success marker");
        };
        return state;
    }
    function test(name, callback) {
        callback();
        count++;
    }
    test("replacement preserves top panels and other monitors; repeated apply is stable", function () {
        var state = environment();
        var old = new state.Panel();
        var top = new state.Panel(); top.location = "top";
        var other = new state.Panel(); other.screen = 9;
        state.execute(true);
        assert(state.panels.indexOf(old) < 0, "old bottom panel remains");
        assert(state.panels.indexOf(top) >= 0 && state.panels.indexOf(other) >= 0, "unrelated panel removed");
        var created = state.createdWidgets;
        state.execute(true);
        assert(state.panels.length === 3 && state.createdWidgets === created, "reapply creates duplicates");
    });
    test("direct use retains the original panel", function () {
        var state = environment();
        var old = new state.Panel();
        state.execute(false);
        assert(state.panels.indexOf(old) >= 0, "preview removed original panel");
    });
    test("missing dependency prevents all writes", function () {
        var state = environment();
        state.known = [];
        var failed = false;
        try { state.execute(true); } catch (error) { failed = true; }
        assert(failed && state.panels.length === 0, "missing widgets changed the layout");
    });
    test("partial creation never removes the recovery panel", function () {
        var state = environment();
        var old = new state.Panel();
        state.failWidget = "org.kde.plasma.digitalclock";
        var failed = false;
        try { state.execute(true); } catch (error) { failed = true; }
        assert(failed && state.panels.indexOf(old) >= 0, "failed apply removed original panel");
        state.failWidget = "";
        state.execute(true);
        assert(state.panels.length === 1 && state.createdWidgets === 7, "partial apply cannot resume");
    });
    test("customized owned panel is protected", function () {
        var state = environment();
        state.execute(true);
        state.panels[0].addWidget("custom.widget");
        var created = state.createdWidgets;
        var failed = false;
        try { state.execute(true); } catch (error) { failed = true; }
        assert(failed && state.createdWidgets === created && state.panels.length === 1,
            "customized panel was changed");
    });
    return count + " panel behavior tests passed";
}

if (typeof module !== "undefined" && require.main === module) {
    var fs = require("fs");
    var path = require("path");
    console.log(runTests(fs.readFileSync(path.join(__dirname,
        "../desktop/kde/windows11-dark/layout.js"), "utf8")));
}
