// SPDX-License-Identifier: MIT
// An active window always takes priority, even if it has an empty title.
function chooseTitle(hasWindow, windowTitle, playing, track, artist) {
    if (hasWindow) {
        return windowTitle || "";
    }
    if (!playing || !track) {
        return "";
    }
    return "♫ " + track + (artist ? " — " + artist : "");
}
