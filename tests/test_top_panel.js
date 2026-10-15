// Node: node tests/test_top_panel.js. Also runnable in an isolated V8 engine.
function runTopTests(layoutSource, titleSource) {
    var count = 0;
    function assert(value, message) { if (!value) { throw new Error(message); } }
    function test(name, fn) { fn(); count++; }
    function environment() {
        var next = 1;
        var state = { panels: [], fail: "", known: ["menu.11.next", "org.kde.plasma.icontasks",
            "org.endvos.paneltitle", "org.kde.plasma.systemtray", "org.kde.plasma.digitalclock"] };
        function item(type) {
            return {id: next++, type: type, currentConfigGroup: [], config: {},
                writeConfig: function (key, value) { this.config[this.currentConfigGroup.join("/") + "/" + key] = value; },
                readConfig: function (key, fallback) {
                    var value = this.config[this.currentConfigGroup.join("/") + "/" + key];
                    return value === undefined ? fallback : value;
                }};
        }
        state.Panel = function () {
            var panel = item("panel"); panel.screen = 7; panel.location = "bottom"; panel.children = [];
            panel.widgets = function () { return panel.children.slice(); };
            panel.addWidget = function (type) { if (state.fail === type) { return null; }
                var widget = item(type); panel.children.push(widget); return widget; };
            panel.remove = function () { state.panels.splice(state.panels.indexOf(panel), 1); };
            panel.reloadConfig = function () {};
            state.panels.push(panel); return panel;
        };
        state.apply = function (replace) {
            var output = [];
            new Function("applicationVersion", "knownWidgetTypes", "panels", "Panel", "print",
                "endvosReplacePanels", "endvosLaunchers", layoutSource)("6.7.5", state.known,
                function () { return state.panels.slice(); }, state.Panel,
                function (text) { output.push(text); }, replace, ["org.kde.dolphin.desktop"]);
            assert(output.join("").indexOf("ENDVOS_TOP_PANEL_OK") >= 0, "missing completion marker");
        };
        return state;
    }
    test("replace only top and bottom panels on the selected monitor", function () {
        var s = environment(); var bottom = new s.Panel(); var top = new s.Panel(); top.location = "top";
        var side = new s.Panel(); side.location = "left"; var other = new s.Panel(); other.screen = 12;
        s.apply(true);
        assert(s.panels.indexOf(bottom) < 0 && s.panels.indexOf(top) < 0, "old horizontal panels remain");
        assert(s.panels.indexOf(side) >= 0 && s.panels.indexOf(other) >= 0, "unrelated panels removed");
        var panel = s.panels[s.panels.length - 1];
        assert(panel.location === "top" && panel.height === 36, "wrong panel position/height");
        assert(panel.children.map(function (w) {return w.type;}).join() === s.known.join(), "wrong widget order");
        assert(panel.children[0].config["General/displayPosition"] === 0, "launcher not anchored to panel");
        assert(panel.children[0].config["General/showWeather"] === false, "weather enabled");
        assert(panel.children[4].config["Appearance/dateDisplayFormat"] === 1, "date setting in wrong group");
        panel.children[1].config["General/launchers"] = ["applications:custom.desktop"];
        panel.children[0].config["General/favoriteApps"] = ["custom.desktop"];
        s.apply(true);
        assert(s.panels.length === 3 && panel.children.length === 5, "repeat produced duplicates");
        assert(panel.children[1].config["General/launchers"][0] === "applications:custom.desktop", "pins reset");
        assert(panel.children[0].config["General/favoriteApps"][0] === "custom.desktop", "favorites reset");
    });
    test("missing widget changes nothing", function () {
        var s = environment(); s.known = []; var old = new s.Panel(); var failed = false;
        try { s.apply(true); } catch (e) { failed = true; }
        assert(failed && s.panels.length === 1 && s.panels[0] === old, "missing widget changed panels");
    });
    test("partial creation preserves old panels and resumes", function () {
        var s = environment(); var old = new s.Panel(); s.fail = "org.endvos.paneltitle"; var failed = false;
        try { s.apply(true); } catch (e) { failed = true; }
        assert(failed && s.panels.indexOf(old) >= 0, "old panel removed on failure");
        s.fail = ""; s.apply(true); assert(s.panels.length === 1 && s.panels[0].children.length === 5, "cannot resume");
    });
    test("direct execution preserves old panels", function () {
        var s = environment(); var old = new s.Panel(); s.apply(false);
        assert(s.panels.indexOf(old) >= 0, "direct execution removed panel");
    });
    test("customized profile panel refused without layout changes", function () {
        var s = environment(); s.apply(true); var panel = s.panels[0]; panel.addWidget("custom.widget");
        panel.location = "bottom"; var failed = false;
        try { s.apply(true); } catch (e) { failed = true; }
        assert(failed && panel.location === "bottom" && panel.children.length === 6, "customized panel changed");
    });
    var choose = new Function(titleSource + "\nreturn chooseTitle;")();
    test("active window has priority over music", function () {
        assert(choose(true, "Dolphin", true, "Song", "Artist") === "Dolphin", "music overrides window");
        assert(choose(true, "", true, "Song", "Artist") === "", "empty active window treated as absent");
    });
    test("music only without window and while playing", function () {
        assert(choose(false, "old window", true, "Song", "Artist") === "♫ Song — Artist", "wrong fallback");
        assert(choose(false, "", false, "Song", "Artist") === "", "paused player displayed");
        assert(choose(false, "", true, "", "Artist") === "", "empty track displayed");
        assert(choose(false, "", true, "Song", "") === "♫ Song", "empty artist displayed");
    });
    return count + " top-panel/title behavior tests passed";
}
if (typeof module !== "undefined" && require.main === module) {
    var fs = require("fs"); var path = require("path"); var root = path.join(__dirname, "../desktop/kde/endvos-dark");
    console.log(runTopTests(fs.readFileSync(path.join(root, "layout.js"), "utf8"),
        fs.readFileSync(path.join(root, "widgets/org.endvos.paneltitle/contents/ui/Title.js"), "utf8")));
}
